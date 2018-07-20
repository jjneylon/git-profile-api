from unittest import mock, TestCase

import responses

from service import constants, models


class GithubProfileTestCase(TestCase):
    def test_init(self):
        profile = models.GithubProfile('user1', page_len=25)

        self.assertEqual(profile.username, 'user1')
        self.assertEqual(profile.page_len, 25)
        self.assertEqual(profile.user_profile, {})
        self.assertEqual(profile.repos, [])

        self.assertEqual(profile.total_repo_count, 0)
        self.assertEqual(profile.total_watcher_count, 0)
        self.assertEqual(profile.total_follower_count, 0)
        self.assertEqual(profile.total_stars_received_count, 0)
        self.assertEqual(profile.total_stars_given_count, 0)
        self.assertEqual(profile.total_open_issues_count, 0)
        self.assertEqual(profile.total_size, 0)
        self.assertEqual(profile.languages_used, set())
        self.assertEqual(profile.languages_used_count, 0)
        self.assertEqual(profile.repo_topics, set())
        self.assertEqual(profile.repo_topics_count, 0)

    def test_properties(self):
        profile = models.GithubProfile('user1', page_len=25)
        profile.user_profile = {
            'repos_url': '/users/user1/repos',
            'starred_url': '/users/user1/starred{/owner}{/repo}',
        }

        self.assertEqual(
            profile.headers,
            {'content-type': 'application/json', 'accept': 'application/vnd.github.mercy-preview+json'}
        )
        self.assertEqual(profile.pagination_str, '?per_page={page_len}')
        self.assertEqual(profile.profile_url, constants.GITHUB_PROFILE_URL)
        self.assertEqual(profile.repos_url, '/users/user1/repos')
        self.assertEqual(profile.stars_received_url, '/users/user1/starred')

    @responses.activate
    def test_get_user_profile(self):
        responses.add(
            responses.GET,
            constants.GITHUB_PROFILE_URL.format(username='user1'),
            json={'profile': 'data'},
            status=200
        )

        profile = models.GithubProfile('user1', page_len=25)
        profile.get_user_profile()

        self.assertEqual(profile.user_profile, {'profile': 'data'})

    @responses.activate
    def test_get_paginated_count(self):
        responses.add(
            responses.HEAD,
            'https://api.github.com/users/user1/repos?per_page=1',
            status=200,
            headers={'link': '<https://api.github.com/users/user1/repos?page=92>; rel="last"'}
        )

        profile = models.GithubProfile('user1', page_len=25)
        count = profile.get_paginated_count('https://api.github.com/users/user1/repos')

        self.assertEqual(count, 92)

    @responses.activate
    def test_get_paginated_list(self):
        responses.add(
            responses.GET,
            'https://api.github.com/users/user1/repos?per_page=2',
            status=200,
            json=['repo1', 'repo2'],
            headers={'link': '<https://api.github.com/users/user1/repos?per_page=2&page=2>; rel="next"'}
        )
        responses.add(
            responses.GET,
            'https://api.github.com/users/user1/repos?per_page=2&page=2',
            status=200,
            json=['repo3', 'repo4'],
        )

        profile = models.GithubProfile('user1', page_len=2)
        repos = profile.get_paginated_list('https://api.github.com/users/user1/repos')

        self.assertEqual(repos, ['repo1', 'repo2', 'repo3', 'repo4'])

    @responses.activate
    def test_get_all_data(self):
        user_profile = {
            'repos_url': 'https://api.github.com/users/user1/repos',
            'starred_url': 'https://api.github.com/users/user1/starred{/owner}{/repo}',
            'followers': 1234,

        }
        repo1 = {
            'watchers_count': 10,
            'stargazers_count': 20,
            'open_issues_count': 3,
            'size': 1234,
            'language': 'Python',
            'topics': ['flask', 'api']
        }
        repo2 = {
            'watchers_count': 10,
            'stargazers_count': 20,
            'open_issues_count': 3,
            'size': 1234,
            'language': 'Python',
            'topics': ['flask', 'testing']
        }
        repo3 = {
            'watchers_count': 1,
            'stargazers_count': 2,
            'open_issues_count': 300,
            'size': 123456,
            'language': 'Java',
            'topics': ['bugs']
        }
        responses.add(
            responses.GET,
            'https://api.github.com/users/user1',
            json=user_profile
        )
        responses.add(
            responses.GET,
            'https://api.github.com/users/user1/repos?page_len=25',
            json=[repo1, repo2, repo3]
        )
        responses.add(
            responses.HEAD,
            'https://api.github.com/users/user1/starred?page_len=25; rel="last"',
            headers={'link': '<api.github.com/users/user1/repos?page=92>; rel="last"'}
        )

        profile = models.GithubProfile('user1', page_len=2)
        profile.get_all_data()

        self.assertCountEqual(profile.repos, [repo1, repo2, repo3])
        self.assertEqual(profile.total_repo_count, 3)
        self.assertEqual(profile.total_watcher_count, 21)
        self.assertEqual(profile.total_follower_count, 1234)
        self.assertEqual(profile.total_stars_received_count, 92)
        self.assertEqual(profile.total_stars_given_count, 42)
        self.assertEqual(profile.total_open_issues_count, 306)
        self.assertEqual(profile.total_size, 125924)
        self.assertCountEqual(profile.languages_used, ['Python', 'Java'])
        self.assertEqual(profile.languages_used_count, 2)
        self.assertCountEqual(profile.repo_topics, ['flask', 'api', 'testing', 'bugs'])
        self.assertEqual(profile.repo_topics_count, 4)
