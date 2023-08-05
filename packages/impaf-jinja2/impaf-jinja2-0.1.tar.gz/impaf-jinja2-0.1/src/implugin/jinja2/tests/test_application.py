from mock import MagicMock

from pytest import fixture

from impaf.application import Application

from ..application import Jinja2Application


class MockedApplication(Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = {}
        self.config = MagicMock()
        self.settings = {}

    def _create_config(self):
        self.flags['_create_config'] = True


class FakeJinja2Application(Jinja2Application, MockedApplication):
    pass


class TestJinja2Application(object):

    @fixture
    def application(self):
        return FakeJinja2Application('module')

    def test_create_config(self, application):
        application._create_config()

        assert application.flags['_create_config'] is True
        application.config.include.assert_called_once_with('pyramid_jinja2')
        assert application.settings['jinja2.extensions'] == []
