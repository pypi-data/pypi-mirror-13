from jinja2 import Markup

from impaf.widget import Widget

from .requestable import Jinja2Requestable


class BaseWidget(Widget, Jinja2Requestable):

    def render(self, template):
        template = self.jinja2.get_template(template)
        return Markup(template.render(**self.context))


class SingleWidget(BaseWidget):

    def get_template(self):
        return self.template

    def __call__(self, *args, **kwargs):
        self.make(*args, **kwargs)
        return self.render(self.get_template())

    def make(self):
        pass


class MultiWidget(BaseWidget):

    prefix = None

    def get_template(self, name, prefix=None):
        args = []
        prefix = prefix or self.prefix
        if prefix:
            args.append(prefix)
        args.append(name)
        return '/'.join(args)

    def render_for(self, name, context, prefix=None):
        self._create_context()
        self.context.update(context)
        return self.render(self.get_template(name, prefix=prefix))
