from unittest import TestCase

import responses

from service import constants, models


class ProfileTestCase(TestCase):
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
        self.assertEqual(profile.repo_topics, set())


class GithubProfileTestCase(TestCase):
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
            'https://api.github.com/users/user1/repos?per_page=25',
            json=[repo1, repo2, repo3]
        )
        responses.add(
            responses.HEAD,
            'https://api.github.com/users/user1/starred?per_page=25',
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
        self.assertCountEqual(profile.repo_topics, ['flask', 'api', 'testing', 'bugs'])


class BitbucketProfileTestCase(TestCase):
    def test_properties(self):
        profile = models.BitbucketProfile('user1', page_len=25)
        profile.user_profile = {
            'links': {
                'repositories': {'href':  '/2.0/repositories/user1'},
                'followers': {'href': '/2.0/users/user1/followers'},
            }
        }

        self.assertEqual(
            profile.headers,
            {'content-type': 'application/json'}
        )
        self.assertEqual(profile.pagination_str, '?pagelen={page_len}')
        self.assertEqual(profile.profile_url, constants.BITBUCKET_PROFILE_URL)
        self.assertEqual(profile.teams_url, constants.BITBUCKET_TEAMS_URL)
        self.assertEqual(profile.repos_url, '/2.0/repositories/user1')
        self.assertEqual(profile.followers_url, '/2.0/users/user1/followers')

    @responses.activate
    def test_get_user_profile(self):
        responses.add(
            responses.GET,
            constants.BITBUCKET_PROFILE_URL.format(username='user1'),
            json={'profile': 'data'},
            status=200
        )

        profile = models.BitbucketProfile('user1', page_len=25)
        profile.get_user_profile()

        self.assertEqual(profile.user_profile, {'profile': 'data'})

    @responses.activate
    def test_get_team_profile(self):
        responses.add(
            responses.GET,
            constants.BITBUCKET_PROFILE_URL.format(username='user1'),
            json={'type': 'error', 'error': {'message': 'user1 is a team account'}},
            status=200
        )
        responses.add(
            responses.GET,
            constants.BITBUCKET_TEAMS_URL.format(username='user1'),
            json={'profile': 'data'},
            status=200
        )

        profile = models.BitbucketProfile('user1', page_len=25)
        profile.get_user_profile()

        self.assertEqual(profile.user_profile, {'profile': 'data'})

    @responses.activate
    def test_get_paginated_count(self):
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1?pagelen=0',
            status=200,
            json={'pagelen': 0, 'size': 30, 'values': [], 'page': 1},
        )

        profile = models.BitbucketProfile('user1', page_len=25)
        count = profile.get_paginated_count('https://api.bitbucket.org/2.0/repositories/user1')

        self.assertEqual(count, 30)

    @responses.activate
    def test_get_paginated_list(self):
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1?pagelen=1',
            status=200,
            json={
                'pagelen': 0,
                'size': 30,
                'values': ['repo1', 'repo2'],
                'page': 1,
                'next': 'https://api.bitbucket.org/2.0/repositories/user1?pagelen=1&page=2'
            },
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1?pagelen=1&page=2',
            status=200,
            json={
                'pagelen': 0,
                'size': 30,
                'values': ['repo3', 'repo4'],
                'page': 1,
            },
        )

        profile = models.BitbucketProfile('user1', page_len=2)
        repos = profile.get_paginated_list('https://api.bitbucket.org/2.0/repositories/user1')

        self.assertEqual(repos, ['repo1', 'repo2', 'repo3', 'repo4'])

    @responses.activate
    def test_get_all_data(self):
        user_profile = {
            'links': {
                'repositories': {'href': 'https://api.bitbucket.org/2.0/repositories/user1'},
                'followers': {'href': 'https://api.bitbucket.org/2.0/users/user1/followers'},
            }
        }
        repo1 = {
            'name': 'repo1',
            'size': 1234,
            'language': 'Python',
            'links': {
                'watchers': {'href': 'https://api.bitbucket.org/2.0/repositories/user1/repo1/watchers'},
                'issues': {'href': 'https://api.bitbucket.org/2.0/repositories/user1/repo1/issues'},
            }
        }
        repo2 = {
            'name': 'repo2',
            'size': 1234,
            'language': 'Python',
            'links': {
                'watchers': {'href': 'https://api.bitbucket.org/2.0/repositories/user1/repo2/watchers'},
                'issues': {'href': 'https://api.bitbucket.org/2.0/repositories/user1/repo2/issues'},
            }
        }
        repo3 = {
            'name': 'repo3',
            'size': 123456,
            'language': 'Java',
            'links': {
                'watchers': {'href': 'https://api.bitbucket.org/2.0/repositories/user1/repo3/watchers'},
                'issues': {'href': 'https://api.bitbucket.org/2.0/repositories/user1/repo3/issues'},
            }
        }

        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/users/user1',
            json=user_profile
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1?pagelen=25',
            json={'pagelen': 25, 'size': 3, 'values': [repo1, repo2, repo3], 'page': 1}
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/users/user1/followers?pagelen=0',
            json={'pagelen': 0, 'size': 1234, 'values': [], 'page': 1},
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1/repo1/watchers?pagelen=0',
            json={'pagelen': 0, 'size': 10, 'values': [], 'page': 1},
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1/repo2/watchers?pagelen=0',
            json={'pagelen': 0, 'size': 10, 'values': [], 'page': 1},
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1/repo3/watchers?pagelen=0',
            json={'pagelen': 0, 'size': 1, 'values': [], 'page': 1},
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1/repo1/issues?pagelen=0',
            json={'pagelen': 0, 'size': 3, 'values': [], 'page': 1},
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1/repo2/issues?pagelen=0',
            json={'pagelen': 0, 'size': 3, 'values': [], 'page': 1},
        )
        responses.add(
            responses.GET,
            'https://api.bitbucket.org/2.0/repositories/user1/repo3/issues?pagelen=0',
            json={'pagelen': 0, 'size': 300, 'values': [], 'page': 1},
        )

        profile = models.BitbucketProfile('user1', page_len=25)
        profile.get_all_data()

        self.assertCountEqual(profile.repos, [repo1, repo2, repo3])
        self.assertEqual(profile.total_repo_count, 3)
        self.assertEqual(profile.total_watcher_count, 21)
        self.assertEqual(profile.total_follower_count, 1234)
        self.assertEqual(profile.total_stars_received_count, 0)
        self.assertEqual(profile.total_stars_given_count, 0)
        self.assertEqual(profile.total_open_issues_count, 306)
        self.assertEqual(profile.total_size, 125924)
        self.assertCountEqual(profile.languages_used, ['Python', 'Java'])
        self.assertCountEqual(profile.repo_topics, [])


