from django import forms

class JobForm(forms.Form):
    pdb_file = forms.FileField()
    name = forms.CharField(label='Job name', max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(label='E-mail', required=False, help_text='Optional')
    ph_range = forms.BooleanField(label='Use pH Range', required=False, help_text='Check if you want to run on a pH range from 2 to 12, with 0.5 step')
    ph = forms.DecimalField(label='pH', max_digits=2, decimal_places=1, min_value=0, max_value=14)
    temperature = forms.DecimalField(label='Temperature', max_digits=10, decimal_places=2, min_value=0)
