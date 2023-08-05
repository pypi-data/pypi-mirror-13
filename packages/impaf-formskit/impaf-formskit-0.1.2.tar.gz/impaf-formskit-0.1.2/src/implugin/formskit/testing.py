from mock import patch

from pytest import fixture
from pytest import yield_fixture

from impaf.testing import ControllerCase
from impaf.testing import ControllerFixture
from impaf.testing import RequestFixture
from impaf.testing import cache


class FormskitControllerFixture(ControllerFixture):

    @yield_fixture
    def madd_form(self, testable):
        patcher = patch.object(testable, 'add_form')
        with patcher as mock:
            yield mock

    @fixture
    def fform(self, madd_form):
        return madd_form.return_value


class FormFixture(RequestFixture):

    @fixture
    def testable(self, mrequest, registry):
        return self._testable_cls(mrequest)


class FormskitControllerCase(ControllerCase):

    @cache
    def madd_form(self):
        return self.pobject(self.object(), 'add_form')

    @cache
    def madd_form_widget(self):
        return self.pobject(self.object(), 'add_form_widget')

    @cache
    def mform(self):
        return self.madd_form().return_value

    @cache
    def mform_widget(self):
        return self.madd_form_widget().return_value
