from pyramid.session import check_csrf_token

from implugin.beaker import BeakerRequestable

from formskit import Form
from formskit.formvalidators import FormValidator


class PostForm(Form, BeakerRequestable):

    def __init__(self, request):
        self.feed_request(request)
        super().__init__()

        self.add_form_validator(CsrfMustMatch())

    def reset(self):
        super().reset()
        self.init_csrf()

    def init_csrf(self):
        self.add_field('csrf_token')
        self.set_value('csrf_token', self.session.get_csrf_token())

    def validate(self):
        return super().validate(self.POST.dict_of_lists())


class CsrfMustMatch(FormValidator):

    message = "CSRF token do not match!"

    def validate(self):
        self.form.POST['csrf_token'] = self.form.get_value('csrf_token')
        return check_csrf_token(self.form.request, raises=False)
