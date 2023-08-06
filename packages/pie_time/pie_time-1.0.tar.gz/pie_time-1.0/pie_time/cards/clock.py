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
pie_time.cards.clock
====================

This module containse the ClockCard class.
"""

import datetime

import pygame

from pie_time.card import AbstractCard


class ClockCard(AbstractCard):
    """
    The clock card.

    This card displays a digital clock and date.

    **Settings dictionary keys**:

    * **time_format** (*string*) - time format string (*strftime()*
      compatible). Defaults to :py:attr:`pie_time.cards.ClockCard.TIME_FORMAT`
    * **time_blink** (*boolean*) - if set to ``True`` the semicolons will
      blink. Defaults to ``True``.
    * **time_color** (*tuple*) - time text color. Defaults to
      :py:attr:`pie_time.cards.ClockCard.GREEN`
    * **date_format** (*string*) - date format string (*strftime()*
      compatible). Defaults to :py:attr:`pie_time.cards.ClockCard.DATE_FORMAT`
    * **date_color** (*tuple*) - date text color. Defaults to
      :py:attr:`pie_time.cards.ClockCard.GREEN`
    """

    #: Green color for text
    GREEN = (96, 253, 108)

    #: Default time format
    TIME_FORMAT = '%I:%M %p'

    #: Default date format
    DATE_FORMAT = '%a, %d %b %Y'

    def initialize(self):
        self._time_font = pygame.font.Font(
            self.path_for_resource('PTM55FT.ttf'), 63
        )

        self._date_font = pygame.font.Font(
            self.path_for_resource('opensans-light.ttf'), 36
        )

        self._now = None
        self._current_interval = 0

    def _render_time(self, now):
        time_format = self._settings.get('time_format', self.TIME_FORMAT)

        if self._settings.get('time_blink', True) and now.second % 2 == 1:
            time_format = time_format.replace(':', ' ')

        current_time = now.strftime(time_format)

        text = self._time_font.render(
            current_time, True, self._settings.get('time_color', self.GREEN)
        )

        return text

    def _render_date(self, now):
        date_format = self._settings.get('date_format', self.DATE_FORMAT)

        current_date = now.strftime(date_format)

        text = self._date_font.render(
            current_date, True, self._settings.get('date_color', self.GREEN)
        )

        return text

    def _update_now(self):
        if self._now is None:
            self._now = datetime.datetime.now()
            self._current_interval = 0

            return True
        else:
            self._current_interval += self._app._clock.get_time()

            if self._current_interval >= 1000:
                self._now = datetime.datetime.now()
                self._current_interval = self._current_interval - 1000

                return True

        return False

    def show(self):
        self._now = None

    def tick(self):
        now_updated = self._update_now()

        if now_updated:
            time_text = self._render_time(self._now)
            date_text = self._render_date(self._now)

            time_text_size = time_text.get_size()
            date_text_size = date_text.get_size()

            time_text_origin_y = (
                (self.height - time_text_size[1] - date_text_size[1]) / 2.0
            )

            time_text_rect = (
                (self.width - time_text_size[0]) / 2.0,
                time_text_origin_y,
                time_text_size[0],
                time_text_size[1]
            )

            date_text_rect = (
                (self.width - date_text_size[0]) / 2.0,
                time_text_origin_y + time_text_size[1],
                date_text_size[0],
                date_text_size[1]
            )

            self.surface.fill(self.background_color)

            self.surface.blit(time_text, time_text_rect)
            self.surface.blit(date_text, date_text_rect)
