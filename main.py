import argparse
import logging
import sys
from os import path

import utils

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
    if args.debug:
        fileHandler = logging.FileHandler('acsi-packager.log', mode='w')
        fileHandler.setFormatter(logFormatter)
        logger.addHandler(fileHandler)
        logger.setLevel(logging.DEBUG)

    if args.installdir:
        ac_install_dir = args.installdir
        # check the installdir if the user supplied the path
        if not path.isdir(ac_install_dir) or not path.isfile(path.join(ac_install_dir, 'AssettoCorsa.exe')):
            sys.exit('Assetto Corsa installation not found!')

    # else use attempt to find it via the get_ac_install_dir function
    else:
        logger.info('No installation directory specified - searching for the AC installation directory')
        ac_install_dir = utils.get_ac_install_dir()
        logger.info('Detected installation: %s', ac_install_dir)

    utils.scan_ui_files(ac_install_dir)

    print('We\'re done here. Press Enter or close this window.')
    input()

    return 0


if __name__ == '__main__':
    main()
