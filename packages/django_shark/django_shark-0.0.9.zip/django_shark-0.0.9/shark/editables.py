from django.utils.timezone import now

from shark.base import Text
from shark.models import EditableText


class Editable:
    def term(self, name, handler):
        text = EditableText.load(name)
        if not text:
            text = EditableText()
            text.name = name
            text.content = name
            text.handler_name = handler.__class__.__name__
            text.line_nr = 0
            text.last_used = now()
            text.save()

        return text.content

class EText(Text, Editable):
    def __init__(self, name='', **kwargs):
        self.init(kwargs)
        self.name = self.param(name, 'text', 'Unique name for the text')

    def get_html(self, html):
        html.append('<span' + self.base_attributes + ' contenteditable="True" data-name="{}" onblur="content_changed(this);">'.format(self.name))
        html.append(self.term(self.name, html.handler) or '')
        html.append('</span>')
