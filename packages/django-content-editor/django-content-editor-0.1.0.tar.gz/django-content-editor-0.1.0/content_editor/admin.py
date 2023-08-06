from __future__ import absolute_import, unicode_literals

import json

from django import forms
from django.contrib.admin.options import ModelAdmin, StackedInline
from django.forms.utils import flatatt
from django.templatetags.static import static
from django.utils.html import format_html, mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext


__all__ = ('ContentEditorForm', 'ContentEditorInline', 'ContentEditor')


class ContentEditorForm(forms.ModelForm):
    """
    The item editor form contains hidden region and ordering fields and should
    be used for all content type inlines.
    """
    region = forms.CharField(widget=forms.HiddenInput())
    ordering = forms.IntegerField(widget=forms.HiddenInput())


class ContentEditorInline(StackedInline):
    """
    Custom ``InlineModelAdmin`` subclass used for content types.
    """
    form = ContentEditorForm
    extra = 0
    fk_name = 'parent'

    @classmethod
    def create(cls, model, **kwargs):
        kwargs['model'] = model
        return type(
            str('ContentEditorInline_%s_%s' % (
                model._meta.app_label,
                model._meta.model_name,
            )),
            (cls,),
            kwargs,
        )


class JS(object):
    """
    Use this to insert a script tag via ``forms.Media`` containing additional
    attributes (such as ``id`` and ``data-*`` for CSP-compatible data
    injection.)
    """
    def __init__(self, js, attrs):
        self.js = js
        self.attrs = attrs

    def startswith(self, _):
        # Masquerade as absolute path so that we are returned as-is.
        return True

    def __html__(self):
        return format_html(
            '{}" {}',
            static(self.js),
            mark_safe(flatatt(self.attrs).rstrip('"')),
        )


class ContentEditor(ModelAdmin):
    """
    The ``ContentEditor`` is a drop-in replacement for ``ModelAdmin`` with the
    speciality of knowing how to work with :class:`feincms.models.Base`
    subclasses and associated plugins.

    It does not have any public API except from everything inherited from'
    the standard ``ModelAdmin`` class.
    """

    class Media:
        css = {'all': (
            'content_editor/content_editor.css',
        )}
        js = (
            'content_editor/jquery-ui-1.11.4.custom.min.js',
            'content_editor/tabbed_fieldsets.js',
            # 'content_editor/content_editor.js',  Look below
        )

    def _content_editor_context(self, request, context):
        plugins = [
            iaf.opts.model
            for iaf in context.get('inline_admin_formsets', [])
            if isinstance(iaf.opts, ContentEditorInline)
        ]
        instance = context.get('original')
        if not instance:
            instance = self.model()

        return json.dumps({
            'plugins': [(
                '%s_%s' % (
                    plugin._meta.app_label,
                    plugin._meta.model_name,
                ),
                capfirst(plugin._meta.verbose_name)
            ) for plugin in plugins],
            'regions': [(
                region.key,
                region.title,
                # TODO correct template when POSTing
            ) for region in instance.regions],
            'messages': {
                'createNew': ugettext('Add new item'),
                'empty': ugettext('No items'),
            },
        })

    def render_change_form(self, request, context, **kwargs):
        response = super(ContentEditor, self).render_change_form(
            request, context, **kwargs)

        response.context_data['media'].add_js((
            JS('content_editor/content_editor.js', {
                'id': 'content-editor-context',
                'data-context': self._content_editor_context(
                    request, response.context_data),
            }
        ),))

        return response
