from flask import render_template_string, Markup

from wtforms_webwidgets.bootstrap import default_widgets
from wtforms_webwidgets import FieldRenderer

renderer = FieldRenderer(default_widgets)

def render_field(field, **kwargs):
    """
    Returns a rendered field using the boilerplate's field renderer.

    :param field: A wtforms.field to render
    :param kwargs: Arguments to render with.
    """
    return renderer(field, **kwargs)


def csrf_setup(**kwargs):
    """
    Return the CSRF setup global for injection into jinja templates.
    """
    template = """
    {% if config.CSRF_ENABLED %}
    <script>
    var csrftoken = "{{ csrf_token() }}"

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken)
            }
        }
    });
    </script>
    {% endif %}
    """
    return Markup(render_template_string(template, **kwargs))