class ConsolidatedProfileTestCase(TestCase):
    def test_dict(self):
        github_profile = models.GithubProfile('user1')
        github_profile.total_repo_count = 2
        github_profile.total_watcher_count = 2
        github_profile.total_follower_count = 3
        github_profile.total_stars_received_count = 4
        github_profile.total_stars_given_count = 5
        github_profile.total_open_issues_count = 7
        github_profile.total_size = 1000
        github_profile.languages_used = {'Python', 'C++'}
        github_profile.repo_topics = {'python', 'flask'}

        bitbucket_profile = models.BitbucketProfile('user2')
        bitbucket_profile.total_repo_count = 2
        bitbucket_profile.total_watcher_count = 2
        bitbucket_profile.total_follower_count = 3
        bitbucket_profile.total_stars_received_count = 0
        bitbucket_profile.total_stars_given_count = 0
        bitbucket_profile.total_open_issues_count = 7
        bitbucket_profile.total_size = 1000
        bitbucket_profile.languages_used = {'Python', 'Java'}
        bitbucket_profile.repo_topics = set()

        profile = models.ConsolidatedProfile(github_profile, bitbucket_profile)

        self.assertEqual(profile.github_profile.username, 'user1')
        self.assertEqual(profile.bitbucket_profile.username, 'user2')

        profile_dict = profile.dict

        self.assertEqual(profile_dict['total_repo_count'], 4)
        self.assertEqual(profile_dict['total_watcher_count'], 4)
        self.assertEqual(profile_dict['total_follower_count'], 6)
        self.assertEqual(profile_dict['total_stars_received_count'], 4)
        self.assertEqual(profile_dict['total_stars_given_count'], 5)
        self.assertEqual(profile_dict['total_open_issues_count'], 14)
        self.assertEqual(profile_dict['total_size'], 2000)
        self.assertCountEqual(profile_dict['languages_used'], ['Python', 'C++', 'Java'])
        self.assertEqual(profile_dict['languages_used_count'], 3)
        self.assertCountEqual(profile_dict['repo_topics'], ['python', 'flask'])
        self.assertEqual(profile_dict['repo_topics_count'], 2)
