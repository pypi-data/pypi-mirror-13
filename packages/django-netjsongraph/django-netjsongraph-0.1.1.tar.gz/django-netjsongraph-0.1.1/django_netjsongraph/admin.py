from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Topology, Node, Link
from .base import TimeStampedEditableAdmin


class TopologyAdmin(TimeStampedEditableAdmin):
    list_display = ('label', 'parser', 'link_url', 'published', 'created', 'modified')
    readonly_fields = ['protocol', 'version', 'revision', 'metric']
    list_filter = ('parser',)
    actions = ['update_selected', 'unpublish_selected', 'publish_selected']

    def link_url(self, obj):  # pragma nocover
        return '<a href="{0}" target="_blank">{0}</a>'.format(obj.url)
    link_url.allow_tags = True

    def get_actions(self, request):
        """ move delete action to last position """
        actions = super(TopologyAdmin, self).get_actions(request)
        delete = actions['delete_selected']
        del actions['delete_selected']
        actions['delete_selected'] = delete
        return actions

    def _message(self, request, rows, suffix):
        if rows == 1:
            prefix = _('1 {0} was'.format(self.model._meta.verbose_name))
        else:  # pragma: nocover
            prefix = _('{0} {1} were'.format(rows, self.model._meta.verbose_name_plural))
        self.message_user(request, '{0} {1}'.format(prefix, suffix))

    def update_selected(self, request, queryset):
        items = list(queryset)
        for item in items:
            item.update()
        self._message(request, len(items), _('successfully updated'))
    update_selected.short_description = _('Update selected topologies')

    def publish_selected(self, request, queryset):
        rows_updated = queryset.update(published=True)
        self._message(request, rows_updated, _('successfully published'))
    publish_selected.short_description = _('Publish selected topologies')

    def unpublish_selected(self, request, queryset):
        rows_updated = queryset.update(published=False)
        self._message(request, rows_updated, _('successfully unpublished'))
    unpublish_selected.short_description = _('Unpublish selected items')


class NodeAdmin(TimeStampedEditableAdmin):
    list_display = ('name', 'topology', 'addresses')
    list_filter = ('topology',)
    search_fields = ('addresses', 'label', 'properties')


class LinkAdmin(TimeStampedEditableAdmin):
    raw_id_fields = ('source', 'target')
    list_display = ('__str__', 'topology', 'status', 'cost', 'cost_text')
    list_filter = ('status', 'topology')
    search_fields = (
        'source__label',
        'target__label',
        'source__addresses',
        'target__addresses',
        'properties',
    )


admin.site.register(Topology, TopologyAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Link, LinkAdmin)
