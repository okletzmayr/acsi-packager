import json
import logging
import shutil
import tarfile
import winreg
from os import listdir, makedirs, path, walk

import vdf

logger = logging.getLogger('main')


def fix_track_length(orig_length):
    # tl = track length. here we remove spaces from the input
    tl = orig_length.replace(' ', '')

    # if we got km, make sure the separator is a dot and multiply by 1000
    if tl.endswith('km'):
        tl = tl.replace(',', '.')
        tl = float(tl[:-2]) * 1000

    # if we got m, remove the thousands separator. (it's unlikely a track is described as e.g. 1400.3m long)
    elif tl.endswith('m'):
        tl = tl.replace(',', '').replace('.', '')
        tl = float(tl[:-1])

    # if we don't have a unit, just convert it to float
    else:
        # float() needs a dot separator, not a comma
        tl = tl.replace(',', '.')
        tl = float(tl)

    # if the track length is really short, we're probably dealing with km. so let's multiply by 1000
    if tl <= 100:
        tl *= 1000

    return tl


def get_steamapps_dir():
    path64 = r'SOFTWARE\WOW6432Node\Valve\Steam'
    path32 = r'SOFTWARE\Valve\Steam'

    try:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path64)
        except FileNotFoundError:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path32)

        steamapps = path.join(winreg.QueryValueEx(key, 'InstallPath')[0], 'steamapps')
        if path.isdir(steamapps):
            return steamapps
        else:
            raise NotADirectoryError('Steam installation registry entry found, but steamapps is empty.')
    except FileNotFoundError:
        raise RuntimeError('Steam installation not found!')


def get_install_dir():
    # there's one steam library we know exists: the one we found in the registry.
    steamapps = [get_steamapps_dir()]

    # steam keeps track of multiple libraries via this file
    fp = open(path.join(steamapps[0], 'libraryfolders.vdf'))
    library_dict = vdf.load(fp)

    # and numbers the libraries from 1 to however many libraries the user has.
    # here we assume that no sane person has more than 16 steam libraries.
    for i in range(1, 16):
        try:
            f = library_dict['LibraryFolders'][str(i)]
            steamapps.append(path.join(f, 'steamapps'))
        except KeyError:
            break

    # next we loop over every library, and check if there's an appmanifest for assetto corsa.
    for library in steamapps:
        if 'appmanifest_244210.acf' in listdir(library):
            return path.join(library, 'common', 'assettocorsa')
        else:
            return None


def read_ui_file(fp):
    # files should be in utf8
    try:
        with open(fp, encoding='utf-8') as f:
            info = json.load(f, strict=False)

    # if json complains, it might be BOM encoded
    except json.JSONDecodeError:
        with open(fp, encoding='utf-8-sig') as f:
            info = json.load(f, strict=False)

    # if unicode throws a fit it might be windows-1252
    except UnicodeDecodeError:
        with open(fp, encoding='windows-1252') as f:
            info = json.load(f, strict=False)

    return info


def scan_ui_files(ac_install_dir, output_dir):
    cars_dir = path.join(ac_install_dir, 'content', 'cars')
    tracks_dir = path.join(ac_install_dir, 'content', 'tracks')
    data = {'cars': {},
            'tracks': {}}

    # scan every car in AC/content/cars
    logger.debug('Scanning for cars')
    for car in listdir(cars_dir):
        fp = path.join(path.join(cars_dir, car, 'ui', 'ui_car.json'))
        info = read_ui_file(fp)
        brand = info['brand']

        if brand not in data['cars']:
            data['cars'][brand] = {}

        data['cars'][brand][car] = {'name': info['name']}

        logger.debug('car: "{}" ({})'.format(info['name'], car))

    # scan every track in AC/content/tracks
    logger.debug('Scanning for tracks')
    for track in listdir(tracks_dir):
        fp = path.join(path.join(tracks_dir, track, 'ui', 'ui_track.json'))

        # if there's a toplevel ui_track.json, it's a single-layout track
        if path.exists(fp):
            info = read_ui_file(fp)
            tl = fix_track_length(info['length'])
            data['tracks'][track] = {'name': info['name'], 'length': tl}
            logger.debug('track: "%s" (%s) - %dm', info['name'], track, tl)

        # if there are more, we have to scan each layout
        else:
            data['tracks'][track] = {'layouts': {}}

            for layout in listdir(path.join(tracks_dir, track, 'ui')):
                # only scan directories, ignore clutter like Thumbs.db
                # if path.isdir(path.join(tracks_dir, track, 'ui', layout)):
                fp = path.join(tracks_dir, track, 'ui', layout, 'ui_track.json')

                if path.isfile(fp):
                    info = read_ui_file(fp)
                    tl = fix_track_length(info['length'])
                    data['tracks'][track]['layouts'][layout] = {'name': info['name'], 'length': tl}
                    logger.debug('track: "%s" (%s/%s) - %dm', info['name'], track, layout, tl)

    car_count = 0
    for brand in data['cars']:
        car_count += len(brand)

    logger.info('Parsed data of %d cars by %s brands and %d tracks.',
                car_count, len(data['cars']), len(data['tracks']))

    with open(path.join(output_dir, 'content.json'), 'w') as fp:
        json.dump(data, fp)


def gzip_tempdir(tempdir, output_dir):
    # this is a mess, so I better write this comment right now:
    # tarfile.add() needs the arcname parameter if we don't want the full path structure in the tarfile,
    # so I'm using os.walk() to loop over each file, and create a relative pathname which is used as arcname
    logger.info('Starting gzipping process. This could take a while, depending on amount of installed content.')
    fp = path.join(output_dir, 'acsi-package.tar.gz')
    tar = tarfile.open(fp, 'w:gz')

    # keep track of compression ratio
    size_prezip = 0

    for root, dirs, files in walk(tempdir):
        for filename in files:
            full_path = path.join(root, filename)
            rel_path = path.relpath(full_path, tempdir)

            size_prezip += path.getsize(full_path)

            tar.add(path.join(tempdir, rel_path), arcname=rel_path)

    tar.close()
    size_postzip = path.getsize(fp)
    logger.info('Compressed %.1f MB of data to %.1f MB. (ratio: %.1f%%)',
                size_prezip / pow(1024, 2), size_postzip / pow(1024, 2), (size_postzip / size_prezip) * 100)


def scan_binary_files(ac_install_dir, dest):
    logger.info('Started copying binary files')
    cars_dir = path.join(ac_install_dir, 'content', 'cars')
    tracks_dir = path.join(ac_install_dir, 'content', 'tracks')

    for root, dirs, files in walk(cars_dir):
        for filename in files:
            full_path = path.join(root, filename)
            rel_path = path.relpath(full_path, cars_dir)
            dest_path = path.join(dest, 'cars', rel_path)

            if filename == 'data.acd':
                makedirs(path.dirname(dest_path), exist_ok=True)
                shutil.copy(full_path, dest_path)

    for root, dirs, files in walk(tracks_dir):
        for filename in files:
            full_path = path.join(root, filename)
            rel_path = path.relpath(full_path, tracks_dir)
            dest_path = path.join(dest, 'tracks', rel_path)

            if filename in ['surfaces.ini', 'preview.png', 'map.png']:
                makedirs(path.dirname(dest_path), exist_ok=True)
                shutil.copy(full_path, dest_path)
