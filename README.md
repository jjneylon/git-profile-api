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
- bitbucket_username: str,
- github_username: str,
- total_repo_count: int,
- total_watcher_count: int,
- total_follower_count: int,
- total_stars_received_count: int,
- total_stars_given_count: int,
- total_open_issues_count: int,
- total_size: int,
- languages_used: list of str,
- languages_used_count: int,
- repo_topics: list of str,
- repo_topics_count: int,

Example
```
curl -X GET "http://127.0.0.1:5000/api/profile?github=kennethreitz&bitbucket=mailchimp"
{
	"bitbucket_username": "mailchimp",
	"github_username": "kennethreitz",
	"total_repo_count": 102
	"total_watcher_count": 58152,
	"total_follower_count": 23458,
	"total_stars_received_count": 1895,
	"total_stars_given_count": 57740,
	"total_open_issues_count": 522,
	"total_size": 16628946,
	"languages_used": ["Lua", "php", "CSS", "javascript", "HTML", "Python", "Swift", "ruby", "Shell", "python", "dart", "Ruby"],
	"languages_used_count": 12,
	"repo_topics": ["tool", "cdn", "humans", "wallet", "sublime-package", "pep8", "pipfile", "android", "guide", "lua", "s3", "installers", "editor", "emoji-picker", "emoji", "codeeditor", "super", "forumans", "js", "sqlalchemy", "ethereum", "client", "cdnjs", "css-selectors", "eth", "compilers", "python3", "inbox", "background-jobs", "pip", "audio", "mock", "no-authentication", "requests", "nicehash", "api-client", "love2d-framework", "samples", "code", "thanks", "texteditor", "shell-scripts", "background", "setuptools", "loops", "flask", "extension", "schemas", "monkeypatching", "twitter-api", "love2d", "orm", "kennethreitz", "bitcoin", "awesome", "tweets", "time", "sublime-text-3", "ripple", "pipenv", "game", "sql", "wsl", "awesome-list", "black", "gcc", "api", "fuse", "http", "twitter", "dotfiles", "datetimes", "css", "beautifulsoup", "jobs", "django", "sublime-text-plugin", "environment", "packaging", "times", "windows", "fs", "bash", "opensource", "homebrew", "shell-extension", "gofmt", "date", "production", "coin", "codeformatter", "lxml", "distutils", "scraping", "algo", "package-control", "cli", "fish", "scraper", "cryptocurrency", "music", "mac", "documentation", "forhumans", "zsh", "requests-html", "parsing", "algorithms", "love", "for-humans", "template", "javascript", "autopep8", "tasks", "doctl", "wav", "ios", "pyfmt", "dates", "html", "soundcloud", "postgres", "digitalocean", "html5", "litecoin", "linux", "ubuntu", "action", "yapf", "saythanks", "pyquery", "fish-shell", "git", "cd", "btc", "thankfulness", "2d", "edm", "python"],
	"repo_topics_count": 139,
}
```