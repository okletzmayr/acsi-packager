import argparse
import json
import logging
import sys
import tempfile
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
    # temporary dir to store the JSON data and car/track preview images
    tempdir = tempfile.mkdtemp(prefix='acsi-packager-')
    basedir = path.dirname(sys.argv[0])

    # more verbose and file output when --debug flag is set
    if args.debug:
        fileHandler = logging.FileHandler(path.join(basedir, 'acsi-packager.log'), mode='w')
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

    # however we got the path, let's check if it exists and check for AssettoCorsa.exe
    if not path.isdir(ac_install_dir) or not path.isfile(path.join(ac_install_dir, 'AssettoCorsa.exe')):
        sys.exit('Assetto Corsa installation not found!')

    logging.info('using tempdir: %s', tempdir)

    # first, collect metadata about installed cars...
    data = utils.scan_ui_files(ac_install_dir)

    # and store them as a JSON.
    with open(path.join(tempdir, 'content.json'), 'w') as fp:
        json.dump(data, fp)

    # finally, gzip the tempdir and output the gzipped file to the basedir
    utils.gzip_tempdir(tempdir, basedir)

    return 0


if __name__ == '__main__':
    main()
