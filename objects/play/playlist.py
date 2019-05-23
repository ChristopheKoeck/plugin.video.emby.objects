# -*- coding: utf-8 -*-

#################################################################################################

import logging

import xbmc
import xbmcgui

from objects.play import PlayStrm
from helper import window

#################################################################################################

LOG = logging.getLogger("EMBY."+__name__)
PLAY = {
    'PlayNow': 0,
    'PlayNext': 1,
    'PlayLast': 2
}

#################################################################################################


class Playlist(object):


    def __init__(self, server_id, items, mode=None, seektime=None, mediasource_id=None, 
                 audio=None, subtitle=None, *args, **kwargs):

        self.server_id = server_id
        self.items = items
        self.info = {}

        mode = mode or PLAY['PlayNow']
        LOG.info("--[ play playlist ]")

        self.play(mode, seektime, mediasource_id, audio, subtitle)
        self.play_playlist()

    def play(self, mode, seektime=None, mediasource_id=None, audio=None, subtitle=None, *args, **kwargs):

        ''' Clear Playlist and start playback for PlayNow mode.
        '''
        params = {
            'Id': self.items.pop(0),
            'AudioIndex': audio,
            'Subtitle': subtitle,
            'MediaSourceId': mediasource_id
        }
        if seektime:
            window('emby.resume.bool', True)

        funcs = [self.play_now, self.play_next, self.play_last]
        funcs[mode](params, *args, **kwargs)

    def play_now(self, params, *args, **kwargs):

        play = PlayStrm(params, self.server_id)
        self.info['StartIndex'] = 0
        self.info['Index'] = self.info['StartIndex']

        if play.info['Item']['MediaType'] == 'Video' or play.info['Item']['Type'] == 'AudioBook':
            play.info['KodiPlaylist'].clear()
        else:
            play.info['KodiPlaylist'] = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
            play.info['KodiPlaylist'].clear()

        self.info['Index'] = play.play()
        play.start_playback()

    def play_next(self, params, *args, **kwargs):

        play = PlayStrm(params, self.server_id)
        pl_size = max(play.info['KodiPlaylist'].size(), 0)
        self.info['StartIndex'] = max(play.info['KodiPlaylist'].getposition(), 0) + int(bool(pl_size))
        self.info['Index'] = play.play(self.info['StartIndex'])

    def play_last(self, params, *args, **kwargs):

        play = PlayStrm(params, self.server_id)
        self.info['StartIndex'] = max(play.info['KodiPlaylist'].size(), 0)
        self.info['Index'] = play.play(self.info['StartIndex'])

    def play_playlist(self):

        for item in self.items:

            play = PlayStrm({'Id': item}, self.server_id)
            self.info['Index'] = play.play_folder(self.info['Index'])