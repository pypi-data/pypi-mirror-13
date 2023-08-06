from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from .utils import is_bitcoin_address_valid


class BitcoinAddressField(serializers.CharField):
    default_error_messages = {
        'invalid': _('Invalid bitcoin address.')
    }

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if not is_bitcoin_address_valid(data):
            self.fail('invalid')
        return data
