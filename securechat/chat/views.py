from rest_framework import generics, permissions
from .models import Message
from .serializers import MessageSerializer
from crypto.utils import encrypt_message
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message
from .serializers import MessageSerializer
from users.utils import decrypt_aes_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        plaintext = self.request.data.get("message")
        aes_key = settings.SECRET_KEY[:32].encode()  # ⚠️ À remplacer par vraie clé AES dans la version finale

        content_encrypted, iv, tag = encrypt_message(aes_key, plaintext)

        serializer.save(
            sender=self.request.user,
            content_encrypted=content_encrypted,
            iv=iv,
            hmac=tag,
        )

class InboxView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user).order_by('-timestamp')


class DecryptMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, message_id):
        try:
            # Récupérer le message
            message = Message.objects.get(id=message_id)
            
            # Assurer que l'utilisateur est bien le destinataire du message
            if message.recipient != request.user:
                return Response({"detail": "Vous n'êtes pas le destinataire de ce message."}, status=403)

            # Déchiffrer la clé AES
            encrypted_aes_key_b64 = message.aes_key  # La clé AES chiffrée
            private_key_pem = request.user.private_key  # La clé privée RSA de l'utilisateur

            aes_key = decrypt_aes_key(encrypted_aes_key_b64, private_key_pem)

            # Déchiffrer le message avec la clé AES
            iv = b64decode(message.iv)  # L'IV est nécessaire pour le déchiffrement
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            # Déchiffrement du contenu du message
            padded_message = decryptor.update(b64decode(message.content)) + decryptor.finalize()

            # Suppression du padding PKCS7
            unpadder = padding.PKCS7(128).unpadder()
            decrypted_message = unpadder.update(padded_message) + unpadder.finalize()

            return Response({
                "message": decrypted_message.decode('utf-8')
            })

        except Message.DoesNotExist:
            return Response({"detail": "Message non trouvé."}, status=404)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
