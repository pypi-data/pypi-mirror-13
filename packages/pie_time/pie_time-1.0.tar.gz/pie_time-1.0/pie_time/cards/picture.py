# -*- coding: utf-8 -*-
# Copyright (c) 2014-2016 Tomek Wójcik <tomek@bthlabs.pl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
pie_time.cards.picture
======================

This module containse the PictureCard class.
"""

import cStringIO
import os
import urlparse

import pygame
import requests

from pie_time.card import AbstractCard


class PictureCard(AbstractCard):
    """
    The picture card.

    This cards displays a picture from list of pre-defined pictures. If more
    than one picture is defined, it's changed each time the card transitions
    to current card.

    **Settings dictionary keys**:

    * **urls** (*list*) - **required** list of picture URLs. Currently, only
      ``file://``, ``http://`` and ``https://`` URL schemes are supported.
    """

    def initialize(self):
        self._pictures = []
        self._current_picture_idx = None
        self._should_redraw = True

        for url in self._settings['urls']:
            self._pictures.append(self._load_picture(url))

    def _load_picture(self, url):
        self._app.logger.debug(
            'PictureCard: Attempting to load picture: %s' % url
        )

        parsed_url = urlparse.urlparse(url)

        surface = None
        try:
            format = None
            if parsed_url.scheme == 'file':
                surface = pygame.image.load(parsed_url.path)

                _, ext = os.path.splitext(parsed_url.path)
                format = ext.lower()
            elif parsed_url.scheme.startswith('http'):
                rsp = requests.get(url)
                assert rsp.status_code == 200

                format = rsp.headers['Content-Type'].replace('image/', '')

                surface = pygame.image.load(
                    cStringIO.StringIO(rsp.content), 'picture.%s' % format
                )

            if surface and format:
                if format.lower().endswith('png'):
                    surface = surface.convert_alpha(self._app.screen)
                else:
                    surface = surface.convert(self._app.screen)
        except Exception as exc:
            self._app.logger.error(
                'PictureCard: Could not load picture: %s' % url, exc_info=True
            )

        return surface

    def show(self):
        if len(self._pictures) == 0:
            self._current_picture_idx = None
        elif len(self._pictures) == 1:
            self._current_picture_idx = 0
        else:
            if self._current_picture_idx is None:
                self._current_picture_idx = 0
            else:
                new_picture_idx = self._current_picture_idx + 1
                if new_picture_idx >= len(self._pictures):
                    new_picture_idx = 0

                self._app.logger.debug(
                    'PictureCard: Picture transition %d -> %d' % (
                        self._current_picture_idx, new_picture_idx
                    )
                )

                self._current_picture_idx = new_picture_idx

        self._should_redraw = True

    def tick(self):
        if self._should_redraw:
            self.surface.fill(self.background_color)

            if self._current_picture_idx is not None:
                picture = self._pictures[self._current_picture_idx]
                picture_size = picture.get_size()

                picture_rect = picture.get_rect()
                if picture_size != self._app.screen_size:
                    picture_rect = (
                        (self.width - picture_size[0]) / 2.0,
                        (self.height - picture_size[1]) / 2.0,
                        picture_size[0], picture_size[1]
                    )

                self.surface.blit(picture, picture_rect)

            self._should_redraw = False
