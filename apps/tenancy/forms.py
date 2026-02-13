from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div
from .models import Tenant, TenantDomain, TenantSetting

class TenantForm(forms.ModelForm):
    """Form for managing tenants"""

    class Meta:
        model = Tenant
        fields = ["name", "code", "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("name"),
                Field("code"),
                Field("status"),
                Submit("submit", "Save Tenant"),
            )
        )


class TenantDomainForm(forms.ModelForm):
    """Form for managing tenant domains"""

    class Meta:
        model = TenantDomain
        fields = ["domain", "is_primary"]

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("domain"),
                Div(
                    Field("is_primary"),
                    css_class="form-check"
                ),
                Submit("submit", "Save Domain"),
            )
        )


class TenantSettingForm(forms.ModelForm):
    """Form for managing tenant settings"""

    class Meta:
        model = TenantSetting
        fields = ["key", "value"]

    def __init__(self, *args, **kwargs):
        self.tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("key"),
                Div(
                    Field("value"),
                    css_class="form-group"
                ),
                Submit("submit", "Save Setting"),
            )
        )
