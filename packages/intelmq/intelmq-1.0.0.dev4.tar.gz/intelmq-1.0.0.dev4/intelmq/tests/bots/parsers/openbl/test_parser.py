# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

import intelmq.lib.test as test
from intelmq.bots.parsers.openbl.parser import OpenBLParserBot


class TestOpenBLParserBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for OpenBLParserBot.
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = OpenBLParserBot
        cls.default_input_message = {'__type': 'Report'}

if __name__ == '__main__':
    unittest.main()
