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
pie_time.card
=============

This module contains the AbstractCard class.
"""

import os
import sys

import pygame


class AbstractCard(object):
    """
    The abstract card class.

    All the custom cards **must** inherit from this class.

    **Application binding and settings.**

    The application calls the card's :py:meth:`pie_time.AbstractCard.set_app`
    and :py:meth:`pie_time.AbstractCard.set_settings` methods during
    initialization (before calling the
    :py:meth:`pie_time.AbstractCard.initialize` method).

    The application reference is stored in ``_app`` attribute.

    The settings dictionary is stored in ``_settings`` attribute and defaults
    to an empty dictionary.

    **Drawing**

    All the drawing on the card's surface should be done in the
    :py:meth:`pie_time.AbstractCard.tick` method. The method's implementation
    should be as fast as possible to avoid throttling the FPS down.

    **Resources**

    The :py:meth:`pie_time.AbstractCard.path_for_resource` method can be used
    to get an absolute path to a resource file. The card's resource folder
    should be placed along with the module containing the card's class.

    Name of the resource folder can be customized by overriding the
    :py:attr:`pie_time.AbstractCard.RESOURCE_FOLDER` attribute.
    """
    #: Name of the folder containing the resources
    RESOURCE_FOLDER = 'resources'

    def __init__(self):
        self._app = None
        self._settings = {}
        self._surface = None

    def set_app(self, app):
        """Binds the card with the *app*."""
        self._app = app

    def set_settings(self, settings):
        """Sets *settings* as the card's settings."""
        self._settings = settings

    @property
    def width(self):
        """The card's surface width. Defaults to the app screen's width."""
        return self._app.screen_size[0]

    @property
    def height(self):
        """The card's surface height. Defaults to the app screen's height."""
        return self._app.screen_size[1]

    @property
    def surface(self):
        """
        The cards surface. The surface width and height are defined by the
        respective properties of the class.
        """
        if self._surface is None:
            self._surface = pygame.surface.Surface((self.width, self.height))

        return self._surface

    @property
    def background_color(self):
        """
        The background color. Defaults to
        :py:attr:`pie_time.PieTime.BACKGROUND_COLOR`.
        """
        return self._settings.get(
            'background_color', self._app.BACKGROUND_COLOR
        )

    def path_for_resource(self, resource, folder=None):
        """
        Returns an absolute path for *resource*. The optional *folder*
        keyword argument allows specifying a subpath.
        """
        _subpath = ''
        if folder:
            _subpath = folder

        module_path = sys.modules[self.__module__].__file__

        return os.path.join(
            os.path.abspath(os.path.dirname(module_path)),
            self.RESOURCE_FOLDER, _subpath, resource
        )

    def initialize(self):
        """
        Initializes the card.

        The application calls this method right after creating an instance of
        the class.

        This method can be used to perform additional initialization on the
        card, e.g. loading resources, setting the initial state etc.

        The default implementation does nothing.
        """
        pass

    def quit(self):
        """
        Initializes the card.

        This method can be used to perform additional cleanup on the
        card, e.g. stop threads, free resources etc.

        The default implementation does nothing.
        """

    def show(self):
        """
        Shows the card.

        The application calls this method each time the card becomes the
        current card.

        This method can be used to reset initial state, e.g. sprite positions.

        The default implementation does nothing.
        """
        pass

    def hide(self):
        """
        Hides the card.

        The application calls this method each time the card resignes the
        current card.

        This method can be used to e.g. stop threads which aren't supposed to
        be running when the card isn't being displayed.

        The default implementation does nothing.
        """
        pass

    def tick(self):
        """
        Ticks the card.

        The application calls this method on the current card in every main
        loop iteration.

        This method should be used to perform drawing and other operations
        needed to properly display the card on screen.

        Subclasses **must** override this method.
        """
        raise NotImplementedError('TODO')
