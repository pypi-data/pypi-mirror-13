# -*- encoding: utf-8 -*-
"""
Fortune-file support
"""

from __future__ import unicode_literals, print_function, division
import random

def command_fortune(bot, user, channel, args):
    with file("databases/theo.fortune") as f:
        d = f.read()
        quotes = d.split("\n")
        bot.say(channel, random.choice(quotes))
