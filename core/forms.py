from django import forms
from .models import Application
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.helper import FormHelper


class ApplicationForm(forms.Form):
    application_type = forms.ChoiceField(choices=Application.Type)
    is_this_application_for_someone_else = forms.BooleanField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField(
        widget=forms.TextInput())
    birth_certificate = forms.FileField(required=True)
    national_id = forms.FileField(required=False)
    street = forms.CharField()
    suburb = forms.CharField()
    city = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Row(
                Column('application_type', css_class='form-group col-6 mb-0'),
                Column('first_name', css_class='form-group col-6 mb-0'),
                Column('last_name', css_class='form-group col-6 mb-0'),
                Column('date_of_birth', css_class='form-group col-6 mb-0'),
                Column('birth_certificate', css_class='form-group col-6 mb-0'),
                Column('national_id', css_class='form-group col-6 mb-0'),
                Column('street', css_class='form-group col-6 mb-0'),
                Column('suburb', css_class='form-group col-6 mb-0'),
                Column('city', css_class='form-group col-12 mb-0'),
                Column('is_this_application_for_someone_else',
                       css_class='form-group col-6 mb-0'),
            ),

            Submit('submit', 'Submit Application',
                   css_class='btn btn-outline-primary w-100')
        )


class UpdateApplicationForm(forms.Form):
    application_type = forms.ChoiceField(choices=Application.Type)
    is_this_application_for_someone_else = forms.BooleanField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    date_of_birth = forms.DateField(
        widget=forms.TextInput())
    birth_certificate = forms.FileField(required=False)
    national_id = forms.FileField(required=False)
    street = forms.CharField()
    suburb = forms.CharField()
    city = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()

        self.helper.layout = Layout(
            Row(
                Column('application_type', css_class='form-group col-6 mb-0'),
                Column('first_name', css_class='form-group col-6 mb-0'),
                Column('last_name', css_class='form-group col-6 mb-0'),
                Column('date_of_birth', css_class='form-group col-6 mb-0'),
                Column('birth_certificate', css_class='form-group col-6 mb-0'),
                Column('national_id', css_class='form-group col-6 mb-0'),
                Column('street', css_class='form-group col-6 mb-0'),
                Column('suburb', css_class='form-group col-6 mb-0'),
                Column('city', css_class='form-group col-12 mb-0'),
                Column('is_this_application_for_someone_else',
                       css_class='form-group col-6 mb-0'),
            ),

            Submit('submit', 'Submit Application',
                   css_class='btn btn-outline-primary w-100')
        )
