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
pie_time.application
====================

This module implements the PieTime application.
"""

import datetime
import argparse
import imp
import logging
import os
import sys

import pygame

from pie_time import __copyright__ as copyright, __version__ as version

RET_OK = 0
RET_ERROR = 99

MOTD_PICLOCK_BANNER = u"PieTime v%s by Tomek Wójcik" % (
    version
)
MOTD_LICENSE_BANNER = u"Released under the MIT license"

EVENT_QUIT = 0
EVENT_CLICK_TO_UNBLANK = 1
EVENT_CLICK_TO_PREV_CARD = 2
EVENT_CLICK_TO_NEXT_CARD = 3


class Quit(Exception):
    pass


class PieTimeEvent(object):
    def __init__(self, app, event):
        self.event = event
        self.app = app

    def is_quit(self):
        return (self.event.type == pygame.QUIT)

    def is_key_quit(self):
        return (
            self.event.type == pygame.KEYDOWN
            and self.event.key == self.app.KEY_QUIT
        )

    def is_click_to_unblank(self):
        return (
            self.event.type == pygame.MOUSEBUTTONDOWN
            and self.app._click_to_unblank_interval is not None
            and self.app._is_blanked is True
        )

    def is_click_to_prev_card(self):
        return (
            self.event.type == pygame.MOUSEBUTTONDOWN
            and self.app._click_to_transition is True
            and self.app._is_blanked is False
            and self.app._ctt_region_prev.collidepoint(self.event.pos) == 1
        )

    def is_click_to_next_card(self):
        return (
            self.event.type == pygame.MOUSEBUTTONDOWN
            and self.app._click_to_transition is True
            and self.app._is_blanked is False
            and self.app._ctt_region_next.collidepoint(self.event.pos) == 1
        )


class PieTime(object):
    """
    The PieTime application.

    :param deck: the deck
    :param screen_size: tuple of (width, height) to use as the screen size
    :param fps: number of frames per second to limit rendering to
    :param blanker_schedule: blanker schedule
    :param click_to_unblank_interval: time interval for click to unblank
    :param click_to_transition: boolean defining if click to transition is
        enabled
    :param verbose: boolean defining if verbose logging should be on
    :param log_path: path to log file (if omitted, *stdout* will be used)
    """

    #: Default background color
    BACKGROUND_COLOR = (0, 0, 0)

    #: Blanked screen color
    BLANK_COLOR = (0, 0, 0)

    #: Default card display duration interval
    CARD_INTERVAL = 60

    #: Defines key which quits the application
    KEY_QUIT = pygame.K_ESCAPE

    #: Defines size of click to transition region square
    CLICK_TO_TRANSITION_REGION_SIZE = 30

    _DEFAULT_OUTPUT_STREAM = sys.stdout

    _STREAM_FACTORY = file

    def __init__(self, deck, screen_size=(320, 240), fps=20,
                 blanker_schedule=None, click_to_unblank_interval=None,
                 click_to_transition=True, verbose=False, log_path=None):
        self._deck = deck

        #: The screen surface
        self.screen = None
        #: The screen size tuple
        self.screen_size = screen_size
        #: List of events captured in this frame
        self.events = []
        #: Path to log file. If `None`, *stdout* will be used for logging.
        self.log_path = log_path

        self._fps = fps
        self._verbose = verbose
        self._blanker_schedule = blanker_schedule
        self._click_to_unblank_interval = click_to_unblank_interval
        self._click_to_transition = click_to_transition
        self._clock = None
        self._cards = []
        self._is_blanked = False
        self._current_card_idx = None
        self._current_card_time = None
        self._should_quit = False
        self._internal_events = set()
        self._ctu_timer = None
        self._output_stream = None

        self._ctt_region_prev = pygame.Rect(
            0,
            self.screen_size[1] - self.CLICK_TO_TRANSITION_REGION_SIZE,
            self.CLICK_TO_TRANSITION_REGION_SIZE,
            self.CLICK_TO_TRANSITION_REGION_SIZE
        )

        self._ctt_region_next = pygame.Rect(
            self.screen_size[0] - self.CLICK_TO_TRANSITION_REGION_SIZE,
            self.screen_size[1] - self.CLICK_TO_TRANSITION_REGION_SIZE,
            self.CLICK_TO_TRANSITION_REGION_SIZE,
            self.CLICK_TO_TRANSITION_REGION_SIZE
        )

    def _should_blank(self, now=None):
        if self._has_click_to_unblank_event() or self._ctu_timer is not None:
            if self._is_blanked is False and self._ctu_timer is None:
                self._ctu_timer = None
                return False

            if self._click_to_unblank_interval is not None:
                if self._ctu_timer is None:
                    self._ctu_timer = self._click_to_unblank_interval
                    return False

                self._ctu_timer -= self._clock.get_time() / 1000.0
                if self._ctu_timer <= 0:
                    self._ctu_timer = None
                    return True
                else:
                    return False

        if self._blanker_schedule:
            delta_blanker_start, delta_blanker_end = self._blanker_schedule

            if now is None:
                now = datetime.datetime.now()

            midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)

            blanker_start = midnight + delta_blanker_start
            blanker_end = midnight + delta_blanker_end

            if blanker_start > blanker_end:
                if now.hour < 12:
                    blanker_start -= datetime.timedelta(days=1)
                else:
                    blanker_end += datetime.timedelta(days=1)

            if now >= blanker_start and now < blanker_end:
                return True

        return False

    def _blank(self):
        if self._is_blanked is False:
            self.logger.debug('Blanking the screen!')
            self.will_blank()

        self._is_blanked = True
        self.screen.fill(self.BLANK_COLOR)

    def _unblank(self):
        if self._is_blanked:
            self.logger.debug('Unblanking the screen!')
            self.will_unblank()

            self._is_blanked = False
            self._current_card_idx = 0
            self._current_card_time = 0

            self._cards[self._current_card_idx][0].show()

    def _transition_cards(self, direction=1, force=False):
        if self._current_card_idx is None and force is False:
            self._current_card_idx = 0
            self._current_card_time = 0
            self._cards[self._current_card_idx][0].show()
        elif len(self._cards) > 1:
            self._current_card_time += self._clock.get_time() / 1000.0
            card_interval = self._cards[self._current_card_idx][1]
            if self._current_card_time >= card_interval or force is True:
                new_card_idx = self._current_card_idx + direction
                if new_card_idx >= len(self._cards):
                    new_card_idx = 0
                elif new_card_idx < 0:
                    new_card_idx = len(self._cards) - 1

                self.logger.debug('Card transition: %d -> %d' % (
                    self._current_card_idx, new_card_idx
                ))

                self._cards[self._current_card_idx][0].hide()

                self._current_card_idx = new_card_idx
                self._current_card_time = 0

                self._cards[self._current_card_idx][0].show()

    def _get_events(self):
        self._internal_events = set()
        self.events = []
        for event in pygame.event.get():
            pie_time_event = PieTimeEvent(self, event)
            if pie_time_event.is_quit():
                self.logger.debug('_get_events: QUIT')
                self._internal_events.add(EVENT_QUIT)
            elif pie_time_event.is_key_quit():
                self.logger.debug('_get_events: KEY_QUIT')
                self._internal_events.add(EVENT_QUIT)
            elif pie_time_event.is_click_to_unblank():
                self.logger.debug('_get_events: CLICK_TO_UNBLANK')
                self._internal_events.add(EVENT_CLICK_TO_UNBLANK)
            elif pie_time_event.is_click_to_prev_card():
                self.logger.debug('_get_events: CLICK_TO_PREV_CARD')
                self._internal_events.add(EVENT_CLICK_TO_PREV_CARD)
            elif pie_time_event.is_click_to_next_card():
                self.logger.debug('_get_events: CLICK_TO_NEXT_CARD')
                self._internal_events.add(EVENT_CLICK_TO_NEXT_CARD)
            else:
                self.events.append(event)

    def _has_quit_event(self):
        return (EVENT_QUIT in self._internal_events)

    def _has_click_to_unblank_event(self):
        return (EVENT_CLICK_TO_UNBLANK in self._internal_events)

    def _start_clock(self):
        self._clock = pygame.time.Clock()

    def _setup_output_stream(self):
        if self.log_path is None:
            self._output_stream = self._DEFAULT_OUTPUT_STREAM
        else:
            self._output_stream = self._STREAM_FACTORY(self.log_path, 'a')

    def _setup_logging(self):
        logger = logging.getLogger('PieTime')
        requests_logger = logging.getLogger('requests')

        if self._verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            requests_logger.setLevel(logging.WARNING)

        handler = logging.StreamHandler(self._output_stream)
        formatter = logging.Formatter(
            '%(asctime)s PieTime: %(levelname)s: %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        for requests_handler in requests_logger.handlers:
            requests_logger.removeHandler(requests_handler)

        requests_logger.addHandler(handler)

    @property
    def logger(self):
        """The application-wide :py:class:`logging.Logger` object."""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger('PieTime')

        return self._logger

    def init_pygame(self):
        """Initializes PyGame and the internal clock."""
        self.logger.debug('Initializing PyGame.')
        pygame.init()
        pygame.mouse.set_visible(False)

    def quit_pygame(self):
        """Quits PyGame."""
        self.logger.debug('Quitting PyGame.')
        pygame.quit()

        self._clock = None

    def init_cards(self):
        """
        Initializes the cards.

        Initialization of a card consits of the following steps:

        * Creating an instance of the card class,
        * Binding the card with the application
          (:py:meth:`pie_time.AbstractCard.set_app`),
        * Setting the card's settings
          (:py:meth:`pie_time.AbstractCard.set_settings`),
        * Initializing the card (:py:meth:`pie_time.AbstractCard.initialize`).
        """
        self.logger.debug('Initializing cards.')
        for i in xrange(0, len(self._deck)):
            card_def = self._deck[i]

            klass = None
            interval = self.CARD_INTERVAL
            settings = {}

            if not isinstance(card_def, tuple):
                klass = card_def
            elif len(card_def) == 2:
                klass, interval = card_def
            elif len(card_def) == 3:
                klass, interval, settings = card_def

            if klass is not None:
                card = klass()
                card.set_app(self)
                card.set_settings(settings)
                card.initialize()

                self._cards.append((card, interval))
            else:
                self.logger.warning('Invalid deck entry at index: %d' % i)

    def destroy_cards(self):
        """
        Destroys the cards.

        Calls the :py:meth:`pie_time.AbstractCard.quit` of each card.
        """
        self.logger.debug('Destroying cards.')
        while len(self._cards) > 0:
            card, _ = self._cards.pop()

            try:
                card.quit()
            except:
                self.logger.error('ERROR!', exc_info=True)

    def get_screen(self):
        """Creates and returns the screen screen surface."""
        self.logger.debug('Creating screen.')
        return pygame.display.set_mode(self.screen_size)

    def fill_screen(self):
        """
        Fills the screen surface with color defined in
        :py:attr:`pie_time.PieTime.BACKGROUND_COLOR`.
        """
        self.screen.fill(self.BACKGROUND_COLOR)

    def run(self, standalone=True):
        """
        Runs the application.

        This method contains the app's main loop and it never returns. Upon
        quitting, this method will call the :py:func:`sys.exit` function with
        the status code (``99`` if an unhandled exception occurred, ``0``
        otherwise).

        The application will quit under one of the following conditions:

        * An unhandled exception reached this method,
        * PyGame requested to quit (e.g. due to closing the window),
        * Some other code called the :py:meth:`pie_time.PieTime.quit` method on
          the application.

        Before quitting the :py:meth:`pie_time.PieTime.destroy_cards` and
        :py:meth:`pie_time.PieTime.quit_pygame` methods will be called to clean
        up.
        """
        result = RET_OK

        self._setup_output_stream()
        self._setup_logging()

        try:
            self.logger.info(MOTD_PICLOCK_BANNER)
            self.logger.info(copyright)
            self.logger.info(MOTD_LICENSE_BANNER)
            self.logger.debug('My PID = %d' % os.getpid())

            self.init_pygame()
            self.screen = self.get_screen()

            self.init_cards()

            self._start_clock()

            while True:
                self._get_events()

                if self._should_quit or self._has_quit_event():
                    raise Quit()

                if not self._should_blank():
                    self._unblank()

                    if EVENT_CLICK_TO_PREV_CARD in self._internal_events:
                        self._transition_cards(direction=-1, force=True)
                    elif EVENT_CLICK_TO_NEXT_CARD in self._internal_events:
                        self._transition_cards(direction=1, force=True)
                    else:
                        self._transition_cards()

                    card = self._cards[self._current_card_idx][0]

                    card.tick()

                    self.fill_screen()
                    self.screen.blit(
                        card.surface, (0, 0, card.width, card.height)
                    )
                else:
                    self._blank()

                pygame.display.flip()

                self._clock.tick(self._fps)
        except Exception as exc:
            if not isinstance(exc, Quit):
                self.logger.error('ERROR!', exc_info=True)
                result = RET_ERROR
        finally:
            self.destroy_cards()
            self.quit_pygame()

            if standalone:
                sys.exit(result)
            else:
                return result

    def quit(self):
        """Tells the application to quit."""
        self._should_quit = True

    def will_blank(self):
        """
        Called before blanking the screen.

        This method can be used to perform additional operations before
        blanking the screen.

        The default implementation does nothing.
        """
        pass

    def will_unblank(self):
        """
        Called before unblanking the screen.

        This method can be used to perform additional operations before
        unblanking the screen.

        The default implementation does nothing.
        """

        pass
