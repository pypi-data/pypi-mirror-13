#!/usr/bin/env python
# -*- coding: utf-8 -*-

import upsidedown
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

__version__ = 0.2


def flip_text(message=None):
    if not message:
        message = "┻━┻"
    else:
        message = upsidedown.transform(message)

    return unicode("(╯°□°）╯︵ " + message)


class FlipException(Exception):
    def __init__(self, message=None):
        message = flip_text(message)
        super(Exception, self).__init__(message)


class FlipValueError(ValueError):
    def __init__(self, message=None):
        message = flip_text(message)
        super(ValueError, self).__init__(message)

