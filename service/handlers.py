import json

import requests


API_URLS = {
    'github': 'https://api.github.com/users/{username}',
    'bitbucket': 'https://api.bitbucket.org/1.0/users/{username}',
}
# Note: The bitbucket endpoint is deprecated. The 2.0 endpoint lists public accounts as inaccessible "team accounts"


def get_user_profile(sitename, username):
    """ Make a GET request to the given site's user endpoint and returns a dict of the response

    :param sitename: The site of the api to request
    :type sitename: str
    :param username: The username of the profile
    :type username: str
    """
    headers = {'content-type': 'application/json'}
    response = requests.get(API_URLS[sitename].format(username=username), headers=headers)
    return json.loads(response.text)
