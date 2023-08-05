from mock import MagicMock

from formskit import Form

from impaf.testing import RequestCase
from impaf.testing import PyTestCase
from impaf.testing import cache

from ..models import PostForm
from ..models import CsrfMustMatch


class MockedPostForm(Form):

    @property
    @cache('instance')
    def reset(self):
        return MagicMock()

    @property
    @cache('instance')
    def validate(self):
        return MagicMock()


class ExamplePostForm(PostForm, MockedPostForm):

    def _get_request_cls(self):
        return lambda x: x


class TestFlashMessageController(RequestCase, PyTestCase):

    _object_cls = ExamplePostForm

    @cache
    def object(self):
        return super().object(self.mrequest())

    @cache
    def madd_form_validator(self):
        return self.pobject(PostForm, 'add_form_validator')

    @cache
    def minit_csrf(self):
        return self.pobject(PostForm, 'init_csrf')

    @cache
    def mCsrfMustMatch(self):
        return self.patch('implugin.formskit.models.CsrfMustMatch')

    def test_init(self):
        add_form_validator = self.madd_form_validator()
        init_csrf = self.minit_csrf()
        CsrfMustMatch = self.mCsrfMustMatch()

        obj = self.object()

        add_form_validator.assert_called_once_with(CsrfMustMatch.return_value)
        init_csrf.assert_called_once_with()

    def test_reset(self):
        self.mregistry()
        obj = self.object()
        init_csrf = self.minit_csrf()
        super(PostForm, obj).reset.reset_mock()

        obj.reset()

        super(PostForm, obj).reset.assert_called_once_with()

        init_csrf.assert_called_once_with()

    def test_validate(self):
        post = self.mPOST()
        obj = self.object()

        result = obj.validate()

        assert result == super(PostForm, obj).validate.return_value
        post.dict_of_lists.assert_called_once_with
        super(PostForm, obj).validate.assert_called_once_with(
            post.dict_of_lists.return_value
        )


class TestCsrfMustMatch(RequestCase, PyTestCase):

    _object_cls = CsrfMustMatch

    @cache
    def mform(self):
        obj = MagicMock()
        obj.POST = self.mPOST()
        return obj

    @cache
    def object(self):
        obj = super().object()
        obj.set_form(self.mform())
        return obj

    @cache
    def mcheck_csrf_token(self):
        return self.patch('implugin.formskit.models.check_csrf_token')

    def test_validate(self):
        post = self.mPOST()
        form = self.mform()
        check_csrf_token = self.mcheck_csrf_token()
        obj = self.object()

        assert obj.validate() == check_csrf_token.return_value

        assert post['csrf_token'] == form.get_value.return_value
        form.get_value.assert_called_once_with('csrf_token')
        check_csrf_token.assert_called_once_with(form.request, raises=False)
