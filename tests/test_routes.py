from unittest import mock, TestCase

from service import routes
from tests import RequestContext


class GetProfileTestCase(TestCase):
    @RequestContext('/api/profile?github=user1&bitbucket=user2')
    def test_get_profile(self):
        with mock.patch.object(routes, 'handle_get_profile', return_value={'profile': 'data'}) as mock_handler:
            response = routes.get_profile()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {'profile': 'data'})
        mock_handler.assert_called_once_with('user1', 'user2')

    @RequestContext('/api/profile?bitbucket=user2')
    def test_no_github_username(self):
        response = routes.get_profile()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "No github in request params"})

    @RequestContext('/api/profile?github=user1')
    def test_no_bitbucket_username(self):
        response = routes.get_profile()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "No bitbucket in request params"})
