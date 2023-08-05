from impaf.controller import Controller

from .resources import Resources


class FanstaticController(Controller):

    def _generate_resources(self):
        self.resources = Resources()

    def _create_context(self):
        super()._create_context()
        self._generate_resources()
        self.context['need'] = self.resources.need
