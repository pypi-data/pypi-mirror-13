#!/usr/bin/env python3
"""
Main module that downloads satelite photographs from http://himawari8.nict.go.jp
"""

import itertools
import logging
import shutil
from datetime import timedelta
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image

from .constants import CWD
from .utils import round_time

logger = logging.getLogger(__name__)


class EarthPhoto:
    """Main class representing configuration and values needed to download
    photos from japan site.

    @param scale: zoom level of photo. The higher the bigger photo is downloaded

    @param storage_path: (type: string) path to folder where files should be
                         written. Default: '%package_folder%/images'
    """

    url_pattern = (
        'http://himawari8.nict.go.jp/img/D531106/{scale}d/550/'
        '{year}/{month:02}/{day:02}/{hour:02}{min:02}00_{x}_{y}.png'
        )
    filename_pattern = (
        'earth_{year}-{month:02}-{day:02}_{hour:02}-{min:02}_{size}.png'
        )
    tile_size = 550
    sizes = {
        1: 'xs',
        2: 'small',
        4: 'big',
        8: 'large',
        16: 'xl',
        20: 'xxl',
        }
    delay = 20  # in minutes

    def __init__(self, scale=2, storage_path=None):
        if storage_path:
            self._images_path = Path(storage_path)
        else:
            self._images_path = Path.cwd() / 'images'
        self._blank_image_path = Path(CWD).parent / 'bin' / 'blank_image.png'
        self._prepare_files()
        self._blank_image = Image.open(self._blank_image_path)
        self._session = requests.Session()
        self.scale = scale
        self.time = round_time() - timedelta(minutes=self.delay)

    @property
    def scale(self):
        """Integer representing zoom scale"""
        return self._scale

    @scale.setter
    def scale(self, scale):
        try:
            self.sizes[scale]
        except KeyError:
            raise ValueError('Scale must be an integer: 1, 2, 4, 8, 16 or 20')
        self._scale = scale

    @property
    def time(self):
        """datetime.datetime object, rounded to whole ten-minutes"""
        return self._time

    @time.setter
    def time(self, value):
        self._time = round_time(value)

    def _prepare_files(self):
        """Creates folder for images and blank file - if not already exist"""
        if not self._images_path.exists():
            Path.mkdir(self._images_path)

        if not self._blank_image_path.exists():
            Path.mkdir(self._blank_image_path.parent)
            self._create_blank_image()

    def _create_blank_image(self):
        """Needed to determine later if photo exists on server"""

        # Attempt of downloading photo from near future returns blank image
        near_future = round_time() + timedelta(hours=1)
        url = self._get_url(near_future, scale=1)
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(str(self._blank_image_path), 'wb') as fout:
                shutil.copyfileobj(response.raw, fout)
        del response

    def download(self, time=None):
        """
        Downloads one photo from given time. If time not specified, downloads
        photo from moment when object was instantiated (minus 20 minutes).
        @param time: detetime object or None object
        @return: string with path to downloaded file
        """
        if time:
            self.time = time

        file_path = self._get_file_path()
        if file_path.exists():
            logger.info('Image already downloaded')
            return str(file_path)

        return self._fetch_and_save_image(file_path)

    def _fetch_and_save_image(self, file_path):
        """
        @param file_path: pathlib.Path() object
        @return: file path as string
        """
        png_image = Image.new(
            'RGB',
            (self.tile_size * self.scale, self.tile_size * self.scale),
        )

        # Photographs on server are storaged as tiles of size scale*scale
        for x, y in itertools.product(range(self.scale), range(self.scale)):
            tile_data = self._download_tile(x, y)
            tile = Image.open(BytesIO(tile_data))
            if tile == self._blank_image:
                print('No Earth image at given time. File not saved.')
                return
            png_image.paste(tile, (self.tile_size * x, self.tile_size * y))

        png_image.save(str(file_path), 'PNG')
        logger.info('Image saved as: {}'.format(file_path))
        return str(file_path)

    def _download_tile(self, x, y):
        url = self._get_url(x=x, y=y)
        logger.info("Fetching tile: {}...{}".format(url[:28], url[-26:]))
        try:
            return self._session.get(url).content
        except requests.ConnectionError:
            logger.info('Connection Error. Retrying.')
            return self._download_tile(x, y)

    def _params(self, time=None, scale=None):
        time = time if time else self.time
        scale = scale if scale else self.scale
        return dict(
            scale=scale,
            year=time.year,
            month=time.month,
            day=time.day,
            hour=time.hour,
            min=time.minute,
        )

    def _get_url(self, time=None, scale=None, x=0, y=0):
        return self.url_pattern.format(
            x=x,
            y=y,
            **self._params(time, scale)
        )

    def _get_file_path(self):
        return self._images_path / self.filename_pattern.format(
            size=self.sizes[self.scale],
            **self._params()
        )
