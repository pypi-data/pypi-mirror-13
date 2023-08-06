from __future__ import unicode_literals

import glob
import os
import shutil
import subprocess
import time


def prerequisites_ok():
    if os.path.exists('metadata.txt'):
        if 'qgisMinimumVersion' in open('metadata.txt').read():
            return True


def create_zipfile(context):
    """This is the actual zest.releaser entry point

    Relevant items in the context dict:

    name
        Name of the project being released

    tagdir
        Directory where the tag checkout is placed (*if* a tag
        checkout has been made)

    version
        Version we're releasing

    workingdir
        Original working directory

    """
    if not prerequisites_ok():
        return
    # Create a zipfile.
    subprocess.call(['make', 'zip'])
    for zipfile in glob.glob('*.zip'):
        first_part = zipfile.split('.')[0]
        new_name = "%s.%s.zip" % (first_part, context['version'])
        target = os.path.join(context['workingdir'], new_name)
        shutil.copy(zipfile, target)
        print("Copied %s to %s" % (zipfile, target))


def fix_version(context):
    """Fix the version in metadata.txt

    Relevant context dict item for both prerelease and postrelease:
    ``new_version``.

    """
    if not prerequisites_ok():
        return
    lines = open('metadata.txt', 'rU').readlines()
    for index, line in enumerate(lines):
        if line.startswith('version'):
            new_line = 'version=%s\n' % context['new_version']
            lines[index] = new_line
    time.sleep(1)
    open('metadata.txt', 'w').writelines(lines)
