from mock import MagicMock

from impaf.testing import ControllerCase
from impaf.testing import PyTestCase

from ..controller import FormskitController


class TestFlashMessageController(ControllerCase, PyTestCase):

    _object_cls = FormskitController

    def test_add_form(self):
        formcls = MagicMock()
        widgetcls = MagicMock()
        madd_widget = self.madd_widget()

        form = self.object().add_form(
            formcls,
            'myname',
            widgetcls,
            'arg',
            kw='arg',
        )

        formcls.assert_called_once_with(self.mrequest(), 'arg', kw='arg')
        form = formcls.return_value
        widgetcls.assert_called_once_with(form)
        madd_widget.assert_called_once_with('myname', widgetcls.return_value)
