#! /usr/bin/env python
"""
The purpose of this script is to update dot files somewhere.  It works in the
following way.  Two locations are set

dothome : ($HOME)
    absolute path to the set the dotfiles

dotarchive : ($HOME/.dotarchive)
    absolute path to the dot files (usually some git archive)

Then symlinks are made from dothome to dotarchive.  Simple as that.
"""
import os
import shutil

__version__ = '0.2.2'


def vprint(string, verbose):
    if verbose:
        print('\t[ditto] %s' % string)


def make_symlinks(dothome, dotarchive, dotfiles, verbose=False):
    """
    1. if needed, create dothome/.dotfiles-original
    2. for each dotfile:
        a check for file or directory (not a symlink)
        b if not in the backup, move to the backup
        c create a symbolic link to dotarchive
    """

    # 1
    dotbackup = os.path.join(dothome, '.dotfiles-original')
    if not os.path.isdir(dotbackup):  # makes this python 2 compliant
        vprint('.dotfiles-original does not exist...making', verbose)
        try:
            os.makedirs(dotbackup)
        except:
            raise IOError('Problem making %s' % dotbackup)
    else:
        vprint('.dotfiles-original exists', verbose)

    # 2
    for dotf in dotfiles:

        dotfloc = os.path.join(dothome, '.' + dotf)
        dotfbloc = os.path.join(dotbackup, dotf)
        dotfaloc = os.path.join(dotarchive, dotf)

        # 2a
        if os.path.islink(dotfloc):
            vprint('%s already linked' % dotf, verbose)
            pass
        elif os.path.isfile(dotfloc) or os.path.isdir(dotfloc):
            # 2b
            vprint('%s found in home' % dotf, verbose)
            if os.path.isfile(dotfbloc) or os.path.isdir(dotfbloc):
                raise ValueError('Found a file (%s) that is already backed up'
                                 % dotf)
            else:
                shutil.move(dotfloc, dotfbloc)
                vprint('%s moved to backup' % dotf, verbose)

        # 2c
        if not os.path.islink(dotfloc):
            vprint('%s not symlinked' % dotf, verbose)
            if not (os.path.isfile(dotfaloc) or os.path.isdir(dotfaloc)):
                vprint('File %s does not exist' % dotfaloc,
                       verbose)
            else:
                try:
                    os.symlink(dotfaloc, dotfloc)
                    vprint('%s is now symlinked' % dotf, verbose)
                except:
                    raise IOError('Could not symlink %s' % dotfaloc)


def get_dotfiles_list(dotarchive, verbose=False):
    """
    Attempt to find a list of files in setup.cfg

    If not, just grab the files in dotarchive
    """
    cfg_file = os.path.join(dotarchive, 'setup.cfg')
    dotfiles = []

    if os.path.isfile(cfg_file):
        vprint('Found setup.cfg', verbose)
        try:
            with open(cfg_file) as f:
                dotfiles = f.readlines()
            vprint('Read setup.cfg', verbose)
        except:
            raise EnvironmentError('could not read %s' % cfg_file)

        dotfiles = [d.strip() for d in dotfiles]
    else:
        dotfiles = [f for f in os.listdir(dotarchive)]

    vprint('Dotfiles are: %s' % ' '.join(dotfiles), verbose)

    return dotfiles


def main():
    """
    Parse arguments.

    Call get_dot_files_list()

    Call make_symlinks()
    """
    # import os
    # dothome = os.path.expanduser('~')
    # dotarchive = os.path.join(dothome, '.dotarchive')

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("dothome",
                        help="absolute path to the dotfiles")
    parser.add_argument("dotarchive",
                        help="absolute path to the dotfile archive")
    parser.add_argument("--verbose", default=False,
                        help="verbose mode", action="store_true")
    args = parser.parse_args()

    dotfiles = get_dotfiles_list(args.dotarchive, verbose=args.verbose)

    make_symlinks(args.dothome, args.dotarchive, dotfiles,
                  verbose=args.verbose)

if __name__ == "__main__":
    main()
