import logging
import os
import re
from datetime import datetime

from git import Repo

from about_py.utils.bunch import Bunch
from about_py.utils.exceptions import AboutPyException

join = os.path.join

LOG = logging.getLogger(__name__)


def locate_git(path=None):
    if not path:
        path = os.path.abspath('.')

    git_dir = os.path.join(path, '.git')
    if os.path.isdir(git_dir):
        return path

    else:
        parent_path = os.path.abspath(os.path.join(path, os.pardir))
        if parent_path == path:
            raise AboutPyException('No git repository found.')
        else:
            return locate_git(parent_path)


def get_vcs_info():
    # rorepo is a a Repo instance pointing to the git-python repository.
    # For all you know, the first argument to Repo is a path to the repository
    # you want to work with
    vcs_bunch = Bunch()
    try:
        git_location = locate_git()
        assert git_location != None
        repo = Repo(git_location)
        vcs_bunch.name = 'Git'
        origin = repo.remotes['origin']
        origin_url = origin.url
        if origin_url.startswith('git@'):
            # convert the origin url to a https url
            p = re.compile('^(git@)(?P<domain>(\w+\.)*\w+)(:)(.*)(.git)')
            origin_url = p.sub('https://\g<2>/\g<5>', origin_url)
        vcs_bunch.origin_url = origin_url
        vcs_bunch.last_commit = {
            'message': repo.commit().message,
            'date': datetime.fromtimestamp(repo.commit().committed_date),
            'url': '{0}/commit/{1}'.format(origin_url, repo.commit().hexsha),
        }
        vcs_bunch.last_pull_requests = parse_commit_log(repo.git.log(n=5, merges=True, grep='Merge pull request'),
                                                        vcs_bunch.origin_url)
    except Exception:
        pass
    return vcs_bunch


def parse_commit_log(commit_log, repo_url):
    all_commits = []
    commit = Bunch()
    for line in commit_log.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('commit '):
            if not commit.is_empty():
                all_commits.append(commit)
            commit = Bunch()
            commit.id = line.split(' ')[1]
            commit.message = ''
        elif line.startswith('Merge:'):
            continue
        elif line.startswith('Author:'):
            continue
        elif line.startswith('Date:'):
            date_str = line.replace('Date:', '').strip()
            commit.date = datetime.strptime(date_str.split('+')[0].strip(), '%a %b %d %H:%M:%S %Y')
        elif line.startswith('Merge pull request'):
            m = re.match('.*#(\d+).*', line)
            commit.pull_request_id = m.groups()[0]
            commit.pull_request_url = repo_url + '/pull/' + commit.pull_request_id
        else:
            commit.message += line + '\n'
    if not commit.is_empty():
        all_commits.append(commit)
    return all_commits




