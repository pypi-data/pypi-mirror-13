import argparse
import os
import logging
import shutil
import time
from glob import glob

from .microbit_path import get_default_microbit_path


logger = logging.getLogger(__name__)

HEX_GLOB = 'micropython*.hex'
SLEEP_TIME = 1


class ParamError(ValueError):
    pass


def get_default_download_path():
    home = os.path.expanduser('~')
    return os.path.join(home, 'Downloads')


def reflash_upon_new(download_path, microbit_path):
    if not microbit_path:
        raise ParamError("Need to set microbit_path")
    if not os.path.exists(download_path):
        raise ParamError("download_path {} doesn't exist".format(download_path))
    if not os.path.isdir(download_path):
        raise ParamError("download_path {} isn't a directory".format(download_path))
    logger.info("Looking for hex files in {}".format(download_path))

    previous_hex = None
    missing_hex_warn = True
    while True:
        all_hexes = glob(os.path.join(download_path, HEX_GLOB))
        hexes_missing = len(all_hexes) == 0
        if hexes_missing:
            if missing_hex_warn:
                logger.info("{} does not contain any hex files".format(download_path))
                missing_hex_warn = False
            previous_hex = None
        else:
            missing_hex_warn = True
            latest_hex_path = max(all_hexes, key=os.path.getctime)
            if latest_hex_path != previous_hex:
                logger.info(latest_hex_path)
                shutil.copy(latest_hex_path, microbit_path)
            previous_hex = latest_hex_path
        time.sleep(SLEEP_TIME)


def main():
    parser = argparse.ArgumentParser(
        description='A command to watch for new hex files from '
        'https://github.com/ntoll/upyed and flash the micro:bit immediately')

    parser.add_argument(
        '--download_path',
        type=str,
        default=get_default_download_path(),
        help='Filepath your browser stores downloads'
    )

    default_microbit_path = get_default_microbit_path()
    parser.add_argument(
        '--microbit_path',
        type=str,
        default=get_default_microbit_path(),
        help='Filepath your computer mounts the micro:bit'
    )

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.debug(args)

    if not args.microbit_path and not default_microbit_path:
        raise ParamError("No micro:bit path detected, did you plug it in?")

    reflash_upon_new(args.download_path, args.microbit_path)


if __name__ == '__main__':
    main()
