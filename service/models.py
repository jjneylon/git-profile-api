import json
import requests

from service import constants


class Profile:
    """ Base Profile class with shared logic for github and bitbucket """
    PROFILE_URL = None

    def __init__(self, username, page_len=50):
        self.username = username
        self.page_len = page_len
        self.user_profile = {}
        self.repos = []

        self.total_repo_count = 0
        self.total_watcher_count = 0
        self.total_follower_count = 0
        self.total_stars_received_count = 0
        self.total_stars_given_count = 0
        self.total_open_issues_count = 0
        self.total_repo_commit_count = 0
        self.total_size = 0
        self.languages_used = set()
        self.languages_used_count = 0
        self.repo_topics = set()
        self.repo_topics_count = 0

    @property
    def default_headers(self):
        """ Headers to pass to all requests

        Content-type for all requests is application/json
        The Accept header must be set to a preview in order to show topics
        """
        return {
            'content-type': 'application/json',
            'accept': 'application/vnd.github.mercy-preview+json'
        }

    @property
    def pagination_str(self):
        raise NotImplementedError

    @property
    def repos_url(self):
        raise NotImplementedError

    @property
    def stars_received_url(self):
        raise NotImplementedError

    def get_user_profile(self):
        """ Retrieves the user profile from the api """
        url = self.PROFILE_URL.format(username=self.username)
        response = requests.get(url, headers=self.default_headers)
        self.user_profile = json.loads(response.text)

    def get_repos(self):
        """ Retrieves repo data for the user. Must be overridden """
        raise NotImplementedError

    def get_paginated_list(self, start_url):
        raise NotImplementedError

    def get_paginated_count(self, start_url):
        raise NotImplementedError

    def collect_data(self):
        raise NotImplementedError

    def get_all_data(self):
        """ Retrieves all data """
        self.get_user_profile()
        self.repos = self.get_paginated_list(self.repos_url)
        self.total_stars_received_count = self.get_paginated_count(self.stars_received_url)
        self.collect_data()


class GithubProfile(Profile):
    PROFILE_URL = constants.GITHUB_PROFILE_URL

    @property
    def headers(self):
        """ Headers to pass to all requests

        The Accept header must be set to a preview in order to show topics
        """
        headers = self.default_headers
        headers.update({'accept': 'application/vnd.github.mercy-preview+json'})
        return headers

    @property
    def pagination_str(self):
        return '?per_page={page_len}'

    @property
    def repos_url(self):
        return self.user_profile['repos_url']

    @property
    def stars_received_url(self):
        return self.user_profile['starred_url'].replace('{/owner}{/repo}', '')

    def get_repos(self):
        """ Retrieves the repo data for the github user """
        url = self.user_profile['repos_url']
        response = requests.get(url, headers=self.default_headers)
        repos = json.loads(response.text)
        self.repos = repos

    def get_paginated_count(self, start_url):
        url = start_url + self.pagination_str.format(page_len=1)
        response = requests.head(url)
        last = response.links.get('last', {}).get('url')
        return int(last.split('page=')[-1]) if last else None

    def get_paginated_list(self, start_url):
        url = start_url + self.pagination_str.format(page_len=self.page_len)
        paginated_list = []
        while True:
            response = requests.get(url, headers=self.default_headers)
            paginated_list += json.loads(response.text)
            url = response.links.get('next', {}).get('url')
            if not url:
                break
        return paginated_list

    def collect_data(self):
        self.total_repo_count = len(self.repos)
        self.total_follower_count = self.user_profile['followers']
        self.total_repo_commit_count = 0
        for repo in self.repos:
            self.total_watcher_count += repo['watchers_count']
            self.total_stars_given_count += repo['stargazers_count']
            self.total_open_issues_count += repo['open_issues_count']
            self.total_size += repo['size']
            if repo['language']:
                self.languages_used = self.languages_used.union({repo['language']})
            self.repo_topics = self.repo_topics.union(set(repo['topics']))

        self.languages_used_count = len(self.languages_used)
        self.repo_topics_count = len(self.repo_topics)


class BitbucketProfile(Profile):
    PROFILE_URL = constants.BITBUCKET_PROFILE_URL

    @property
    def headers(self):
        return self.default_headers

    def get_repos(self):
        """ Retrieves the repo data for the bitbucket user. Data is paginated, so we need to loop through each page """
        self.repos = []
        url = self.user_profile['repositories']['href'] + '?pagelen={}'.format(self.page_len)
        while True:
            response = requests.get(url, headers=self.headers)
            response_body = json.loads(response.text)
            repos = response_body['values']
            self.repos += repos
            if self.page_len and len(self.repos) < response_body['size']:
                url = repos['next']
            else:
                break


class ConsolidatedProfile:
    def __init__(self, github_profile, bitbucket_profile):
        self.github_profile = github_profile
        self.bitbucket_profile = bitbucket_profile

    @property
    def dict(self):
        """ A dictionary of all data consolidated from both profiles """
        response_dict = {
            'github_username': self.github_profile.username,
            'bitbucket_username': self.bitbucket_profile.username,
        }
        for attr in (
            'total_repo_count',
            'total_watcher_count',
            'total_follower_count',
            'total_stars_received_count',
            'total_stars_given_count',
            'total_open_issues_count',
            'total_repo_commit_count',
            'total_size',
            'languages_used_count',
            'repo_topics_count',
        ):
            response_dict[attr] = getattr(self.github_profile, attr) + getattr(self.bitbucket_profile, attr)

        for attr in (
            'languages_used',
            'repo_topics',
        ):
            response_dict[attr] = list(getattr(self.github_profile, attr).union(getattr(self.bitbucket_profile, attr)))

        return response_dict
