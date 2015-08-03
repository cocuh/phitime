import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    Text,
    String,
    Unicode,
    UnicodeText,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import (
    relationship,
    backref,
)
from passlib.context import CryptContext

from phitime.exceptions import (
    ValidationException,
)

from phitime.db import (
    Base,
    DBSession,
)
from phitime.scrambler import scramble, unscramble
from phitime.timetable import TimetableUtils


class User(Base):
    __tablename__ = 'users'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    identifier = Column(Text, unique=True, nullable=False)

    _password = Column(String(511), nullable=True, default=None)
    twitter_id = Column(BigInteger, unique=True, nullable=True, default=None)

    _password_ctx = CryptContext(["sha512_crypt"])

    def __init__(self, name):
        self.identifier = name

    @classmethod
    def create(cls, name):
        """
        :type name: Unicode, str 
        :rtype: User
        """
        # TODO validate name
        return cls(name)

    def set_password(self, password):
        """
        :type password: str
        :rtype: None
        """
        self._password = self._password_ctx.encrypt(password)

    def verify_password(self, password):
        """
        :type password: str
        :rtype: bool
        """
        return self._password_ctx.verify(password, self._password)


class Event(Base):
    __tablename__ = 'events'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    name = Column(Unicode, nullable=False)
    description = Column(UnicodeText, nullable=False)

    sponsor_id = Column(Integer, ForeignKey('users.id'))
    sponsor = relationship(User)

    created_at = Column(Date, nullable=False, default=datetime.date.today)

    last_member_position = Column(Integer, nullable=False)

    _timetable_type = Column(String, nullable=False, default='')

    def __init__(self, name, description, timetable_type):
        self.name = name
        self.description = description
        self._timetable_type = timetable_type
        self.last_member_position = 0

    def __repr__(self):
        return '<Event name="{}">'.format(self.name)

    def __json__(self):
        return {
            'name': self.name,
            'description': self.description,

        }

    def _get_timetable_type(self):
        """
        :rtype: phitime.timetable.base.TimetableType
        """
        return TimetableUtils.find_by_name(self._timetable_type)

    def _set_timetable_type(self, timetable_type):
        self._timetable_type = timetable_type

    timetable_type = property(_get_timetable_type, _set_timetable_type)

    @property
    def scrambled_id(self):
        """
        :rtype: str
        """
        return scramble(self.id)

    @classmethod
    def create(cls, name, description, timetable_type):
        """
        :type name: Unicode, str
        :type description: Unicode, str
        :type timetable_type: str
        :rtype: Event
        """
        event = cls(name, description, timetable_type)
        return event

    @classmethod
    def find_by_scrambled_id(cls, scrambled_id):
        """
        :param scrambled_id: event scrambled id
        :type scrambled_id: str
        :rtype: Event
        """
        id = unscramble(scrambled_id)
        return cls.query.filter(cls.id == id).first()

    def validate(self):
        """validate the instance's attributes. raises ValidationException
        :rtype: None
        """
        if self.name is None:  # TODO validate length
            raise ValidationException('event.name is None')
        if self.description is None:  # TODO Validate length
            raise ValidationException('event.description is None')
        if not TimetableUtils.is_exist(self._timetable_type):
            raise ValidationException(
                'event.timetable_type is not exist: timetable_type:{!r}'.format(self.timetable_type))

    def create_member(self, name, comment, available_times):
        """
        :type name: Unicode, str
        :type comment: Unicode, str 
        :rtype: Member
        """
        self.last_member_position += 1
        member = Member(self, name, comment, self.last_member_position, available_times)
        member.validate()
        DBSession.add(self)
        DBSession.flush()
        return member


class Member(Base):
    __tablename__ = 'members'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    name = Column(Unicode, nullable=False)
    comment = Column(Unicode, nullable=False)
    position = Column(Integer, nullable=False)

    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    event = relationship(Event, backref=backref('members'))

    def __init__(self, event, name, comment, position, available_times):
        self.event = event
        self.name = name
        self.comment = comment
        self.position = position
        self.available_times = available_times

    def __repr__(self):
        return '<Member name="{}" position="{}">'.format(self.name, self.position)

    @classmethod
    def find(cls, event, position):
        """
        :type event: Event
        :type position: int
        :rtype: Member
        """
        return cls.query.filter(cls.event_id == event.id, cls.position == position)

    def validate(self):
        """validate the instance's attributes. raises ValidationException
        :rtype: None
        """
        if self.event is None:
            raise ValidationException('member.event is None')
        if self.name is None:  # TODO validate length
            raise ValidationException('member.name is None')
        if self.comment is None:  # TODO Validate length
            raise ValidationException('member.comment is None')

    def clear_available_times(self):
        for old_available_time in self.available_times:
            DBSession.delete(old_available_time)

    def append_available_time(self, date, start_minutes, period_length):
        return AvailableTime(self, date, start_minutes, period_length)

class _PeriodTime(object):
    date = Column(Date, nullable=False)

    _start_minutes = Column(Integer)
    _period_length = Column(Integer)

    def set_date(self, date):
        """
        :type date: datetime.date 
        :return:
        """
        self.date = date

    def set_times(self, start_minutes, period_length):
        """
        :param start_minutes: the number of minutes from the beginning of the day.
        :type start_minutes: int
        :param period_length: length (minutes)
        :type period_length: int
        :rtype: None
        """
        self._validate_times(start_minutes, period_length)
        self._start_minutes = start_minutes
        self._period_length = period_length

    def get_start_time(self):
        return self._start_minutes

    def get_end_time(self):
        return self._start_minutes + self._period_length

    @staticmethod
    def _validate_times(start_minutes, period_length):
        """
        validate hour and minute in range 00:00-24:00
        
        :param start_minutes: the number of minutes from the beginning of the day.
        :type start_minutes: int
        :param period_length: length (minutes)
        :type period_length: int
        :rtype: None
        """
        if not (0 <= start_minutes <= 24 * 60):
            raise ValidationException('minutes should be 0 <= minutes <= 24*60')
        if not (0 < period_length):
            raise ValidationException('length should be 0 < length')
        if not (start_minutes + period_length <= 24 * 60):
            raise ValidationException('length should be start_minutes+period_length <= 24*60')


class ProposedTime(_PeriodTime, Base):
    __tablename__ = 'proposed_times'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    event_id = Column(Integer, ForeignKey('events.id'))
    event = relationship(Event, backref=backref('proposed_times'))


class AvailableTime(_PeriodTime, Base):
    __tablename__ = 'available_times'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
    member = relationship(Member, backref=backref('available_times', cascade='delete'))

    def __init__(self, member, date, start_minutes, period_length):
        self.member = member
        self.set_date(date)
        self.set_times(start_minutes, period_length)
