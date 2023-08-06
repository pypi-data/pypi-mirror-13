import django
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.utils.safestring import mark_safe

_render = ForeignKeyRawIdWidget.render

def render_with_link(self, name, value, attrs=None):
    html = _render(self, name, value, attrs)
    if value:
        lbl = self.label_for_value(value)
        url = '../../../%s/%s/%s/' % (self.rel.to._meta.app_label, self.rel.to._meta.object_name.lower(), value)
        link = u'<a href="%s">%s</a>' % (url, lbl)
        html = mark_safe(html.replace(lbl, link))
    return html

ForeignKeyRawIdWidget.render = render_with_link