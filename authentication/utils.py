from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.conf import settings

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active) + settings.TOKEN_GENERATOR_SECRET_KEY
        )

generate_token = TokenGenerator()