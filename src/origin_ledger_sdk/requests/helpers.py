
from bip32utils import BIP32Key
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory, Signer
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey as PrivateKey


def get_signer(signer_key: BIP32Key) -> Signer:
    context = create_context('secp256k1')
    private_key = PrivateKey.from_bytes(signer_key.PrivateKey())
    return CryptoFactory(context).new_signer(private_key)   
