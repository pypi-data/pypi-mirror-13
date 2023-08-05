import builtins
from mock import MagicMock
from mock import patch

from pytest import fixture
from pytest import raises
from pytest import yield_fixture

from ..resources import ModuleNotFound
from ..resources import NameNotKnowError
from ..resources import Resources

example_resource = MagicMock()


class TestResources(object):

    @fixture
    def resources(self):
        return Resources()

    @yield_fixture
    def m_is_resource(self, resources):
        patcher = patch.object(resources, '_is_resource')
        with patcher as mock:
            yield mock

    def test_needing_wrong_name(self, resources):
        with raises(NameNotKnowError):
            resources.need('name')

    def test_needing_missing_url(self, resources):
        resources.add_resource('name', 'very.wrong.url:something')
        with raises(ModuleNotFound):
            resources.need('name')

    def test_needing_good_but_empty_url(self, resources):
        resources.add_resource('name', 'os.path:something')
        with raises(ModuleNotFound):
            resources.need('name')

    def test_needing_good_url(self, resources):
        resources.add_resource(
            'name',
            'implugin.fanstatic.tests.test_resources:example_resource',
        )
        example_resource.reset_mock()

        resources.need('name')

        example_resource.need.assert_called_once_with()

    def test_needing_lib(self, resources, m_is_resource):
        m_is_resource.return_value = True
        resources.add_resource(
            'name',
            example_resource,
        )
        example_resource.reset_mock()

        resources.need('name')

        example_resource.need.assert_called_once_with()
