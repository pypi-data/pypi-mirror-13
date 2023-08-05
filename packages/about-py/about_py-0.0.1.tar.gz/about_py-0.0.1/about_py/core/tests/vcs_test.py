from git import Repo

from about_py.core import vcs
from about_py.core.vcs import get_vcs_info, locate_git


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
