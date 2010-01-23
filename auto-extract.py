# Script:   Auto-Extract (Python edition)
# Author:   Mark Stahler <markstahler@gmail.com>
# Website:  http://bitbucket.org/markstahler/auto-unrar-python/, http://www.markstahler.ca
# Version:  1.00
# Released: January 2010
# License:  BSD
#
# Description:  Auto-Extract is a script designed to be run as a cron job (or scheduled task).
#   Its purpose is to recursively scan a directory for archive files and extract them. The script
#   is designed to be run at regular intervals and will create a file named .unrared in each
#   directory that contains an archive extracted by the script. This file is used to tell the
#   script, on subsequent scans, that the archive in the marked folder has previously been
#   extracted.
#
# Limitations:  Auto-Extract has been written to support one archive group per directory scanned
#   (Example a movie in its own directory with files .rar, .r01, .r02, .nfo, etc). This works well
#   with movies and other files that are packed and downloaded in individual directories.
#
#   Auto-Extract will overwrite previously extracted files if it does not find a .unrar file
#   present in the archive directory.
#
# Requirements:
# -Python 2.4 or newer
# -unrar in your path [Freeware command line version available from http://www.rarlab.com/]
#
# BUGS:
#   -Cannot tell if a archive has been fully downloaded
#
# TODO:
#   -Proper logging (ie. debug, info messages)
#   -Check for available disk space and estimate required
#   -Support for other archive types
#

import os, sys
import pdb

class Unrar(object):
    def __init__(self):
        # Global Variables
        #------------------
        self.mark_file_name = '.unrared'
        self.extensions_unrar = ['.rar', '.r01']        # List of extensions for auto-extract to look for
        self.extensions_unzip = ['.zip']
        self.supported_filetypes = []                   # Filled by extensions_list function
        self.extensions_list()

        # Sanity Checks
        #------------------
        # Check for proper number of parameters (TODO: and that parameters are correct)
        if len(sys.argv) < 2:
            self.display_help()
        # Check that we can find unrar on this system
        self.unrar_check()
        # Check that the download directory parameters is actually a directory
        self.check_arguments()
        self.traverse_directories()

    '''Displays script command line usage help'''
    def display_help(self):
        print 'usage: ' + sys.argv[0] + ' [options] [download_directory]'
        print 'options:'
        print '     -h, --help      Display this help message'
        exit()

    '''Creates the list of extensions supported by the script'''
    def extensions_list(self):
        self.supported_filetypes.extend(self.extensions_unrar)       # rar support
        self.supported_filetypes.extend(self.extensions_unzip)       # zip support (Not implemented yet)

    '''Figures out what the unrar executable name should be'''
    def unrar_exe(self):
        unrar_name = 'unrar'
        # If on Windows, add .exe to the end of the program file name
        if sys.platform == 'win32':
            unrar_name = 'UnRAR.exe'
        self.unrar_name = unrar_name

    '''Attempts to find unrar on the system path and return the directory unrar is found in'''
    def find_unrar(self):
        for dir in os.getenv('PATH').split(os.pathsep):
            # Ensure the dir in the path is a real directory
            if os.path.exists(dir):
                files = os.listdir(dir)
                if self.unrar_name in files:
                    # Found it!
                    print 'Found ' + self.unrar_name +' in ' + dir
                    return dir
            else:
                # The directory in the path does not exist
                pass
        return False

    '''Sanity check to make sure unrar is found on the system'''
    def unrar_check(self):
        self.unrar_exe()
        self.unrar_path = self.find_unrar()
        if self.unrar_path != False:
            self.unrar_exe = os.path.join(self.unrar_path, self.unrar_name)
        else:
            print 'Error: ' + self.unrar_name + ' not found in the system path \n'
            exit()

    '''Ensure download dir argument is in fact a directory'''
    def check_arguments(self):
        if os.path.isdir(sys.argv[1]):
            self.download_dir = os.path.abspath(sys.argv[1])

    '''Scan the download directory and its subdirectories'''
    def traverse_directories(self):
        # Search download directory and all subdirectories
        for dirname, dirnames, filenames in os.walk(self.download_dir):
            self.scan_for_archives(dirname)


    '''Check for rar files in each directory'''
    def scan_for_archives(self, dir):
        # Look for a .rar archive in dir
        dir_listing = os.listdir(dir)
        # First archive that is found with .rar extension is extracted
        # (for directories that have more than one archives in it)
        for filename in dir_listing:
            for ext in self.supported_filetypes:
                if filename.endswith(ext):
                    # If a .rar archive is found, check to see if it has been extracted previously
                    file_unrared = os.path.exists(os.path.join(dir, self.mark_file_name))
                    if file_unrared == False:
                        print "Need to extract: " + filename
                        # Start extracting file
                        self.start_unrar(dir, filename)
                    else:
                        print 'Skipping archive ' + filename
                    # .rar was found, dont need to search for .r01
                    break


    '''Extract a rar archive'''
    def start_unrar(self, dir, archive_name):
        # Create command line arguments for rar extractions
        cmd_args = ['','','','']
        cmd_args[0] = self.unrar_name                   # unrar
        cmd_args[1] = 'e'                               # command line switches: e - extract, u - update all files
        cmd_args[2] = os.path.join(dir, archive_name)   # archive path
        cmd_args[3] = dir                               # destination

        try:
            os.spawnv(os.P_WAIT, self.unrar_exe, cmd_args)
        except OSError:
            print 'Error: ' + self.unrar_name + ' not found in the given path \n'
            exit()

        # Sucessfully extracted archive, mark the dir with a hidden file
        self.mark_dir(dir)

    '''Creates a hidden file so the same archives will not be extracted again'''
    def mark_dir(self, dir):
        mark_file = os.path.join(dir, self.mark_file_name)
        f = open(mark_file,'w')
        f.close()
        print self.mark_file_name + ' file created'

if __name__ == '__main__':
    obj = Unrar()
