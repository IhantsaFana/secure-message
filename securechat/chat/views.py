import base64
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from .models import EncryptedMessage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

class SendEncryptedMessage(APIView):
    def post(self, request):
        recipient_id = request.data.get('recipient')
        message = request.data.get('message')

        try:
            recipient = User.objects.get(id=recipient_id)
            recipient_public_key = serialization.load_pem_public_key(
                recipient.public_key.encode()  # Assure-toi que ce champ existe et est bien une clé PEM
            )

            # Génère une clé AES aléatoire (256 bits)
            aes_key = os.urandom(32)

            # Génère un IV (Initialisation Vector)
            iv = os.urandom(16)

            # Chiffre le message
            cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
            encryptor = cipher.encryptor()

            # Padding du message à un multiple de 16 (CBC nécessite un bloc multiple)
            from cryptography.hazmat.primitives import padding as sym_padding
            padder = sym_padding.PKCS7(128).padder()
            padded_data = padder.update(message.encode()) + padder.finalize()

            encrypted_message = encryptor.update(padded_data) + encryptor.finalize()

            # Chiffre la clé AES avec la clé publique du destinataire (RSA)
            encrypted_aes_key = recipient_public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Enregistre le message
            EncryptedMessage.objects.create(
                sender=request.user,
                recipient=recipient,
                encrypted_message=base64.b64encode(encrypted_message).decode(),
                encrypted_aes_key=base64.b64encode(encrypted_aes_key).decode(),
                iv=base64.b64encode(iv).decode(),
            )

            return Response({'status': 'Message sent & encrypted ✅'}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': 'Recipient not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReadEncryptedMessages(APIView):
    def get(self, request):
        user = request.user

        # Si on a stocké la clé privée déchiffrée (en mémoire ou dans la DB temporairement)
        try:
            private_key = serialization.load_pem_private_key(
                user.decrypted_private_key.encode(),  # 🔐 doit être disponible en texte PEM
                password=None,
            )

            messages = EncryptedMessage.objects.filter(recipient=user)
            result = []

            for msg in messages:
                # Décodage base64
                encrypted_aes_key = base64.b64decode(msg.encrypted_aes_key)
                iv = base64.b64decode(msg.iv)
                encrypted_message = base64.b64decode(msg.encrypted_message)

                # 🔓 Déchiffre la clé AES avec la clé privée RSA
                aes_key = private_key.decrypt(
                    encrypted_aes_key,
                    asym_padding.OAEP(
                        mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                # 🔓 Déchiffre le message AES
                cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
                decryptor = cipher.decryptor()
                padded_plaintext = decryptor.update(encrypted_message) + decryptor.finalize()

                # Retire le padding
                unpadder = sym_padding.PKCS7(128).unpadder()
                plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

                result.append({
                    'from': msg.sender.username,
                    'message': plaintext.decode(),
                    'received_at': msg.created_at
                })

            return Response(result, status=200)

        except Exception as e:
            return Response({'error': f'Erreur de déchiffrement : {str(e)}'}, status=500)
