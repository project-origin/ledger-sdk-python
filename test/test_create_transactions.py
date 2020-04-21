
import unittest
import pytest
import random
import string

from datetime import datetime
from bip32utils import BIP32Key

from sawtooth_signing import create_context
from src.origin_ledger_sdk.requests.helpers import get_signer
from src.origin_ledger_sdk import Batch, PublishMeasurementRequest, MeasurementType,IssueGGORequest, TransferGGORequest, SplitGGOPart, SplitGGORequest, RetireGGORequest, generate_address, AddressPrefix, RetireGGOPart


def randomString(stringLength=32):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))



class TestLedger(unittest.TestCase):


    @pytest.mark.unittest
    def test_sign_with_bip32(self):
        context = create_context('secp256k1')

        key = BIP32Key.fromEntropy("bfdgafgaertaehtaha43514r<aefag".encode())
        signer = get_signer(key.PrivateKey())

        signed_message = signer.sign("Hello world".encode())
        self.assertEqual(signed_message, '01799dd2268934d11fcc95a164fb1b32c4a0da3284461890838f31f48e37917c532174048672ba1b0f028e5d74943966e799acadd41c7aa433fcf254e794fbed')

        result = context.verify(signed_message, "Hello world".encode(), signer.get_public_key())
        self.assertEqual(result, True)
        

    @pytest.mark.unittest
    def test_build_publish_measurement_request(self):
        key = BIP32Key.fromEntropy("bfdgafgaertaehtaha43514r<aefag".encode())

        address = generate_address(AddressPrefix.MEASUREMENT, key.PublicKey())

        request = PublishMeasurementRequest(
            address=address,
            begin=datetime(2020,1,1,12),
            end=datetime(2020,1,1,12),
            sector='DK1',
            type=MeasurementType.PRODUCTION,
            amount=1244
        )

        batch = Batch(signer_private_key=key.PrivateKey())
        batch.add_request(request)
        batch.get_signed_batch()

        
    @pytest.mark.unittest
    def test_build_issue_ggo_request(self):
        key = BIP32Key.fromEntropy("bfdgafgaertaehtaha43514r<aefag".encode())
        
        mea_address = generate_address(AddressPrefix.MEASUREMENT, key.PublicKey())
        ggo_address = generate_address(AddressPrefix.GGO, key.PublicKey())

        request = IssueGGORequest(
            measurement_address=mea_address,
            ggo_address=ggo_address,
            tech_type="T12412",
            fuel_type="F123123"
        )

        batch = Batch(signer_private_key=key.PrivateKey())
        batch.add_request(request)
        batch.get_signed_batch()

       
    @pytest.mark.unittest
    def test_build_transfer_ggo_request(self):
        owner_key = BIP32Key.fromEntropy("bfdgafgaertaehtaha43514r<aefag".encode())
        receipent_key = BIP32Key.fromEntropy("bfasdfasdfasdgasdgasdgqwerhrjnr".encode())

        source_add = generate_address(AddressPrefix.GGO, owner_key.PublicKey())
        receipient_add = generate_address(AddressPrefix.GGO, receipent_key.PublicKey())
    
        request = TransferGGORequest(
            source_private_key=owner_key.PrivateKey(),
            source_address=source_add,
            destination_address=receipient_add,
        )

        batch = Batch(signer_private_key=owner_key.PrivateKey())
        batch.add_request(request)
        batch.get_signed_batch()

        
    @pytest.mark.unittest
    def test_build_split_ggo_request(self):
        master_key = BIP32Key.fromEntropy("bfdgafgaertaehtaha43514r<aefag".encode())

        key_1 = master_key.ChildKey(1)
        key_2 = master_key.ChildKey(2)
        key_3 = master_key.ChildKey(3)
        

        request = SplitGGORequest(
            source_private_key=key_1.PrivateKey(),
            source_address=generate_address(AddressPrefix.GGO, key_1.PublicKey()),
            parts=[
                SplitGGOPart(address=generate_address(AddressPrefix.GGO, key_2.PublicKey()), amount=124),
                SplitGGOPart(address=generate_address(AddressPrefix.GGO, key_3.PublicKey()), amount=124)
            ]
        )

        batch = Batch(signer_private_key=master_key.PrivateKey())
        batch.add_request(request)
        batch.get_signed_batch()

               
    @pytest.mark.unittest
    def test_build_retire_ggo_request(self):
        key = BIP32Key.fromEntropy("bfdgafgaertaehtaha43514r<aefag".encode())

        measurement_key = key.ChildKey(1)
        mea_address = generate_address(AddressPrefix.MEASUREMENT, measurement_key.PublicKey())
        set_address = generate_address(AddressPrefix.SETTLEMENT, measurement_key.PublicKey())

        ggo_key = key.ChildKey(2)
        ggo_address = generate_address(AddressPrefix.GGO, ggo_key.PublicKey())

        request = RetireGGORequest(
            measurement_address=mea_address,
            measurement_private_key=measurement_key.PrivateKey(),
            settlement_address=set_address,
            parts=[
                RetireGGOPart(
                    address=ggo_address,
                    private_key=ggo_key.PrivateKey()
                )
            ]
        )

        batch = Batch(signer_private_key=key.PrivateKey())
        batch.add_request(request)
        batch.get_signed_batch()
