#!/usr/bin/env python3
"""
Main console script. Call with '-h' argument for help.
"""

import argparse
import logging
import sched
import time
from datetime import datetime, timedelta

import pytz
from pathlib import Path

from earthpic.himawari8 import EarthPhoto
from earthpic.utils import (
    set_wallpaper,
    scheduled_downloading,
    info_console_handler,
    debug_console_handler,
)

logger = logging.getLogger(__name__)

start_time = datetime.now(pytz.utc) - timedelta(minutes=20)
default_date = start_time.strftime('%Y-%m-%d')
default_time = start_time.strftime('%H:%M')

parser = argparse.ArgumentParser(
    prog='earthpic',
    description='Download satelite Earth photo(s)',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    '-d',
    '--date',
    metavar='DATE',
    default=default_date,
    help='date of the photo [format: YYYY-MM-DD]',
)
parser.add_argument(
    '-t',
    '--time',
    metavar='TIME',
    default=default_time,
    help='time of the photo [fotmat: hh:mm]',
)
parser.add_argument(
    '-s',
    '--scale',
    type=int,
    metavar='SCALE',
    choices=(1, 2, 4, 8, 16, 20),
    default=2,
    help='scale of the photo, choices: 1, 2, 4, 8, 16 or 20'
)
parser.add_argument(
    '-w',
    '--wallpaper',
    help='set downloaded image as desktop wallpaper',
    action='store_true',
)
parser.add_argument(
    '-v',
    '--verbose',
    help='increase output verbosity',
    action='store_true',
)
parser.add_argument(
    '--debug',
    action='store_true',
    help=argparse.SUPPRESS,
)
parser.add_argument(
    '-l',
    '--last',
    type=int,
    metavar='N_PHOTOS',
    default=1,
    help='process N photos to given date'
)
parser.add_argument(
    '-b',
    '--batch',
    help='run batch downloading photos. To stop, press ctrl+c.',
    action='store_true',
)
default_path = str(Path('.') / 'images')
parser.add_argument(
    '-p',
    '--path',
    metavar='PATH',
    default=default_path,
    help='path where images will be saved',
)


def main():
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().addHandler(debug_console_handler)
    elif args.verbose:
        logging.getLogger().addHandler(info_console_handler)

    logger.debug(args)

    # Downloading big images needs confirmation
    if args.scale > 4:
        answer = input(
            'Are you sure you want to download photo of that size '
            '({0}x{0}={1} tiles)?'.format(args.scale, args.scale ** 2) +
            ' [Y/n] '
        )
        if answer.lower() in ('n', 'no'):
            return

    earth_photo = EarthPhoto(args.scale, args.path)

    date_string = '{} {}'.format(args.date, args.time)
    date = datetime.strptime(date_string, '%Y-%m-%d %H:%M')
    date = pytz.utc.localize(date)
    if date > start_time:
        date = start_time

    logger.debug('      date: {}'.format(date))
    logger.debug('start_date: {}'.format(start_time))

    if args.batch:
        if args.last > 1:
            print("Don't use batch option when defining '--last N' option")
            return
        scheduler = sched.scheduler(time.time, time.sleep)
        scheduler.enter(
            0,  # 0s ie. instant execution
            1,
            scheduled_downloading,
            (earth_photo, date, args.wallpaper, scheduler),
        )
        try:
            scheduler.run()
        except KeyboardInterrupt:
            return

    for delta in range(args.last-1, -1, -1):
        image_path = earth_photo.download(date - timedelta(minutes=10 * delta))
        logger.debug('image_path: {}'.format(image_path))
        if args.wallpaper and image_path:
            set_wallpaper(image_path)


if __name__ == "__main__":
    main()
