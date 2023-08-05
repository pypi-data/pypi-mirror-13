from pyramid_jinja2 import IJinja2Environment

from impaf.requestable import Requestable


class Jinja2Requestable(Requestable):

    @property
    def jinja2(self):
        return self._get_jinja2_envoritment()

    def _get_jinja2_envoritment(self):
        return self.registry.queryUtility(IJinja2Environment, name='.jinja2')
