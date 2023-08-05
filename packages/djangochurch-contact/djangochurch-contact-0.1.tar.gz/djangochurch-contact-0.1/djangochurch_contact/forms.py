from django import forms
from django.conf import settings


ANTI_SPAM = getattr(settings, 'CONTACT_ANTISPAM', 'human')


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.widgets.Textarea)
    anti_spam = forms.RegexField(
        regex='^(?i)%s$' % (ANTI_SPAM,),
        help_text='Please enter <strong>%s</strong> in the field above' % (ANTI_SPAM,))

    error_css_class = 'error'
    required_css_class = 'required'
