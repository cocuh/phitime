import unittest

from pyramid import testing

from phitime.db import (
    Base,
    DBSession,
)


class BaseTestCase(unittest.TestCase):
    ECHO_SQL = False
    DEFAULT_SETTINGS = {
        'phitime.scramble_salt': 2204040131,
        'phitime.scramble_inverse_salt': 3264957675,
    }

    def _getTargetClass(self):
        raise NotImplementedError()

    def _makeOne(self):
        raise NotImplementedError()

    def _callFUT(self, *args, **kwargs):
        raise NotImplementedError()

    def setUp(self):
        self.config = testing.setUp(settings=self.DEFAULT_SETTINGS)
        self._setup_db()

    def tearDown(self):
        DBSession.remove()
        Base.metadata.drop_all(self.engine)

    def _setup_db(self):
        from sqlalchemy import create_engine
        import phitime.models  # to load models

        self.engine = create_engine('sqlite://', echo=self.ECHO_SQL)
        DBSession.configure(bind=self.engine)
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)

        self.DBSession = DBSession
    

