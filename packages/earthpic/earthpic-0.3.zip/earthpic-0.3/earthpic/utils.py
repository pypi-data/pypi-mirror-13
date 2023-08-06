#!/usr/bin/env python3
"""
Useful utilities
"""

import ctypes
import logging
from datetime import datetime, timedelta
from pathlib import Path

import pytz
from PIL import Image

from .constants import CWD, SPIF_UPDATEINIFILE, SPI_SETDESKWALLPAPER

# logging object:
logger = logging.getLogger(__name__)

# create console handlers and set levels
info_console_handler = logging.StreamHandler()
info_console_handler.setLevel(logging.INFO)
debug_console_handler = logging.StreamHandler()
debug_console_handler.setLevel(logging.DEBUG)

# create formatters
formatter = logging.Formatter('%(levelname)s: %(message)s')
formatter2 = logging.Formatter('%(name)18s: (%(levelname)s) %(message)s')

# add formatters
info_console_handler.setFormatter(formatter)
debug_console_handler.setFormatter(formatter2)


def round_time(dtime=None, round_to=600):
    """Floor round a datetime object to any time laps in seconds.
    If not specified, treats datetime object as in UTC timezone.
    @param dtime: datetime object or None. If None, returns rounded current time
    @param round_to: time laps in seconds (default: 600s = 10min)
    """

    tz = pytz.utc
    logger.debug('In round_time (dtime 1): {}'.format(dtime))
    if dtime is None:
        dtime = datetime.now(tz)
    logger.debug('In round_time (dtime 2): {}'.format(dtime))
    if not dtime.tzinfo:
        dtime = tz.localize(dtime)
    logger.debug('In round_time (dtime 3): {}'.format(dtime))
    seconds = (dtime - datetime(1970, 1, 1, tzinfo=tz)).seconds
    rounding = (seconds // round_to) * round_to
    logger.debug('seconds: {} rounding: {}'.format(seconds, rounding))
    dtime = dtime + timedelta(0, rounding - seconds, -dtime.microsecond)
    logger.debug('In round_time (dtime 4): {}'.format(dtime))
    return dtime


def set_wallpaper(file_path):
    """
    Set any graphic file as Windows desktop wallpaper. Internally converts to,
    and saves as 'wallpaper.bmp' file localized in 'bin' directory.
    @param file_path: string or pathlib.Path() object
    """

    temp_file = str(Path(CWD).parent / 'bin' / 'wallpaper.bmp')
    im = Image.open(str(file_path))
    im.save(temp_file)
    logger.info('Setting wallpaper: {}'.format(temp_file))
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        temp_file,
        SPIF_UPDATEINIFILE,
    )


def scheduled_downloading(earth_photo, date, make_wallpaper, scheduler):
    """
    Allows to run infinite loop that downloads file every 10 minutes
    @param earth_photo: instance of EarthPhoto
    @param date: datetime object
    @param make_wallpaper: Boolean. If true - sets image as desktop wallpaper
    @param scheduler: sched.scheduler object, to which next event is added
    """
    logger.info('downloading photo from {}'.format(date))
    pic = earth_photo.download(date)
    if pic and make_wallpaper:
        set_wallpaper(pic)
    date += timedelta(seconds=600)
    logger.info(
        'Next photo will be downloaded after 10 minutes. ({})'.format(date))
    scheduler.enter(
        600,  # 10 minutes
        1,  # priority
        scheduled_downloading,
        (earth_photo, date, make_wallpaper, scheduler),
    )
