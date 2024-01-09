from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from django.contrib.auth.models import User

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self):
        token = (
            six.text_type(4) + six.text_type(726484072) +
            six.text_type(False) + "63635d5d44a61d6e9be3de16fd47ec0f5fc91864dc1c3aaffffd81f0284c2118"
        )
        print(f'token {token}') 
        return token

generate_token = TokenGenerator()

print(generate_token.make_token(User.objects.get(email="admin@admin")))