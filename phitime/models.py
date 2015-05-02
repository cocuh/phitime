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
from phitime.timetable import TimetableType


class User(Base):
    __tablename__ = 'users'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    identifier = Column(Text, unique=True, nullable=False)

    _password = Column(String(511), nullable=True, default=None)
    twitter_id = Column(BigInteger, unique=True, nullable=True, default=None)

    _password_ctx = CryptContext(["sha256_crypt"])

    def __init__(self, name):
        self.identifier = name

    @classmethod
    def create(cls, name):
        # TODO validate name
        return cls(name)

    def set_password(self, password):
        self._password = self._password_ctx.encrypt(password)

    def verify_password(self, password):
        self._password_ctx.verify(password, self.password)


class Event(Base):
    __tablename__ = 'events'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    name = Column(Unicode, nullable=False)
    description = Column(UnicodeText, nullable=False)

    sponsor_id = Column(Integer, ForeignKey('users.id'))
    sponsor = relationship(User)

    _timetable_type = Column(String, nullable=False)

    def __init__(self, name, description, timetable_type):
        self.name = name
        self.description = description
        self._timetable_type = timetable_type

    @property
    def timetable_type(self):
        return TimetableType.find_by_name(self._timetable_type)

    @property
    def scrambled_id(self):
        """
        :rtype: int
        """
        return scramble(self.id)

    @classmethod
    def create(cls, name, description, timetable_type):
        if name is None:  # TODO validate length
            raise ValidationException('event.name is None')
        if description is None:  # TODO Validate length
            raise ValidationException('event.description is None')
        if not TimetableType.is_exist(timetable_type):
            raise ValidationException('event.timetable_type is not exist: timetable_type:{!r}'.format(timetable_type))
        return cls(name, description, timetable_type)

    @classmethod
    def find_by_scrambled_id(cls, scrambled_id):
        id = unscramble(scrambled_id)
        return cls.query.filter(cls.id == id).first()


class Member(Base):
    __tablename__ = 'members'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    name = Column(Unicode, nullable=False)

    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    event = relationship(Event)


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
        self._start_minutes = start_minutes
        self._period_length = period_length

    @staticmethod
    def _validate_times(start_minutes, period_length):
        """
        validate hour and minute in range 00:00-24:00
        
        :param hour: 00-24
        :type hour: int
        :param minute: 00-59
        :type minute: int
        :return:
        """
        if not (0 <= start_minutes <= 24 * 60):
            raise ValidationException('minutes should be 0 <= minutes <= 24*60')
        if not (0 < period_length ):
            raise ValidationException('length should be 0 < length')
        if not (start_minutes + period_length <= 24 * 60):
            raise ValidationException('length should be start_minutes+period_length <= 24*60')


class ProposedTime(_PeriodTime, Base):
    __tablename__ = 'proposed_times'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    event_id = Column(Integer, ForeignKey('events.id'))
    event = relationship(Event)


class AvailableTime(_PeriodTime, Base):
    __tablename__ = 'available_times'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    member_id = Column(Integer, ForeignKey('members.id'))
    member = relationship(Member)
