import base64
import hashlib
import ed25519


def generate_keys():
    # Heh, I can use private and public so freely in Python.
    private, public = ed25519.create_keypair()

    return (private.to_ascii(encoding="hex").decode("ascii"),
            public.to_ascii(encoding="hex").decode("ascii"))


def sign(message: str, private: str):
    signing_key = ed25519.SigningKey(private.encode('ascii'), encoding="hex")
    sign_bytes = signing_key.sign(message.encode(), encoding="hex")
    return sign_bytes.decode('ascii')


def verify(message, public: str, signature: str):
    try:
        vk = ed25519.VerifyingKey(public.encode('ascii'), encoding="hex")
        vk.verify(signature.encode('ascii'),
                  message.encode(),
                  encoding="hex")

        return True
    except ed25519.BadSignatureError:
        return False
