from mock import patch
from mock import sentinel

from pytest import fixture
from pytest import yield_fixture

from impaf.application import Application

from ..application import FanstaticApplication


class MockedFanstaticApplication(Application):

    def _return_wsgi_app(self):
        return sentinel.wsgi_application


class ExampleFanstaticApplication(
    FanstaticApplication,
    MockedFanstaticApplication,
):
    pass


class TestFanstaticApplication(object):

    @fixture
    def application(self):
        return ExampleFanstaticApplication('module')

    @yield_fixture
    def mFanstatic(self):
        patcher = patch('implugin.fanstatic.application.Fanstatic')
        with patcher as mock:
            yield mock

    def test_wsgi_app(self, application, mFanstatic):
        """
        Fanstatic shuld wrap a wsgi application.
        """
        application.settings = {
            'fanstatic': {'data': 'something'},
        }

        application._return_wsgi_app() == mFanstatic.return_value
        mFanstatic.assert_called_once_with(
            sentinel.wsgi_application,
            data='something',
        )
