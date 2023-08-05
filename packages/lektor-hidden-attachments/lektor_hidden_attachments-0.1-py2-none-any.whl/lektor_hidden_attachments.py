# -*- coding: utf-8 -*-
import os.path

from lektor.pluginsystem import Plugin
from jinja2 import is_undefined


class HiddenAttachmentsPlugin(Plugin):
    name = u'hidden-attachments'
    description = u'Hide attachments by default based on file extension.'

    def on_before_build(self, source, **extra):
        config = self.get_config()

        # if we're building an attachment & hidden isn't explicitly set
        if (getattr(source, 'is_attachment', False) and
            is_undefined(source._data['_hidden'])
            ):

            # see if this extension is hidden by default
            ext = os.path.splitext(source.path)[1][1:]
            source._data['_hidden'] = config.get('hidden.{}'.format(ext), False)
