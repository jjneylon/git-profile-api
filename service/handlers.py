from service.models import (
    BitbucketProfile,
    ConsolidatedProfile,
    GithubProfile,
)


def handle_get_profile(github_username, bitbucket_username):
    """ Handler for get profile.

    :param github_username: username of a github user
    :type github_username: str
    :param bitbucket_username: username of a bitbucket user
    :type bitbucket_username: str
    :return: consolidated user info for both profiles
    :rtype: dict
    """
    github_profile = GithubProfile(github_username)
    github_profile.get_all_data()
    bitbucket_profile = BitbucketProfile(bitbucket_username)
    bitbucket_profile.get_all_data()
    profile = ConsolidatedProfile(github_profile, bitbucket_profile)

    return profile.dict
