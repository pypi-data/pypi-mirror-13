from mock import MagicMock

from pytest import fixture

from implugin.jinja2 import Jinja2Application

from .haml import HamlApplication


class MockedHamlApplication(Jinja2Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flags = {}
        self.settings = {}
        self.config = MagicMock()

    def _create_jinja2_settings(self):
        self.flags['_create_jinja2_settings'] = True

    def _generate_registry(self, registry):
        self.flags['_generate_registry'] = True


class ExampleHamlApplication(HamlApplication, MockedHamlApplication):
    pass


class TestHamlApplication(object):

    @fixture
    def application(self):
        return ExampleHamlApplication('module')

    def test_create_jinja2_settings(self, application):
        application.settings['jinja2.extensions'] = []

        application._create_jinja2_settings()

        assert application.flags['_create_jinja2_settings'] is True
        assert application.settings == {
            'jinja2.extensions': ['hamlish_jinja.HamlishExtension']
        }

    def test_generate_registry(self, application):
        registry = {}
        application._generate_registry(registry)

        assert registry == {}
        assert application.flags['_generate_registry'] is True
        application.config.add_jinja2_renderer.assert_called_once_with('.haml')
