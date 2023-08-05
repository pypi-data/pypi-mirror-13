# -*- coding: utf-8 -*-
from django.forms import ModelForm
from localflavor.us.forms import USPhoneNumberField

from contactbox.models import Message


class ContactForm(ModelForm):
    phone = USPhoneNumberField(required=False, label='Phone')

    class Meta:
        model = Message
        fields = ('name', 'email', 'organization', 'phone', 'message')
