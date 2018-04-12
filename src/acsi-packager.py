import argparse
import json
import logging
import os
import shutil
import sys
import tarfile
from os import path

from src import utils

logFormatter = logging.Formatter('%(levelname)-5s - %(message)s')
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger = logging.getLogger()
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('installdir', help='Assetto Corsa directory', nargs='?')
parser.add_argument('--debug', help='log debug output', action='store_true')
args = parser.parse_args()


def main():
    # more verbose and file output when --debug flag is set
    if args.debug:
        fileHandler = logging.FileHandler('acsi-packager.log', mode='w')
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)
        logger.setLevel(logging.DEBUG)

    # set the installdir if the user supplied the path
    if args.installdir:
        ac_install_dir = args.installdir

    # else attempt to find it via the get_install_dir function
    else:
        logger.info('No installation directory specified - searching for the AC installation directory')
        ac_install_dir = utils.get_install_dir()
        logger.info('Detected installation: %s', ac_install_dir)

    if not path.isdir(ac_install_dir) or not path.isfile(path.join(ac_install_dir, 'AssettoCorsa.exe')):
        sys.exit('Assetto Corsa installation not found!')

    # temporary dir to store the JSON data and car/track preview images
    tempdir = path.join(path.dirname(__file__), 'package')
    if not path.isdir(tempdir):
        os.mkdir(tempdir)

    with open(path.join(tempdir, 'content.json'), 'w') as fp:
        data = utils.scan_ui_files(ac_install_dir)
        json.dump(data, fp)

    # this is a mess, so I better write this comment right now:
    # tarfile.add() needs the arcname parameter if we don't want the full path structure in the tarfile,
    # so I'm using os.walk() to loop over each file, and create a relative pathname which is used as arcname
    tar = tarfile.open('acsi-package.tar.gz', 'w:gz')

    for root, dirs, files in os.walk(tempdir):
        for filename in files:
            rel_path = path.relpath(path.join(root, filename), tempdir)
            tar.add(path.join(tempdir, rel_path), arcname=rel_path)

    tar.close()
    shutil.rmtree(tempdir)

    return 0


if __name__ == '__main__':
    main()
