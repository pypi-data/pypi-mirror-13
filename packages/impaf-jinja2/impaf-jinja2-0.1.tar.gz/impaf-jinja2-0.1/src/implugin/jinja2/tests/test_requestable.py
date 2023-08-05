from mock import MagicMock

from pytest import fixture
from pyramid_jinja2 import IJinja2Environment

from impaf.testing import RequestFixture

from ..requestable import Jinja2Requestable


class TestJinja2Requestable(RequestFixture):

    @fixture
    def obj(self, mrequest):
        obj = Jinja2Requestable()
        obj.request = mrequest
        return obj

    def test_jinja2(self, obj, mrequest):
        mrequest.registry = MagicMock()

        assert obj.jinja2 == mrequest.registry.queryUtility.return_value
        mrequest.registry.queryUtility.assert_called_once_with(
            IJinja2Environment,
            name='.jinja2',
        )
