from mock import MagicMock

from impaf.application import Application

from .beaker import BeakerApplication


class MockedBeakerApplication(Application):

    def _create_config(self):
        self.config = MagicMock()
        self._create_config_runned = True


class ExampleBeakerApplication(BeakerApplication, MockedBeakerApplication):
    pass


class TestBeakerApplication(object):

    def test_create_config(self):
        app = ExampleBeakerApplication('module')
        app._create_config()

        assert app._create_config_runned
        app.config.include.assert_called_once_with('pyramid_beaker')
