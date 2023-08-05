from impaf.controller import Controller

from .widget import FormWidget


class FormskitController(Controller):

    def add_form(
        self,
        formcls,
        name='form',
        widgetcls=FormWidget,
        *args,
        **kwargs
    ):
        form = formcls(self.request, *args, **kwargs)
        widget = widgetcls(form)
        self.add_widget(name, widget)
        return form

    def add_form_widget(self, widget, name='form', *args, **kwargs):
        form, widget = widget.from_form(self.request, *args, **kwargs)
        self.add_widget(name, widget)
        return form
