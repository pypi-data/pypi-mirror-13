"""
Base OS
"""

import zope.interface

class OsBase(zope.interface.Interface):
    """
    OS Interface
    """

    def systemFiles(self):
        """
        Get system-installed files

        :return: list of system-installed files
        :rtype: list
        """

    def check(self):
        """
        Check whether this OS is installed

        :return: True if this Os is installed
        :rtype: bool
        """
