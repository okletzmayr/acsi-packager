import argparse
import logging
import sys
from os import listdir, path

import utils

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')

parser = argparse.ArgumentParser()
parser.add_argument('installdir', nargs='?', help='Assetto Corsa installation directory')
parser.add_argument('--debug', help='print debug output', action='store_true')

args = parser.parse_args()

if args.debug:
    logger.setLevel(logging.DEBUG)


def main():
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

    cars_dir = path.join(ac_install_dir, 'content', 'cars')
    tracks_dir = path.join(ac_install_dir, 'content', 'tracks')
    cars = 0
    tracks = 0

    logger.debug('Scanning for cars')
    # scan every car in AC/content/cars
    for car in listdir(cars_dir):
        fp = path.join(path.join(cars_dir, car, 'ui', 'ui_car.json'))
        info = utils.read_ui_file(fp)

        logger.debug('car: "{}" ({})'.format(info['name'], car))
        cars += 1

    logger.debug('Scanning for tracks')
    # scan every track in AC/content/tracks
    for track in listdir(tracks_dir):
        fp = path.join(path.join(tracks_dir, track, 'ui', 'ui_track.json'))

        # this way we can avoid code redundancy
        layouts = []

        # if there's a toplevel ui_track.json, it's a single-layout track
        if path.exists(fp):
            info = utils.read_ui_file(fp)
            tl = utils.fix_track_length(info['length'])
            layouts.append({'name': info['name'],
                            'path': track,
                            'length': tl})

        # if there are more, we have to scan each layout
        else:
            for track_config in listdir(path.join(tracks_dir, track, 'ui')):
                if path.isdir(path.join(tracks_dir, track, 'ui', track_config)):
                    fp = path.join(tracks_dir, track, 'ui', track_config, 'ui_track.json')
                    info = utils.read_ui_file(fp)
                    tp = track + '/' + track_config
                    tl = utils.fix_track_length(info['length'])
                    layouts.append({'name': info['name'],
                                    'path': tp,
                                    'length': tl})

        for l in layouts:
            logger.debug('track: "{}" ({}) {:.0f}m'.format(l['name'], l['path'], l['length']))
        tracks += 1

    logger.info('Found and parsed data of %d cars and %d tracks', cars, tracks)

    return 0


if __name__ == '__main__':
    main()
