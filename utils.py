import json
import logging
import winreg
from os import path

logger = logging.getLogger('main')


def fix_track_length(orig_length):
    # tl = track length. here we remove spaces from the input
    tl = orig_length.replace(' ', '')

    # if we got km, make sure the separator is a dot and multiply by 1000
    if tl.endswith('km'):
        tl = tl.replace(',', '.')
        tl = float(tl[:-2])*1000

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


def get_ac_install_dir():
    kname = ['HKEY_CURRENT_USER/Software/Valve/Steam/SteamPath',
             'HKEY_LOCAL_MACHINE/Software/Wow6432Node/Microsoft/Windows/CurrentVersion/Uninstall/Steam App 244210',
             'HKEY_LOCAL_MACHINE/Software/Microsoft/Windows/CurrentVersion/Uninstall/Steam App 244210']
    ac_dir = None

    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam')
        v = winreg.QueryValueEx(k, 'SteamPath')
        res = path.join(v[0], 'SteamApps', 'common', 'assettocorsa')
        if path.isdir(res) and path.isfile(path.join(res, 'AssettoCorsa.exe')):
            logger.debug('Found using %s', kname[0])
            ac_dir = res
        else:
            logger.error('Not found using %s', kname[0])
    except Exception as e:
        logger.error('Could not query %s: %s', kname[0], str(e))

    if ac_dir is None:
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r'SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244210')
            res = winreg.QueryValueEx(k, 'InstallLocation')[0]
            if path.isdir(res) and path.isfile(path.join(res, 'AssettoCorsa.exe')):
                logger.error('Found using %s', kname[1])
                ac_dir = res
            else:
                logger.error('Not found using %s', kname[1])
        except Exception as e:
            logger.error('Could not query %s: %s', kname[1], str(e))

    if ac_dir is None:
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244210')
            res = winreg.QueryValueEx(k, 'InstallLocation')[0]
            if path.isdir(res) and path.isfile(path.join(res, 'AssettoCorsa.exe')):
                logger.error('Found using %s', kname[2])
                ac_dir = res
            else:
                logger.error('Not found using %s', kname[2])
        except Exception as e:
            logger.error('Could not query %s: %s', kname[2], str(e))

    if ac_dir is not None:
        return ac_dir
    else:
        raise RuntimeError('AC Installation not found!')


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
