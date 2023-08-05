from __future__ import unicode_literals

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView

from .forms import ContactForm


class BaseFormView(FormView):
    email_recipients = None
    email_subject = 'Contact Form'
    email_reply_to = None

    def form_valid(self, form):
        # Build up the email here, so any number of fields can be added
        form_data = []

        for field in form:
            form_data.append('%s: %s' % (field.label, field.data))

        body = '\n'.join(form_data)
        subject = '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, self.email_subject)

        # Default to managers if no recipients are specified
        recipients = self.email_recipients or [x[1] for x in settings.MANAGERS]

        # Get a decent reply-to address if we can
        reply_to = form.cleaned_data.get(self.email_reply_to, None)

        if reply_to is not None:
            reply_to = [reply_to]

        mail = EmailMessage(subject=subject, body=body, to=recipients, reply_to=reply_to)
        mail.send()

        return super(BaseFormView, self).form_valid(form)


class ContactFormView(BaseFormView):
    form_class = ContactForm
    email_reply_to = 'email'
    template_name = 'contact/form.html'
    success_url = reverse_lazy('contact:form-thanks')
