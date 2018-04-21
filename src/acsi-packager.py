import argparse
import logging
import shutil
import sys
import tempfile
from os import makedirs, path, remove

from src import utils


def main(installdir=None, debug=False):
    # attempt to the path via the get_install_dir function if not supplied manually
    ac_install_dir = installdir if installdir else utils.get_install_dir()
    logger.info('Using AC installation path: %s', ac_install_dir)

    # let's check if ac_install_dir exists and check for AssettoCorsa.exe
    if not (path.isdir(ac_install_dir) and path.isfile(path.join(ac_install_dir, 'AssettoCorsa.exe'))):
        raise RuntimeError('Assetto Corsa installation not found!')

    # collect metadata about installed cars
    utils.scan_ui_files(ac_install_dir, tempdir)

    # scan binary files (graphics, car data, etc.) and copy them to be gzipped later
    utils.scan_binary_files(ac_install_dir, tempdir)

    # finally, gzip the tempdir and output the gzipped file to the basedir
    utils.gzip_tempdir(tempdir, basedir)

    # remove logfile if everything went smooth
    if not debug:
        try:
            f_handler.close()
            logger.removeHandler(f_handler)
            remove(logfile)
        except OSError:
            logging.error('Removal of \'acsi-packager.log\' failed. You might want to delete it manually.')

    # leave the window open to show the user what happened
    print('Done. Press Enter or simply close this window.')

    input()


if __name__ == '__main__':
    # temporary dir to store compiled JSON and binary data
    if getattr(sys, 'frozen', False):
        tempdir = path.join(sys._MEIPASS, 'acsi-packager-temp')
        makedirs(tempdir, exist_ok=True)
    else:
        tempdir = tempfile.mkdtemp(prefix='acsi-packager-')

    basedir = path.dirname(sys.argv[0])

    # console handler logs at INFO level
    c_formatter = logging.Formatter('%(levelname)s: %(message)s')
    c_handler = logging.StreamHandler()
    c_handler.setFormatter(c_formatter)
    c_handler.setLevel(logging.INFO)

    # file handler logs at DEBUG level
    logfile = path.join(basedir, 'acsi-packager.log')
    f_formatter = logging.Formatter('%(relativeCreated)05d; %(funcName)s; %(levelname)s; %(message)s')
    f_handler = logging.FileHandler(logfile, mode='w')
    f_handler.setFormatter(f_formatter)
    f_handler.setLevel(logging.DEBUG)

    # add both handlers to logger
    logger = logging.getLogger()
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logging.DEBUG)

    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('installdir', help='Assetto Corsa directory', nargs='?')
    parser.add_argument('--debug', help='keep log output', action='store_true')
    args = parser.parse_args()

    logging.debug('Using tempdir: %s', tempdir)

    # whatever happens, remove the tempdir afterwards
    try:
        main(args.installdir, args.debug)

    except Exception as e:
        logging.error('%s', str(e))
        logging.info('Please report this bug and include the \'acsi-packager.log\' file. Thank you.')
        logging.info('Press Enter or simply close this window.')
        input()

    finally:
        shutil.rmtree(tempdir)
