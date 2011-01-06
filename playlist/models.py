from datetime import datetime, timedelta

from django.contrib.contenttypes import generic
from django.conf import settings
from django.db import models

from panya.models import ModelBase
from playlist.managers import ContentPlaylistManager

class Playlist(ModelBase):
    def current_entry(self):
        now = datetime.now()
        entries = self.playlistentry_set.filter(start__lt=now, end__gt=now).order_by('-start')
        return entries[0] if entries else None
    
    def next_entry(self):
        now = datetime.now()
        entries = self.playlistentry_set.filter(start__gt=now).order_by('start')
        return entries[0] if entries else None

    def __unicode__(self):
        return self.title

class PlaylistEntry(models.Model):
    title = models.CharField(max_length=64)
    playlist = models.ForeignKey('playlist.Playlist')
    start = models.DateTimeField(
        verbose_name="Starting Date & Time", 
        help_text="Date and time at which this entry starts."
    )
    end = models.DateTimeField(
        verbose_name="Ending Date & Time", 
        help_text="Date and time at which this entry ends."
    )

    def __unicode__(self):
        return '%s %s - %s' % (self.title, self.start, self.end)

    class Meta():
        verbose_name = "Playlist entry"
        verbose_name_plural = "Playlist entries"
        ordering = ['start', 'end']


class ScheduledPlaylist(models.Model):
    objects = ContentPlaylistManager()
    
    content = models.ForeignKey(
        "panya.ModelBase", 
        related_name="content_content_playlist_set",
    )

    playlist = models.ForeignKey(
        'playlist.Playlist', 
        related_name="playlist_content_playlist_set"
    )
    start = models.DateTimeField()
    end = models.DateTimeField()

    def __unicode__(self):
        return "Scheduled playlist for %s" % self.playlist.title

    def get_inclusive_entries(self):
        """
        Returns those playlist entries that fall between start and end.
        A playlist entry falls between start and end if it starts on or after
        start and before end. Order by start.
        """
        return self.playlist.playlistentry_set.filter(start__gt=self.start, start__lt=self.end, is_public=True).order_by('start')

    def get_inclusive_entries_today(self):
        """
        Get inclusive entries limited to entries for the current day
        A playlist entry applies to the current day if it ends on or after
        00:00 today and starts before 23:59:59 today. Order by start.
        """
        today = datetime.now().date()
        start = datetime(year=today.year, month=today.month, day=today.day)
        end = datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59)
        return self.get_inclusive_entries().filter(end__gt=start, start__lt=end).order_by('start')
   
    @classmethod
    def get_current_playlist_entry_for(cls, obj):
        """
        Looks up current playlist for the given object and return its current entry. 
        """
        scheduled_playlist = cls.objects.for_content_now(obj)
        return scheduled_playlist.playlist.current_entry() if scheduled_playlist else None

    @classmethod
    def get_next_playlist_entry_for(cls, obj):
        """
        Looks up current playlist for the given object and return its next entry. 
        """
        scheduled_playlist = cls.objects.for_content_now(obj)
        return scheduled_playlist.playlist.next_entry() if scheduled_playlist else None
