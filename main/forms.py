from django import forms

class JobForm(forms.Form):
    pdb_file = forms.FileField()
    name = forms.CharField(label='Job name', max_length=30, required=False)
    email = forms.EmailField(label='E-mail', required=False)
    ph_range = forms.BooleanField(label='Use pH Range', required=False)
    ph = forms.DecimalField(label='pH', max_digits=2, decimal_places=1)    
    temperature = forms.DecimalField(label='Temperature', max_digits=10, decimal_places=2)
