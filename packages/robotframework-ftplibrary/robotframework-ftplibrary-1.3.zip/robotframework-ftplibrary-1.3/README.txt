Robot Framework FTP Library

-----------------------------license--------------------------------
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

----------------------------------------------------------------------

This library provides functionality of FTP client.

Version 1.3 released on 30th of January 2016.

What's new in release 1.3:
- multiple connections in parallel
- strongly refactored source code
- enabling/disabling printout of messages returned by ftp server

Despite new features, 1.3 should be compatible with previous versions.

FTP communication provided by ftplib.py

Author: Marcin Kowalczyk

Website: http://sourceforge.net/projects/rf-ftp-py/

Installation:
- run command: pip install robotframework-ftplibrary

OR
- download, unzip and run command: python setup.py install

OR
- download, unzip and copy FtpLibrary.py file to a directory pointed by
    PYTHONPATH (for example ...\Python27\lib\site-packages).

The simplest example (connect, change working dir, print working dir, close):
 | ftp connect | 192.168.1.10 | mylogin | mypassword |
 | cwd | /home/myname/tmp/testdir |
 | pwd |
 | ftp close |

It is possible to use multiple ftp connections in parallel. Connections are
identified by string identifiers:
 | ftp connect | 192.168.1.10 | mylogin | mypassword | connId=ftp1 |
 | ftp connect | 192.168.1.20 | mylogin2 | mypassword2 | connId=ftp2 |
 | cwd | /home/myname/tmp/testdir | ftp1 |
 | cwd | /home/myname/tmp/testdir | ftp2 |
 | pwd | ftp2 |
 | pwd | ftp1 |
 | ftp close | ftp2 |
 | ftp close | ftp1 |

During library import it is possible to disable logging of server messages.
By default logging is enabled:
 | Library | FtpLibrary.py |
 To disable logging of server messages, additional parameter must be added to import:
 | Library | FtpLibrary.py | False |