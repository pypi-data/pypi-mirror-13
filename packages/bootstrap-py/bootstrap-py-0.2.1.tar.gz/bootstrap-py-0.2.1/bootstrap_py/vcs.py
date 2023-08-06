# -*- coding: utf-8 -*-
"""bootstrap_py.vcs."""
import git


class VCS(object):
    """VCS class."""

    def __init__(self, repo_dir, vcs_type):
        """Initialize."""
        # repo_dir is outdir

        if vcs_type == 'git':
            self.repo = git.Git(repo_dir)
            self.repo.init()

    def add_index(self):
        """git add ."""
        pass

    def initial_commit(self):
        """initial commit."""
        pass

    def config(self):
        """git config."""
        pass

    def add_remote_repo(self):
        """git remote add."""
        pass
