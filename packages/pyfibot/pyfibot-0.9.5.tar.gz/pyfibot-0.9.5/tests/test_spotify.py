# .-*- encoding: utf-8 -*-
from __future__ import unicode_literals
import bot_mock
from nose.tools import eq_
from pyfibot.modules.module_spotify import handle_privmsg
from utils import check_re
from vcr import VCR
my_vcr = VCR(path_transformer=VCR.ensure_suffix('.yaml'),
             cassette_library_dir="tests/cassettes/")


bot = bot_mock.BotMock()


@my_vcr.use_cassette
def test_spotify_track():
    msg = 'spotify:track:46c5HqyYtOkpjdp193KCln'
    title = '[Spotify] Ultra Bra - Sinä päivänä kun synnyin - Heikko valo'
    eq_(('#channel', title), handle_privmsg(bot, None, '#channel', msg))


@my_vcr.use_cassette
def test_http_artist():
    msg = 'http://open.spotify.com/artist/3MXhtYDNuzQQmLfOKFgPiI'
    regex = '\[Spotify\] Einojuhani Rautavaara( \(Genre: \S.+\))?'
    check_re(regex, handle_privmsg(bot, None, '#channel', msg)[1])


@my_vcr.use_cassette
def test_http_album():
    msg = 'http://open.spotify.com/album/5O8MKoOZoTK1JfD1tAN2TA'
    title = '[Spotify] Organ - Nekrofiilis (2001)'
    eq_(('#channel', title), handle_privmsg(bot, None, '#channel', msg))
