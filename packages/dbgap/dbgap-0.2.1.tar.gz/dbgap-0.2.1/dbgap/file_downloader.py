# Copyright (c) 2016, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
from ftplib import FTP
import os
import logging
from typing import Callable, Optional


class MemFile:
    """ A simple in-memory reader/writer
    """
    def __init__(self):
        self.text = ""

    def write(self, txt):
        self.text += txt.decode('utf-8') if isinstance(txt, bytes) else txt

    def read(self):
        return self.text


class FileWrapper:
    def __init__(self, fname: Optional[str] = None):
        self.file = open(fname, 'w') if fname else MemFile()

    def write(self, txt):
        self.file.write(txt.decode('utf-8') if isinstance(txt, bytes) else txt)

    def read(self):
        return self.file.read()


class FileDownloader:
    """ Utility that supports FTP transfer of directories and files
    """
    def __init__(self, root_directory: str) -> None:
        """ Construct a downloader for root_directory
        :param root_directory:
        :return:
        """
        self.root_directory = root_directory
        self.ftp = FTP(root_directory)
        self.ftp.login()
        self.nfiles = 0

    def _download_file(self, fname: str, target_file: FileWrapper) -> None:
        """ Download fname from the current working ftp directory
        :param fname: name of file to download
        :param target_file: target file to write to (anything that matches MemFile signature)
        """
        self.ftp.retrbinary('RETR ' + fname,
                            lambda line: target_file.write(line.decode('utf-8') if isinstance(line, bytes) else line))

    def download_dir(self, source_dir: str, target_dir: str, name_map: Callable[[str], str]=lambda s: s,
                     file_filtr: Callable[[str], bool]=lambda s: True) -> int:
        """ Download all of the files in source directory that match the filter requirement and store them in the
        target directory.
        :param source_dir: Source directory relative to the ftp root
        :param target_dir: Destination directory.  Must exist.
        :param name_map: Target file name map function.  Default: identity function
        :param file_filtr: File name filter.  True means download, false means skip
        :return: Number of files downloaded
        """
        nfiles = 0
        logging.info("Downloading files from %s%s into %s" % (self.root_directory, source_dir, target_dir))
        self.ftp.cwd(source_dir)
        for f in self.ftp.nlst():
            if file_filtr(f):
                tf = os.path.join(target_dir, name_map(f))
                logging.info("  Reading %s into %s" % (f, tf))
                self._download_file(f, FileWrapper(tf))
                nfiles += 1
        return nfiles

    def download_file(self, file_name: str) -> str:
        """ Download and return the referenced file
        :param file_name: source file name
        :return: text of downloaded file
        """
        logging.info("Downloading  %s" % file_name)
        target = FileWrapper()
        self._download_file(file_name, target)
        return target.read()
