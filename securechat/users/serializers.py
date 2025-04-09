from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password
from .utils import generate_rsa_key_pair, encrypt_private_key

from django.contrib.auth import authenticate
from .models import CustomUser
from .utils import decrypt_private_key
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data.get('email', '')

        # Génération de la paire RSA
        private_key, public_key = generate_rsa_key_pair()
        private_key_encrypted = encrypt_private_key(private_key, password)

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            public_key=public_key.decode(),
            private_key_encrypted=private_key_encrypted
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError('Invalid credentials')

        # Déchiffrement de la clé privée RSA
        try:
            private_key = decrypt_private_key(user.private_key_encrypted, password)
        except Exception as e:
            raise serializers.ValidationError('Unable to decrypt private key: ' + str(e))

        # Génère un token
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'private_key': private_key.decode()  # optionnel, à sécuriser selon l’usage
        }
