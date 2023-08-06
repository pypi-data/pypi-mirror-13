#!/usr/bin/env python
# -*- coding: utf-8 -*-

import upsidedown
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

__version__ = 0.4


class FlipException(Exception):

    @staticmethod
    def flip_text(message=None):
        if not message:
            message = "┻━┻"
        else:
            message = upsidedown.transform(message)

        return unicode("(╯°□°）╯︵ " + message)

    def __init__(self, message=None):
        message = self.flip_text(message)
        super(Exception, self).__init__(message)
