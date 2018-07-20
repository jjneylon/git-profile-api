from unittest import mock, TestCase

from service import handlers


class HandleGetProfileTestCase(TestCase):
    def test_handle_get_profile(self):
        inst = mock.Mock()
        inst.dict = {'profile': 'data'}
        with mock.patch.object(handlers.GithubProfile, 'get_all_data') as mock_github_get_data, \
                mock.patch.object(handlers.BitbucketProfile, 'get_all_data') as mock_bitbucket_get_data, \
                mock.patch.object(handlers, 'ConsolidatedProfile', return_value=inst) as mock_consolidated_profile:
            profile = handlers.handle_get_profile('user1', 'user2')

        mock_github_get_data.assert_any_call()
        mock_bitbucket_get_data.assert_any_call()
        github_profile, bitbucket_profile = mock_consolidated_profile.call_args[0]

        self.assertEqual(github_profile.username, 'user1')
        self.assertEqual(bitbucket_profile.username, 'user2')
        self.assertEqual(profile, {'profile': 'data'})
