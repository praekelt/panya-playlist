import unittest
from datetime import datetime, timedelta

from panya.models import ModelBase
from playlist.models import Playlist, PlaylistEntry, ScheduledPlaylist

class ScheduledPlaylistTestCase(unittest.TestCase):
    def test_get_playlist_entry_for(self):
        # Create testing content.
        playlist = Playlist.objects.create(title='test playlist', state='published')
        content = ModelBase.objects.create(title='test content', state='published')

        # Return nothing without a defined scheduled playlist.
        self.failIf(ScheduledPlaylist.get_current_playlist_entry_for(content))
        
        # Return nothing with a defined scheduled playlist not having any playlist entries.
        scheduled_playlist = ScheduledPlaylist.objects.create(playlist=playlist, content=content, start=datetime.now(), end=datetime.now() + timedelta(days=10))
        self.failIf(ScheduledPlaylist.get_current_playlist_entry_for(content))

        # Return current entry with a defined scheduled playlist having a current playlist entry.
        playlist_entry = PlaylistEntry.objects.create(title = 'test playlistentry', playlist=playlist, start=datetime.now() - timedelta(days=1), end=datetime.now() + timedelta(days=1))
        self.failUnless(ScheduledPlaylist.get_current_playlist_entry_for(content) == playlist_entry)
        
        # Return next entry with a defined scheduled playlist having a current playlist entry.
        playlist_entry = PlaylistEntry.objects.create(title = 'test playlistentry', playlist=playlist, start=datetime.now() + timedelta(days=1), end=datetime.now() + timedelta(days=2))
        self.failUnless(ScheduledPlaylist.get_next_playlist_entry_for(content) == playlist_entry)
