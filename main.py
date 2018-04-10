import logging
from os import listdir, path
from sys import stdout

from utils import get_ac_install_dir, read_ui_file

logging.basicConfig(stream=stdout, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('main')


def main():
    logger.debug('Searching the Assetto Corsa installation directory')
    ac_install_dir = get_ac_install_dir()
    logger.debug('Detected installation: %s', ac_install_dir)

    cars_dir = path.join(ac_install_dir, 'content', 'cars')
    tracks_dir = path.join(ac_install_dir, 'content', 'tracks')

    logger.debug('Scanning for cars')
    # scan every car in AC/content/cars
    for car in listdir(cars_dir):
        fp = path.join(path.join(cars_dir, car, 'ui', 'ui_car.json'))
        info = read_ui_file(fp)

        logger.debug('\t"{}" ({})'.format(info['name'], car))

    logger.debug('Scanning for tracks')
    # scan every track in AC/content/tracks
    for track in listdir(tracks_dir):
        fp = path.join(path.join(tracks_dir, track, 'ui', 'ui_track.json'))
        track_config = ''

        # if there's a toplevel ui_track.json, it's a single-layout track
        if path.exists(fp):
            info = read_ui_file(fp)

        # if there are more, we have to scan each layout
        # TODO: handle case when info is not defined
        else:
            for track_config in listdir(path.join(tracks_dir, track, 'ui')):
                if path.isdir(path.join(tracks_dir, track, 'ui', track_config)):
                    fp = path.join(tracks_dir, track, 'ui', track_config, 'ui_track.json')
                    info = read_ui_file(fp)

        # format data
        # TODO: use this in the loop for each layout!
        track_name = track + '/' + track_config if track_config != '' else track
        tl = info['length'].replace(' ', '')
        if tl.endswith('km'):
            tl = tl.replace(',', '.')
            tl = float(tl[:-2])*1000
        elif tl.endswith('m'):
            tl = tl.replace('.', '')
            tl = float(tl[:-1])
        else:
            tl = float(tl)

        # sometimes there's a dot, and 'km' is missing, so in that case multiply e.g. '6.3' * 1000 to get 6300
        if tl < 20:
            tl *= 1000

        logger.debug('\t"{}" ({}) {:.0f}m'.format(info['name'], track_name, tl))

    return 0


if __name__ == '__main__':
    main()
