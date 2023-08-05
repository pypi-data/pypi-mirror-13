from implugin.jinja2 import Jinja2Application


class HamlApplication(Jinja2Application):

    def _create_jinja2_settings(self):
        super()._create_jinja2_settings()
        self.settings['jinja2.extensions'].append(
            'hamlish_jinja.HamlishExtension'
        )

    def _generate_registry(self, registry):
        super()._generate_registry(registry)
        self.config.add_jinja2_renderer('.haml')
