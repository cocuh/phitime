from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    SmallInteger,
    Text,
    String,
    Unicode,
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

    sponsor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sponsor = relationship(User)


class Member(Base):
    __tablename__ = 'members'
    query = DBSession.query_property()
    id = Column(Integer, primary_key=True)

    name = Column(Unicode, nullable=False)

    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)
    event = relationship(Event)


class _PeriodTime(object):
    date = Column(Date, nullable=False)

    _start_hour = Column(SmallInteger)
    _start_minute = Column(SmallInteger)
    _end_hour = Column(SmallInteger)
    _end_minute = Column(SmallInteger)

    def set_date(self, date):
        """
        :type date: datetime.date 
        :return:
        """
        self.date = date

    def set_times(self, start_hour, start_minute, end_hour, end_minute):
        self._validate_times(start_hour, start_minute)
        self._validate_times(end_hour, end_minute)

        self._start_hour = start_hour
        self._start_minute = start_minute
        self._end_hour = end_hour
        self._end_minute = end_minute

    @staticmethod
    def _validate_times(hour, minute):
        """
        validate hour and minute in range 00:00-24:00
        
        :param hour: 00-24
        :type hour: int
        :param minute: 00-59
        :type minute: int
        :return:
        """
        if not (0 <= minute < 60):
            raise ValidationException('minutes should be 0 <= MM < 60')
        if not (0 <= hour <= 24):
            raise ValidationException('minutes should be 0 <= HH <= 24')
        if hour == 24 and minute != 0:
            raise ValidationException('hour=24 only accepted 24:00; minute should be 0')


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
