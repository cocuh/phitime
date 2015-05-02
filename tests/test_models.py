from . import BaseTestCase


class BaseModelTestCase(BaseTestCase):
    pass


class ModelUserTests(BaseModelTestCase):
    def test_it(self):
        from phitime.models import User

        user = User.create('rarara')
        user.set_password('password')
        self.assertTrue(user.verify_password('password'))
        self.assertFalse(user.verify_password('wrong'))