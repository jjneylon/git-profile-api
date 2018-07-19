# git-profile-api
API that retrieves user information from github and bitbucket


## Run Server

```
virtualenv venv --python=python3.6
source venv/bin/activate
pip install -r requirements.txt
python runserver.py -H 127.0.0.1 -P 5000
```

The server will run on http://127.0.0.1:5000

### API Endpoints

#### Profile

`/api/profile?github=<username>&bitbucket=<username>`

METHOD: GET

parameters:
- github: The username of the github profile to collect
- bitbucket: The username of the bitbucket profile to collect

Response
- github_username: str,
- bitbucket_username: str,
- total_repos: int,
- total_watcher_count: int,
- total_follower_count: int,
- total_stars_received: int,
- total_stars_given: int,
- total_open_issues: int,
- total_repo_commit_count: int,
- total_github_size: int,
- total_bitbucket_size: int,
- languages_used: list of str,
- languages_used_count: int,
- repo_topics: list of str,
- repo_topics_count: int,
