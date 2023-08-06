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
pie_time.cards.weather
======================

This module containse the WeatherCard class.
"""

from threading import Timer

import pygame
import requests

from pie_time.card import AbstractCard

URL_TEMPLATE = (
    'http://api.openweathermap.org/data/2.5/weather?q=%s&units=%s&APPID=%s'
)


class WeatherCard(AbstractCard):
    """
    The weather card.

    This cards displays the current weather for a selected city. The weather
    information is obtained from OpenWeatherMap.

    **Settings dictionary keys**:

    * **api_key** (*string*) - **required** API key.
    * **city** (*string*) - **required** name of the city.
    * **units** (*string*) - units name (``metric`` or ``imperial``). Defaults
      to :py:attr:`pie_time.cards.WeatherCard.UNITS`
    * **refresh_interval** (*int*) - refresh interval in seconds. Defaults to
      :py:attr:`pie_time.cards.WeatherCard.REFRESH_INTERVAL`
    * **city_color** (*tuple*) - city text color. Defaults to
      :py:attr:`pie_time.cards.WeatherCard.WHITE`
    * **icon_color** (*tuple*) - icon text color. Defaults to
      :py:attr:`pie_time.cards.WeatherCard.WHITE`
    * **temperature_color** (*tuple*) - temperature text color. Defaults to
      :py:attr:`pie_time.cards.WeatherCard.WHITE`
    * **conditions_color** (*tuple*) - conditions text color. Defaults to
      :py:attr:`pie_time.cards.WeatherCard.WHITE`
    """

    #: Default units
    UNITS = 'metric'

    #: Default refresh interval
    REFRESH_INTERVAL = 600

    #: White color for text
    WHITE = (255, 255, 255)

    WEATHER_CODE_TO_ICON = {
        '01d': u'',
        '01n': u'',
        '02d': u'',
        '02n': u'',
        '03d': u'',
        '03n': u'',
        '04d': u'',
        '04n': u'',
        '09d': u'',
        '09n': u'',
        '10d': u'',
        '10n': u'',
        '11d': u'',
        '11n': u'',
        '13d': u'',
        '13n': u'',
        '50d': u'',
        '50n': u''
    }
    ICON_SPACING = 24

    def initialize(self, refresh=True):
        assert 'api_key' in self._settings,\
            'Configuration error: missing API key'
        assert 'city' in self._settings, 'Configuration error: missing city'

        self._text_font = pygame.font.Font(
            self.path_for_resource('opensans-light.ttf'), 30
        )

        self._temp_font = pygame.font.Font(
            self.path_for_resource('opensans-light.ttf'), 72
        )

        self._icon_font = pygame.font.Font(
            self.path_for_resource('linea-weather-10.ttf'), 128
        )

        self._timer = None
        self._current_conditions = None
        self._should_redraw = True

        if refresh:
            self._refresh_conditions()

    def _refresh_conditions(self):
        self._app.logger.debug('Refreshing conditions.')
        self._timer = None

        try:
            rsp = requests.get(
                URL_TEMPLATE % (
                    self._settings['city'],
                    self._settings.get('units', self.UNITS),
                    self._settings['api_key']
                )
            )

            if rsp.status_code != 200:
                self._app.logger.error(
                    'WeatherCard: Received HTTP %d' % rsp.status_code
                )
            else:
                try:
                    payload = rsp.json()
                    self._current_conditions = {
                        'conditions': payload['weather'][0]['main'],
                        'icon': payload['weather'][0].get('icon', None),
                        'temperature': payload['main']['temp']
                    }
                    self._should_redraw = True
                except:
                    self._app.logger.error(
                        'WeatherCard: ERROR!', exc_info=True
                    )
        except:
            self._app.logger.error('WeatherCard: ERROR!', exc_info=True)

        self._timer = Timer(
            self._settings.get('refresh_interval', self.REFRESH_INTERVAL),
            self._refresh_conditions
        )
        self._timer.start()

    def _render_city(self):
        city_text = self._text_font.render(
            self._settings['city'], True,
            self._settings.get('city_color', self.WHITE)
        )

        return city_text

    def _render_conditions(self):
        conditions_text = self._text_font.render(
            self._current_conditions['conditions'].capitalize(),
            True, self._settings.get('conditions_color', self.WHITE)
        )

        return conditions_text

    def _render_icon(self):
        icon = self._current_conditions['icon']
        weather_icon = None

        if icon in self.WEATHER_CODE_TO_ICON:
            weather_icon = self._icon_font.render(
                self.WEATHER_CODE_TO_ICON[icon],
                True, self._settings.get('icon_color', self.WHITE)
            )

        return weather_icon

    def _render_temperature(self):
        temp_text = self._temp_font.render(
            u'%d°' % self._current_conditions['temperature'],
            True,
            self._settings.get('temperature_color', self.WHITE)
        )

        return temp_text

    def quit(self):
        if self._timer is not None:
            self._timer.cancel()

    def tick(self):
        if self._should_redraw:
            self.surface.fill(self.background_color)

            city_text = self._render_city()
            city_text_size = city_text.get_size()
            city_text_rect = (
                (self.width - city_text_size[0]) / 2.0,
                0,
                city_text_size[0],
                city_text_size[1]
            )
            self.surface.blit(city_text, city_text_rect)

            if self._current_conditions:
                conditions_text = self._render_conditions()
                conditions_text_size = conditions_text.get_size()
                conditions_text_rect = (
                    (self.width - conditions_text_size[0]) / 2.0,
                    self.height - conditions_text_size[1],
                    conditions_text_size[0],
                    conditions_text_size[1]
                )
                self.surface.blit(conditions_text, conditions_text_rect)

                icon = self._render_icon()
                has_icon = (icon is not None)

                temp_text = self._render_temperature()
                temp_text_size = temp_text.get_size()

                if has_icon:
                    icon_size = icon.get_size()
                    icon_origin_x = (
                        (
                            self.width - (
                                icon_size[0] + self.ICON_SPACING +
                                temp_text_size[0]
                            )
                        ) / 2.0
                    )
                    icon_origin_y = (
                        city_text_size[1] + (
                            self.height - conditions_text_size[1] -
                            city_text_size[1] - icon_size[1]
                        ) / 2.0
                    )
                    icon_rect = (
                        icon_origin_x,
                        icon_origin_y,
                        icon_size[0],
                        icon_size[1]
                    )

                    self.surface.blit(icon, icon_rect)

                temp_text_origin_y = (
                    city_text_size[1] + (
                        self.height - conditions_text_size[1] -
                        city_text_size[1] - temp_text_size[1]
                    ) / 2.0
                )

                if has_icon:
                    temp_text_origin_x = (
                        icon_rect[0] + icon_size[0] +
                        self.ICON_SPACING
                    )
                    temp_text_rect = (
                        temp_text_origin_x,
                        temp_text_origin_y,
                        temp_text_size[0],
                        temp_text_size[1]
                    )
                else:
                    temp_text_rect = (
                        (self.width - temp_text_size[0]) / 2.0,
                        temp_text_origin_y,
                        temp_text_size[0],
                        temp_text_size[1]
                    )

                self.surface.blit(temp_text, temp_text_rect)

            self._should_redraw = False
