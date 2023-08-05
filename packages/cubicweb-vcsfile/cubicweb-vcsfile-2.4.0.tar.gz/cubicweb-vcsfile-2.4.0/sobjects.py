
from hglib.error import CommandError

from cubicweb.server import Service


class RevisionExportService(Service):
    """return the patch version of a revision
    """

    __regid__ = 'vcs.export-rev'

    def call(self, repo, nodeid):
        repo_ent = self._cw.entity_from_eid(repo)
        if repo_ent.type != 'mercurial':
            # no svn support yet (use a selector when we have multiple versions)
            return None
        hdrepo = repo_ent.cw_adapt_to('VCSRepo')
        try:
            with hdrepo.hgrepo() as hgrepo:
                if nodeid in hgrepo:
                    return hgrepo.export(revs=nodeid, git=True)
        except CommandError as e:
            return None


class RevisionDiffService(Service):
    """ Return the diff between two revisions."""

    __regid__ = 'vcsfile.export-rev-diff'

    def call(self, repo_eid, rev1, rev2):
        repo = self._cw.entity_from_eid(repo_eid)
        adapter = repo.cw_adapt_to('VCSRepo')
        try:
            with adapter.hgrepo() as hgrepo:
                return hgrepo.diff(revs=[rev1, rev2], git=True, unified=5,
                                   showfunction=True)
        except CommandError:
            return None
