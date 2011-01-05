from datetime import datetime

from django.db import models

class ContentPlaylistManager(models.Manager):
    def for_content(self, content):
        return self.get_query_set().filter(content=content)
    
    def for_content_today(self, content):
        today = datetime.now().date()
        start = datetime(year=today.year, month=today.month, day=today.day)
        end = datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59)
        return self.for_content(content).exclude(start__gt=end, end__lt=start).order_by('start')
        
    def for_content_now(self, content):
        now = datetime.now()
        query_set = self.for_content(content).filter(start__lt=now, end__gt=now)
        return query_set[0] if query_set else None

    def todays_entries_for_content(self, content):
        playlists = self.for_content_today(content)
        playlist_entries = []
        for playlist in playlists:
            playlist_entries += [entry for entry in playlist.get_inclusive_entries_today()]

        return playlist_entries
