from unittest import TestCase

from service import app
from service.routes import get_user_profile


class GetUserProfileTestCase(TestCase):
    def test_get_user_profile(self):
        with app.test_request_context():
            response = get_user_profile()

        self.assertEqual(response, '{}')
