from datetime import datetime

from git import Repo

from about_py.core import vcs
from about_py.core.vcs import get_vcs_info, locate_git, parse_commit_log


class MockOrigin(object):

    def __init__(self, fetch_url=None):
        self.url = fetch_url


def test_no_vcs(monkeypatch):
    monkeypatch.setattr(vcs, 'locate_git', lambda: None)
    info = get_vcs_info()
    assert info.is_empty()


def test_get_vcs_info(monkeypatch):
    monkeypatch.setattr(vcs, 'locate_git', lambda: '.')
    monkeypatch.setattr(Repo, 'remotes', {'origin': MockOrigin('https://github.com/ceasaro/about_py')})
    info = get_vcs_info()
    assert info.name == 'Git'
    assert info.origin_url == 'https://github.com/ceasaro/about_py'


def test_github_vcs_info(monkeypatch):
    monkeypatch.setattr(vcs, 'locate_git', lambda: '.')
    monkeypatch.setattr(Repo, 'remotes', {'origin': MockOrigin('git@github.com:ceasaro/about_py.git')})
    info = get_vcs_info()
    assert info.name == 'Git'
    assert info.origin_url == 'https://github.com/ceasaro/about_py'


def test_bitbucket_vcs_info(monkeypatch):
    monkeypatch.setattr(vcs, 'locate_git', lambda: '.')
    monkeypatch.setattr(Repo, 'remotes', {'origin': MockOrigin('git@bitbucket.org:ceasaro/scripts.git')})
    info = get_vcs_info()
    assert info.name == 'Git'
    assert info.origin_url == 'https://bitbucket.org/ceasaro/scripts'


def test_parse_commit_log():
    git_logs = u'commit 0ce74ff82b840fae6af64593ca1e6ef67982a53a\nMerge: 4cab26e 98f8c7b\nAuthor: Cees van Wieringen <ceesvw@gmail.com>\nDate:   Wed Dec 23 19:31:47 2015 +0100\n\n    Merge pull request #2507 from Crop-R/django_1_7_v2\n    \n    Django 1 7 v2\n\ncommit c9b1f45aa7ece24265bb8b7275dfa34cf036ee31\nMerge: e396362 e474216\nAuthor: JJStoker <jeroen@crop-r.com>\nDate:   Wed Dec 23 16:59:15 2015 +0100\n\n    Merge pull request #2502 from Crop-R/organismen_toelatingen_admin\n    \n    Toelatingbeheer: organismen gefixed\n\ncommit e39636217110ba0d79417c0d570dd953be68ea87\nMerge: 1d5bdbe a27fc33\nAuthor: Nico-van-Ek <nico@crop-r.com>\nDate:   Wed Dec 23 09:35:31 2015 +0100\n\n    Merge pull request #2500 from Crop-R/testresultaten_sensus_admin\n    \n    melding weergeven als er geen gewaspercelen zijn'
    commits = parse_commit_log(git_logs, 'http://example.com')
    assert len(commits) == 3
    assert commits[0].pull_request_id == '2507'
    assert commits[0].pull_request_url == 'http://example.com/pull/2507'
    assert commits[0].id == '0ce74ff82b840fae6af64593ca1e6ef67982a53a'
    assert commits[0].message == 'Django 1 7 v2\n'
    assert commits[0].date == datetime(year=2015, month=12, day=23, hour=19, minute=31, second=47)
    assert commits[2].pull_request_id == '2500'
    assert commits[2].id == 'e39636217110ba0d79417c0d570dd953be68ea87'
    assert commits[2].message == 'melding weergeven als er geen gewaspercelen zijn\n'
