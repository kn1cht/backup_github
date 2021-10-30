#!/usr/bin/env python
import os
import urllib.parse
from dotenv import load_dotenv
import git
from github import Github

load_dotenv()
github_token = os.getenv('GITHUB_TOKEN')
clone_dir = (os.getenv('CLONE_DIR') +'/').replace('//', '/')

github_scheme = f'https://{github_token}:x-oauth-basic@' # for cloning private repos
g = Github(github_token)

clone_urls = []
for repo in g.get_user().get_repos(type='owner'):
    clone_urls.append(repo.clone_url)

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
