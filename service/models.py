import json
import requests

from service import constants


class Profile:
    """ Base Profile class with shared logic for github and bitbucket """
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
        self.total_size = 0
        self.languages_used = set()
        self.repo_topics = set()

    @property
    def default_headers(self):
        """ Headers to pass to all requests

        Content-type for all requests is application/json
        """
        return {
            'content-type': 'application/json',
        }


class GithubProfile(Profile):
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
    def profile_url(self):
        return constants.GITHUB_PROFILE_URL

    @property
    def repos_url(self):
        return self.user_profile['repos_url']

    @property
    def stars_received_url(self):
        return self.user_profile['starred_url'].replace('{/owner}{/repo}', '')

    def get_user_profile(self):
        """ Retrieves the user profile from the api """
        url = self.profile_url.format(username=self.username)
        response = requests.get(url, headers=self.headers)
        self.user_profile = response.json()

    def get_paginated_count(self, start_url):
        """ Sends a head request to get a count of resources at a endpoint

        :param start_url: url of the first page of an endpoint
        :type start_url: str
        """
        url = start_url + self.pagination_str.format(page_len=1)
        response = requests.head(url)
        last = response.links.get('last', {}).get('url')
        return int(last.split('page=')[-1]) if last else None

    def get_paginated_list(self, start_url):
        """ Sends a get request to get a full list of resources at an endpoint. Loops through each page

        :param start_url: url of the first page of an endpoint
        :type start_url: str
        """
        url = start_url + self.pagination_str.format(page_len=self.page_len)
        paginated_list = []
        while True:
            response = requests.get(url, headers=self.headers)
            paginated_list += response.json()
            url = response.links.get('next', {}).get('url')
            if not url:
                break
        return paginated_list

    def get_all_data(self):
        """ Retrieves all data. Loops through each repo to get counts """
        self.get_user_profile()
        self.repos = self.get_paginated_list(self.repos_url)
        self.total_stars_received_count = self.get_paginated_count(self.stars_received_url)

        self.total_repo_count = len(self.repos)
        self.total_follower_count = self.user_profile['followers']
        for repo in self.repos:
            self.total_watcher_count += repo['watchers_count']
            self.total_stars_given_count += repo['stargazers_count']
            self.total_open_issues_count += repo['open_issues_count']
            self.total_size += repo['size']
            if repo['language']:
                self.languages_used = self.languages_used.union({repo['language']})
            self.repo_topics = self.repo_topics.union(set(repo['topics']))


class BitbucketProfile(Profile):
    @property
    def headers(self):
        return self.default_headers

    @property
    def pagination_str(self):
        return '?pagelen={page_len}'

    @property
    def profile_url(self):
        return constants.BITBUCKET_PROFILE_URL

    @property
    def teams_url(self):
        return constants.BITBUCKET_TEAMS_URL

    @property
    def repos_url(self):
        return self.user_profile['links']['repositories']['href']

    @property
    def followers_url(self):
        return self.user_profile['links']['followers']['href']

    def get_user_profile(self):
        """ Retrieves the user profile from the api

        If the user is a "team account", then it will try the teams url
        """
        url = self.profile_url.format(username=self.username)
        response = requests.get(url, headers=self.headers)
        response_body = response.json()
        if response_body.get('error', {}).get('message') == '{} is a team account'.format(self.username):
            url = self.teams_url.format(username=self.username)
            response = requests.get(url, headers=self.headers)
            response_body = response.json()

        self.user_profile = response_body

    def get_paginated_count(self, start_url):
        """ Sends a get request to get a count of resources at a endpoint

        :param start_url: url of the first page of an endpoint
        :type start_url: str
        """
        url = start_url + self.pagination_str.format(page_len=0)
        response = requests.get(url, headers=self.headers)
        response_body = response.json()
        return response_body['size']

    def get_paginated_list(self, start_url):
        """ Sends a get request to get a full list of resources at an endpoint. Loops through each page

        :param start_url: url of the first page of an endpoint
        :type start_url: str
        """
        url = start_url + self.pagination_str.format(page_len=self.page_len)
        paginated_list = []
        while True:
            response = requests.get(url, headers=self.headers)
            response_body = json.loads(response.text)
            paginated_list += response_body['values']
            url = response_body.get('next')
            if not url:
                break

        return paginated_list

    def get_all_data(self):
        """ Retrieves all data. Loops through each repo and makes additional requests to get counts """
        self.get_user_profile()
        self.repos = self.get_paginated_list(self.repos_url)
        self.total_follower_count = self.get_paginated_count(self.followers_url)
        self.total_repo_count = len(self.repos)

        for repo in self.repos:
            self.total_watcher_count += self.get_paginated_count(repo['links']['watchers']['href'])
            self.total_size += repo['size']

            issues_link = repo['links'].get('issues', {}).get('href')
            if issues_link:
                self.total_open_issues_count += self.get_paginated_count(issues_link)
            if repo['language']:
                self.languages_used = self.languages_used.union({repo['language']})


class ConsolidatedProfile:
    """ Class containing logic to consolidate the attributes of two profiles """
    def __init__(self, github_profile, bitbucket_profile):
        self.github_profile = github_profile
        self.bitbucket_profile = bitbucket_profile

    @property
    def dict(self):
        """ A dictionary of all data consolidated from both profiles """

        response_dict = {
            'github_username': self.github_profile.username,
            'bitbucket_username': self.bitbucket_profile.username,
            'languages_used': list(self.github_profile.languages_used.union(self.bitbucket_profile.languages_used)),
            'repo_topics': list(self.github_profile.repo_topics.union(self.bitbucket_profile.repo_topics)),
            'total_repo_count': self.github_profile.total_repo_count + self.bitbucket_profile.total_repo_count,
            'total_watcher_count': self.github_profile.total_watcher_count + self.bitbucket_profile.total_watcher_count,
            'total_follower_count': self.github_profile.total_follower_count + self.bitbucket_profile.total_follower_count,
            'total_stars_received_count': self.github_profile.total_stars_received_count + self.bitbucket_profile.total_stars_received_count,
            'total_stars_given_count': self.github_profile.total_stars_given_count + self.bitbucket_profile.total_stars_given_count,
            'total_open_issues_count': self.github_profile.total_open_issues_count + self.bitbucket_profile.total_open_issues_count,
            'total_size': self.github_profile.total_size + self.bitbucket_profile.total_size,
        }
        response_dict.update({
            'languages_used_count': len(response_dict['languages_used']),
            'repo_topics_count': len(response_dict['repo_topics']),
        })

        return response_dict
