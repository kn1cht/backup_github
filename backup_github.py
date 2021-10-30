#!/usr/bin/env python
import json
import os
import re
import urllib.parse
from dotenv import load_dotenv
import git
from github import Github

###### read settings ######
load_dotenv()
github_token = os.getenv('GITHUB_TOKEN')
clone_dir = (os.getenv('CLONE_DIR') +'/').replace('//', '/')
with open(os.path.join(os.path.dirname(__file__), 'repository_settings.json')) as f:
    repos = json.load(f)

###### prepare github client ######
github_scheme = f'https://{github_token}:x-oauth-basic@' # for cloning private repos
g = Github(github_token)

###### get urls from github (the user and organizations) ######
clone_urls = [repo.clone_url for repo in g.get_user().get_repos(type='owner')]

clone_urls_org = set()
for org in repos['orgs']:
    for repo in g.get_organization(org['name']).get_repos(type='owner'):
        if 'patterns' in org and len(org['patterns']) != 0:
            for pattern in org['patterns']:
                if re.search(pattern, repo.name) is not None:
                    clone_urls_org.add(repo.clone_url)
        else:
            clone_urls_org.add(repo.clone_url)

clone_urls += list(clone_urls_org)

###### perform git clone or git pull ######
for url in clone_urls:
    parsed_url = urllib.parse.urlparse(os.path.splitext(url)[0])
    repo_path = parsed_url.netloc + parsed_url.path # e.g. github.com/github/gitignore
    if not os.path.exists(f'{clone_dir}{repo_path}'):
        try:
            git.Repo.clone_from(f'{github_scheme}{repo_path}', f'{clone_dir}{repo_path}', multi_options=['--recursive'])
            print(f'[{repo_path}] performed git clone')
        except git.exc.GitCommandError as e:
            # print(str(e))
            print(f'[{repo_path}] clone failed')

    repo = git.Repo(f'{clone_dir}{repo_path}')
    info = repo.remote().pull()[0]
    if info.old_commit is not None:
        print(f'[{repo_path}] performed git pull: {info.old_commit}...{info.ref}')
