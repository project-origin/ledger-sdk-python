

import unittest
import random
import string

from datetime import datetime, timezone
from bip32utils import BIP32Key

from sawtooth_signing import create_context

from src.ledger import Ledger, Batch, PublishMeasurementRequest, MeasurementDirection, BatchStatus, IssueGGORequest #, TransferGGORequest, SplitGGOPart, SplitGGORequest


def randomString(stringLength=32):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


from src.ledger.requests.helpers import get_signer

class TestLedger(unittest.TestCase):

    def setUp(self):
        self.ledger = Ledger('http://localhost:8008')


    def test_sign_with_bip32(self):
        context = create_context('secp256k1')

        key = BIP32Key.fromEntropy("bfdgafgaertaehtaha43514r<aefag".encode())
        signer = get_signer(key)

        signed_message = signer.sign("Hello world".encode())
        self.assertEqual(signed_message, '01799dd2268934d11fcc95a164fb1b32c4a0da3284461890838f31f48e37917c532174048672ba1b0f028e5d74943966e799acadd41c7aa433fcf254e794fbed')

        result = context.verify(signed_message, "Hello world".encode(), signer.get_public_key())
        self.assertEqual(result, True)
        

    def test_ledger_get_measurement(self):


        measurement = self.ledger.get_measurement_from_address('5a98391d0968501bedc7539d79b6084a7c3b2e2a0eea63989383b3f312f3973174a078')

        self.assertEqual(measurement.address, '5a98391d0968501bedc7539d79b6084a7c3b2e2a0eea63989383b3f312f3973174a078')
        self.assertEqual(measurement.amount, 5123)
        self.assertEqual(measurement.sector, 'DK1')
        self.assertEqual(measurement.direction, MeasurementDirection.CONSUMPTION)
        self.assertEqual(measurement.begin, datetime(2020,1,1,12, tzinfo=timezone.utc))
        self.assertEqual(measurement.end,  datetime(2020,1,1,13, tzinfo=timezone.utc))
        self.assertEqual(measurement.key, '03c50162209fda62f0bfee5c4a5e18a156db331810ee5ff8ddc35cbfb89cb18c93')


    def test_publish_and_read_measurement(self):

        key = BIP32Key.fromEntropy(randomString().encode())
        child_key = key.CKDpub(1)
        
        batch = Batch(key)

        batch.add_request(PublishMeasurementRequest(
            extended_key=child_key,
            begin=datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc),
            end=datetime(2020, 1, 1, 13, 0, tzinfo=timezone.utc),
            sector='DK1',
            direction=MeasurementDirection.CONSUMPTION,
            amount=5123))

        batch.add_request(IssueGGORequest(
            extended_key=child_key,
            tech_type="T0124",
            fuel_type="F2345"))

        handle = self.ledger.execute_batch(batch)

        print(handle)
        status = BatchStatus.PENDING
        while status == BatchStatus.PENDING:
            batch_status = self.ledger.get_batch_status(handle)
            status = batch_status.data[0].status

        self.assertEqual(status, BatchStatus.COMMITTED)

        # Try to get the committed measurement
        measurement = self.ledger.get_measurement_from_key(child_key)

        self.assertEqual(measurement.begin, datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(measurement.end, datetime(2020, 1, 1, 13, 0, tzinfo=timezone.utc))
        self.assertEqual(measurement.sector, 'DK1')
        self.assertEqual(measurement.direction, MeasurementDirection.CONSUMPTION)
        self.assertEqual(measurement.amount, 5123)
        self.assertEqual(measurement.key, child_key.PublicKey().hex())


    # A lot more tests are still required.

    # def test_issue_ggo(self):
    #     key = BIP32Key.fromEntropy(randomString().encode())
    #     child_key = key.CKDpub(1)


    #     handle = publish_measurement(
    #         child_key,
    #         begin=datetime(2020, 1, 1, 12, 0, tzinfo=timezone.utc),
    #         end=datetime(2020, 1, 1, 13, 0, tzinfo=timezone.utc),
    #         sector='DK1',
    #         direction=Direction.PRODUCTION,
    #         amount=123)

    #     print(handle)
    #     status = Status.PENDING
    #     while status == Status.PENDING:
    #         status = get_status(handle)

    #     self.assertEqual(status, Status.COMMITTED)

    #     handle = issue_ggo(
    #         child_key, 
    #         'T020002',
    #         'F01050100')
            
    #     status = Status.PENDING
    #     while status == Status.PENDING:
    #         status = get_status(handle)

    #     self.assertEqual(status, Status.COMMITTED)



        



