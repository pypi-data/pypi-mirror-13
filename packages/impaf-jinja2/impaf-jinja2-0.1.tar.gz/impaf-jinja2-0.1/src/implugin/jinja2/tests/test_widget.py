from mock import MagicMock
from mock import sentinel
from mock import patch

from pytest import fixture
from pytest import yield_fixture

from impaf.widget import Widget

from ..widget import BaseWidget
from ..widget import SingleWidget
from ..widget import MultiWidget


class MockedBaseWidget(Widget):

    pass


class FakeBaseWidget(BaseWidget, MockedBaseWidget):

    pass


class TestBaseWidget(object):

    @fixture
    def widget(self):
        return FakeBaseWidget()

    @fixture
    def mrequest(self, widget):
        request = MagicMock()
        widget.request = request
        return request

    @fixture
    def mjinja2(self, widget, mrequest):
        return mrequest.registry.queryUtility.return_value

    @yield_fixture
    def mMarkup(self):
        patcher = patch('implugin.jinja2.widget.Markup')
        with patcher as mock:
            yield mock

    def test_render(self, widget, mjinja2, mMarkup):
        """
        .render should render template from template link
        """
        template = 'url.to.module:template.jinja2'
        context = {'my': 'context'}
        widget.context = context

        markup = widget.render(template)

        mjinja2.get_template.assert_called_once_with(template)
        template = mjinja2.get_template.return_value
        template.render.assert_called_once_with(**context)
        mMarkup.assert_called_once_with(template.render.return_value)
        assert markup == mMarkup.return_value


class ExampleSingleWidget(SingleWidget):
    template = 'link to template'

    def make(self, arg, kw):
        super().make()
        self.context = {
            'arg': arg,
            'kw': kw,
        }


class TestSingleWidget(object):

    @fixture
    def widget(self):
        return ExampleSingleWidget()

    @yield_fixture
    def mrender(self, widget):
        patcher = patch.object(widget, 'render')
        with patcher as mock:
            yield mock

    def test_simple(self, widget, mrender):
        widget('arg', kw='kwarg')

        assert widget.context == {
            'arg': 'arg',
            'kw': 'kwarg',
        }
        mrender.assert_called_once_with(widget.template)


class TestMultiWidget(object):

    @fixture
    def widget(self):
        return MultiWidget()

    @yield_fixture
    def mrender(self, widget):
        patcher = patch.object(widget, 'render')
        with patcher as mock:
            yield mock

    def test_get_template_when_no_self_prefix(self, widget):
        assert widget.get_template('myname', 'p1') == 'p1/myname'

    def test_get_template_when_self_prefix(self, widget):
        widget.prefix = 'p2'
        assert widget.get_template('myname') == 'p2/myname'

    def test_render_for(self, widget, mrender):
        widget.request = sentinel.request
        widget.context = {'old': sentinel.old}
        widget.render_for('mytemplate', {'mycontext': sentinel.new})

        assert widget.context == {
            'request': sentinel.request,
            'mycontext': sentinel.new,
            'widget': widget,
        }
        mrender.assert_called_once_with('mytemplate')
