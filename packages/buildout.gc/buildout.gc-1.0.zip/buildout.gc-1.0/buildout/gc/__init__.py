from __future__ import print_function
import os
import logging
import zc.buildout.easy_install
from zc.buildout import bool_option
import shutil
import sys


logger=zc.buildout.easy_install.logger


def enable_eggs_cleaner(old_get_dist):
    """Patching method so we can go keep track of all the used eggs"""
    def get_dist(self, *kargs, **kwargs):
        dists = old_get_dist(self, *kargs, **kwargs)
        for dist in dists:
            p = os.path.normpath(dist.location)
            if sys.platform == 'win32':
               p = p.lower()
            self.__used_eggs[dist.egg_name()] = p
        return dists
    return get_dist


def delete_path(path):
    try:
        if os.path.isfile(path) or os.path.islink(path):
           os.remove(path)
        else:
           shutil.rmtree(path)
    except (OSError, IOError) as e:
        print("Can't remove path %s: %s" % (path, e))

def eggs_cleaner(old_logging_shutdown, eggs_directory, old_eggs_directory, remove_eggs, factor, extensions):
    # Patching method so we can report and/or move eggs when buildout shuts down

    def logging_shutdown():
        # Set some easy to use variables
        used_eggs = set(zc.buildout.easy_install.Installer.__used_eggs.values())
        eggsdirectory = os.listdir(eggs_directory)
        move_eggs = []

        # Loop through the contents of the eggs directory
        # Determine which eggs aren't used..
        # ignore any which seem to be buildout  extensions
        for eggname in eggsdirectory:
            fullpath = os.path.normpath(os.path.join(eggs_directory, eggname))
            if sys.platform == 'win32':
               fullpath = fullpath.lower()
            if fullpath not in used_eggs:
                is_extensions = False
                for ext in extensions:
                    if ext in eggname:
                        is_extensions = True
                        break
                if not is_extensions:
                    move_eggs.append(eggname)

        if len(move_eggs) > len(eggsdirectory) * factor:
            print("*** To many eggs for delete. Possible buildout failed **")
            print(" ".join(move_eggs))
            move_eggs = []

        # Move or not?
        if old_eggs_directory:
            if not os.path.exists(old_eggs_directory):
                # Create if needed
                os.mkdir(old_eggs_directory)
            for eggname in move_eggs:
                oldpath = os.path.join(eggs_directory, eggname)
                newpath = os.path.join(old_eggs_directory, eggname)
                if remove_eggs:
                    delete_path(oldpath)
                else:
                    if not os.path.exists(newpath):
                        shutil.move(oldpath, newpath)
                    else:
                        delete_path(oldpath)
                print("Moved unused egg: %s " % eggname)
        else:  # Only report
            print("Don't have a 'old-eggs-directory' set, only reporting")
            print("Can add it by adding 'old-eggs-directory = ${buildout:directory}/old-eggs' to your [buildout]")
            for eggname in move_eggs:
                print("Found unused egg: %s " % eggname)

        old_logging_shutdown()
    return logging_shutdown


def install(buildout):
    # Fetch the eggs-directory from the buildout
    eggs_directory = 'eggs-directory' in buildout['buildout'] and buildout['buildout']['eggs-directory'].strip() or None

    # Fetch our old-eggs-directory
    old_eggs_directory = buildout['buildout'].get('old-eggs-directory', '').strip()
    remove_eggs = bool_option(buildout['buildout'], 'old-eggs-remove', False)
    factor = buildout['buildout'].get('old-eggs-factor', '0.5').strip()
    try:
        factor = float(factor)
    except ValueError:
        raise zc.buildout.UserError('Value of factor should be float')

    # Get a list of extensions. There is no fancier way to ensure they don't get included.
    extensions = buildout['buildout'].get('extensions', '').split()
    extensions.append('zc.buildout')

    # Patch methods
    zc.buildout.easy_install.Installer.__used_eggs = {}
    zc.buildout.easy_install.Installer._get_dist = enable_eggs_cleaner(zc.buildout.easy_install.Installer._get_dist)
    logging.shutdown = eggs_cleaner(logging.shutdown, eggs_directory,
                                    old_eggs_directory, remove_eggs, factor, extensions)
