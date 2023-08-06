"""
Dpkg-based operating systems
"""
import glob

from sortedcontainers import SortedList
from future.moves import itertools
import os
from zope.interface import implementer

from jw.backup.os import base

PKG_DB = '/var/lib/dpkg/info'

@implementer(base.OsBase)
class Dpkg(object):
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
            e for e in (
                f.rstrip('\r\n')
                for f in itertools.chain(*(open(i).readlines() for i in glob.glob(PKG_DB + '/*.list')))
            )
            if e != '/.'
        )

    def check(self):
        """
        Check whether OS is dpkg-based (Debian, Ubuntu et al)

        :return: True if this OS is installed
        :rtype: bool

        Returns True if this OS is managed by the dpkg package management (Debian, Ubuntu etc)
        """
        return os.path.exists(PKG_DB)