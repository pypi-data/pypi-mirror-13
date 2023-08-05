# The MIT License (MIT)
#
# Copyright (c) 2016 masuda_kenichi
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

try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import os


class ConstantsManager():
    def __init__(self, config_file_name='constants.ini', constants_name='ENV'):
        self.config = configparser.RawConfigParser()
        self.config.optionxform = str
        self.config.read(config_file_name)
        self.environment = 'DEFAULT'
        if constants_name in os.environ:
            self.environment = os.environ[constants_name]

    def __getitem__(self, key):
        return self.get(key)

    def get(self, key):
        return self.config.get(self.environment, key)
