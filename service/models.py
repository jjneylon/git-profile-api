import json
import requests

from service import constants


class Profile:
    """ Base Profile class with shared logic for github and bitbucket """
    PROFILE_URL = None
    REPOS_URL = None

    def __init__(self, username, pagelen=None):
        self.username = username
        self.pagelen = pagelen
        self.user_profile = {}
        self.repos = []

    @property
    def default_headers(self):
        """ Headers to pass to all requests """
        return {'content-type': 'application/json'}

    def get_user_profile(self):
        """ Retrieves the user profile from the api """
        url = self.PROFILE_URL.format(username=self.username)
        response = requests.get(url, headers=self.default_headers)
        self.user_profile = json.loads(response.text)

    def get_repos(self):
        """ Retrieves repo data. Must be overridden """
        raise NotImplementedError

    def get_all_data(self):
        """ Retrieves all data """
        self.get_user_profile()
        self.get_repos()


class GithubProfile(Profile):
    PROFILE_URL = constants.GITHUB_PROFILE_URL
    REPOS_URL = constants.GITHUB_REPOS_URL

    def get_repos(self):
        """ Retrieves the repo data for the github user """
        url = self.REPOS_URL.format(username=self.username)
        response = requests.get(url, headers=self.default_headers)
        repos = json.loads(response.text)
        self.repos += repos


class BitbucketProfile(Profile):
    PROFILE_URL = constants.BITBUCKET_PROFILE_URL
    REPOS_URL = constants.BITBUCKET_REPOS_URL

    def get_repos(self):
        """ Retrieves the repo data for the bitbucket user. Data is paginated, so we need to loop through each page """
        self.repos = []
        url = self.REPOS_URL.format(username=self.username, pagelen=self.pagelen)
        while True:
            response = requests.get(url, headers=self.default_headers)
            response_body = json.loads(response.text)
            repos = response_body.get('values', response_body)
            self.repos += repos
            if self.pagelen and len(self.repos) <= response_body.get('size'):
                url = repos.get('next')
            else:
                break


class ConsolidatedProfile:
    def __init__(self, github_profile, bitbucket_profile):
        self.github_profile = github_profile
        self.bitbucket_profile = bitbucket_profile

    @property
    def dict(self):
        """ A dictionary of all data consolidated from both profiles """
        return {
            'github_username': self.github_profile.username,
            'bitbucket_username': self.bitbucket_profile.username,
            'total_repos': None,
            'total_watcher_count': None,
            'total_follower_count': None,
            'total_stars_received': None,
            'total_stars_given': None,
            'total_open_issues': None,
            'total_repo_commit_count': None,
            'total_github_size': None,
            'total_bitbucket_size': None,
            'languages_used': [],
            'languages_used_count': None,
            'repo_topics': [],
            'repo_topics_count': None,
        }
