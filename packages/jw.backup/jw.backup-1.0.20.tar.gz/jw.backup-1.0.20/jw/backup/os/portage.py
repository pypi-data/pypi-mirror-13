"""
Gentoo Linux
"""
import glob

from sortedcontainers import SortedList
from future.moves import itertools
import os
from zope.interface import implementer

from jw.backup.os import base

PKG_DB = '/var/db/pkg'

@implementer(base.OsBase)
class Portage(object):
    """
    Dpkg-based interface
    """

    def __init__(self):
        """
        Create a Dpkg object
        """

    def systemFiles(self):
        """
        Get system-installed files

        :return: list of system-installed files
        :rtype: list
        """
        # Generate the list of files belonging to Dpkg packages
        return SortedList(
            e[1] for e in (
                f.rstrip('\r\n').split()
                for f in itertools.chain(*(open(i).readlines() for i in glob.glob(PKG_DB + '/*/*/CONTENTS')))
            )
            if e[0] != 'dir'
        )

    def check(self):
        """
        Check whether OS is portage-based (Gentoo et al)

        :return: True if this OS is installed
        :rtype: bool

        Returns True if this OS is managed by the portage package management (Gentoo)
        """
        return os.path.exists('/usr/portage') and os.path.exists('/etc/portage') and os.path.exists(PKG_DB)