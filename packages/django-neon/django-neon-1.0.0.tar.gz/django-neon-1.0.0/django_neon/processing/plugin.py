"""
Signal-based plugin-mechanism for django-neon.

A plugin can be a function defined in any other application registered in
INSTALLED_APPS.

A plugin is a signal-handler which is called when a pane gets rendered
and the pane markup-attribute is set to 'dynamic'. To write a
signal-handler use the receiver-decorator:

    from django_neon.plugin import receiver, get_dynamic_pane_content, Pane

    @receiver(get_dynamic_pane_content, sender=Pane)
    def contribute_content(sender, pane, request, **kwargs):
        content = ''
        if pane.name == 'my special pane':
            # ignore other dynamic panes
            content = str(request.META)
        return content

The signal-handler has access to all attributes of the given
Pane-instance and to the request-object. Because every signal-handler gets
called by every dynamic pane, the signal-handlers can filter for some
panes and ignoring others. This can be done by inspection of the
attributes of a pane.

The plugin-function should return html or an empty string. It is up to
you to take care that this is valid html and fits into the
html-structure of the page the pane belongs to. It's easy to break things
here, so be careful.

"""

# convenience imports
from django.dispatch import receiver  # noqa
from ..models.pane import Pane, get_dynamic_pane_content  # noqa
