from flask import Blueprint, request
from flask import render_template as _render_template

def render_template(filename, *args, **kwargs):
    """Blueprint Patched render_template. 

    If a filename is passed starting with '.', the current blueprint will
    be prepended plus an additional slash.

    This allows using duplicate filenames without worrying about rendering
    the wrong file.

    Example:

        .index.html will be converted into: <current_blueprint>/index.html

    """

    if filename.startswith('.'):
            if request.blueprint:
                # Filename started with ., expecting a blueprint relative path.
                filename = request.blueprint + "/" + filename[1:]
            else:
                # No blueprint found. Assuming this was a mistake.
                filename = filename[1:]

    return _render_template(filename, *args, **kwargs)


def monkey_patch_all():
    """Inject all boilerplate monkey patches for Flask.

    Overrides render_template: If a render_template is passed a filename
    starting with '.', the blueprint name + / will be prepended to the path.
    """

    import flask
    flask.render_template = render_template

class NestableBlueprint(Blueprint):
    """
    Hacking in support for nesting blueprints, until hopefully 
    https://github.com/mitsuhiko/flask/issues/593 will be resolved
    """

    def register_blueprint(self, blueprint, **options):
        def deferred(state):
            url_prefix = (state.url_prefix or u"") + (options.get('url_prefix', blueprint.url_prefix) or u"")
            if 'url_prefix' in options:
                del options['url_prefix']

            if self.name in state.app.template_context_processors:
                for processor in state.app.template_context_processors[self.name]:
                    blueprint.context_processor(processor)

            state.app.register_blueprint(blueprint, url_prefix=url_prefix, **options)
        self.record(deferred)

from flask.ext.classy import FlaskView as FFlaskView
from flask.ext.classy import get_true_argspec
import re


class FlaskView(FFlaskView):
    """
    Override Flask-Classy's FlaskView to provide ignoring of kwargs when converting
    them to a endpoint mapping. Allows blueprints to have dynamic arguments in them
    and allow an endpoint to catch them in it's kwargs.
    """
    @classmethod
    def register(cls, app, *args, **kwargs):
        if hasattr(app, 'expected_parameters'):
            cls.ignored_rule_args = app.expected_parameters
        
        return super(FlaskView, cls).register(app, *args,**kwargs)

    @classmethod
    def build_rule(cls, rule, method=None):
        rule_parts = []

        if cls.route_prefix:
            rule_parts.append(cls.route_prefix)

        route_base = cls.get_route_base()
        if route_base:
            rule_parts.append(route_base)

        rule_parts.append(rule)
        ignored_rule_args = ['self']
        if hasattr(cls, 'base_args'):
            ignored_rule_args += cls.base_args

        if hasattr(cls, 'ignored_rule_args'):
            ignored_rule_args += cls.ignored_rule_args

        if method:
            args = get_true_argspec(method)[0]
            for arg in args:
                if arg not in ignored_rule_args:
                    rule_parts.append("<%s>" % arg)

        result = "/%s" % "/".join(rule_parts)
        return re.sub(r'(/)\1+', r'\1', result)