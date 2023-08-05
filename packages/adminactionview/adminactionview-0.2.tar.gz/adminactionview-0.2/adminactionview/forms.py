from django import forms


class IntermediateAdminForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
