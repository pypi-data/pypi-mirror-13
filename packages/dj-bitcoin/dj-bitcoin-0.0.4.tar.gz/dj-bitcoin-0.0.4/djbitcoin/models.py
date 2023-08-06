from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .utils import is_bitcoin_address_valid


def validate_address(value):
    if not is_bitcoin_address_valid(value):
        raise ValidationError(_('Not a valid bitcoin address.'))


class BitcoinAddressField(models.CharField):
    description = 'A bitcoin address'

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 36
        super().__init__(*args, **kwargs)
        self.validators.append(validate_address)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs
