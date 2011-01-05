from django import template
from playlist.models import ScheduledPlaylist

register = template.Library()

@register.tag
def get_current_playlist_entry(parser, token):
    try:
        tag_name, for_arg, obj, as_arg, as_varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('get_current_playlist_entry tag requires 2 arguments (obj, as_varname), %s given' % (len(token.split_contents()) - 1))
    return GetCurrentPlaylistEntryNode(obj, as_varname)

class GetCurrentPlaylistEntryNode(template.Node):
    def __init__(self, obj, as_varname):
        self.obj = template.Variable(obj)
        self.as_varname = as_varname

    def render(self, context):
        obj = self.obj.resolve(context)
        context[self.as_varname] = ScheduledPlaylist.get_current_playlist_entry_for(obj)
        return ''

@register.tag
def get_next_playlist_entry(parser, token):
    try:
        tag_name, for_arg, obj, as_arg, as_varname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('get_next_playlist_entry tag requires 2 arguments (obj, as_varname), %s given' % (len(token.split_contents()) - 1))
    return GetNextPlaylistEntryNode(obj, as_varname)

class GetNextPlaylistEntryNode(template.Node):
    def __init__(self, obj, as_varname):
        self.obj = template.Variable(obj)
        self.as_varname = as_varname

    def render(self, context):
        obj = self.obj.resolve(context)
        context[self.as_varname] = ScheduledPlaylist.get_next_playlist_entry_for(obj)
        return ''
