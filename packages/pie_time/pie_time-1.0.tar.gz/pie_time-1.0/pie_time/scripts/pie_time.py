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

import ConfigParser
import imp
import os
import sys
import traceback

RET_OK = 0
RET_NO_ARGS = 1
RET_ERROR = 99

CONFIG_SECTION_PIE_TIME = 'PieTime'
CONFIG_SECTION_SDL = 'SDL'

SDL_DEFAULTS = {
    'VIDEODRIVER': None
}

def _find_module(name, search_path):
    import_path = name.split('.', 1)

    mod_f, mod_path, mod_desc = imp.find_module(import_path[0], search_path)
    if mod_desc[2] == imp.PKG_DIRECTORY:
        return _find_module(
            import_path[1], [os.path.abspath(mod_path)]
        )
    else:
        return mod_f, mod_path, mod_desc

def main():
    try:
        config_file_path = sys.argv[1]
    except IndexError:
        print 'usage: %s [CONFIG_FILE]' % sys.argv[0]
        return RET_NO_ARGS

    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    config.read(config_file_path)

    app_spec = config.get(CONFIG_SECTION_PIE_TIME, 'app_module', True)
    try:
        app_module, app_obj = app_spec.split(':')
    except ValueError:
        print "%s: failed to find application '%s'" % (
            sys.argv[0], app_spec
        )
        return RET_ERROR

    mod_f = None
    result = RET_OK
    try:
        mod_search_path = [os.getcwd()] + sys.path
        mod_f, mod_path, mod_desc = _find_module(app_module, mod_search_path)

        mod = imp.load_module(app_module, mod_f, mod_path, mod_desc)
        app = getattr(mod, app_obj)

        if config.has_option(CONFIG_SECTION_PIE_TIME, 'log_path'):
            app.log_path = config.get(CONFIG_SECTION_PIE_TIME, 'log_path')

        sdl_config = dict(SDL_DEFAULTS)
        if config.has_section(CONFIG_SECTION_SDL):
            sdl_config.update({
                x[0]: x[1] for x in config.items(CONFIG_SECTION_SDL)
            })

        for k, v in sdl_config.iteritems():
            if v:
                os.environ['SDL_%s' % k] = v

        result = app.run(standalone=False)
    except:
        traceback.print_exc()
        result = RET_ERROR
    finally:
        if mod_f:
            mod_f.close()

    return result

if __name__ == '__main__':
    sys.exit(main())
