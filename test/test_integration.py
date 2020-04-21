import unittest
import pytest
import time

from datetime import datetime, timezone

from bip32utils import BIP32Key
from testcontainers.compose import DockerCompose

from src.origin_ledger_sdk import Ledger, Batch, BatchStatus, MeasurementType, PublishMeasurementRequest, IssueGGORequest, TransferGGORequest, SplitGGORequest, SplitGGOPart, RetireGGORequest, generate_address, AddressPrefix, RetireGGOPart


class TestIntegration(unittest.TestCase):

    def wait_for_commit(self, ledger, handle):
        i = 0
        while True:
            status = ledger.get_batch_status(handle).status
            
            if status == BatchStatus.COMMITTED:
                break

            if status == BatchStatus.INVALID:
                raise Exception("INVALID")

            i += 1

            if i > 30:
                raise Exception("TIMEOUT")

            time.sleep(1)

        self.assertEqual(status, BatchStatus.COMMITTED)

    @pytest.mark.integrationtest
    @pytest.mark.trylast
    def test_integration(self):

        issuer_key = BIP32Key.fromEntropy("this_will_be_the_issuers_main_key_entropy".encode())
        user_1_masterkey = BIP32Key.fromEntropy("this_will_be_user_one_who_has_the_production_device".encode())
        user_2_masterkey = BIP32Key.fromEntropy("this_will_be_user_two_who_has_the_production_device".encode())

        # Accounts is always 0.0
        user_1_account = user_1_masterkey.ChildKey(0).ChildKey(0)
        # Meatering points is always 1.n
        user_1_meter_42 = user_1_masterkey.ChildKey(1).ChildKey(42)

        
        # Accounts is always 0.0
        user_2_account = user_2_masterkey.ChildKey(0).ChildKey(0)
        # Meatering points is always 1.n
        user_2_meter_5 = user_2_masterkey.ChildKey(1).ChildKey(5)


        with DockerCompose("./test") as compose:
            time.sleep(5)

            host = compose.get_service_host('rest-api', 8008)
            port = compose.get_service_port('rest-api', 8008)
            url = f'http://{host}:{port}'

            ledger = Ledger(url)

            # ----------- Publish and Issue ----------- 

            measurement_prod_key = user_1_meter_42.ChildKey(26429040)
            measurement_prod_address = generate_address(AddressPrefix.MEASUREMENT, measurement_prod_key.PublicKey())
            measurement_prod_request = PublishMeasurementRequest(
                address=measurement_prod_address,
                begin=datetime(2020, 4, 1, 12, tzinfo=timezone.utc),
                end=datetime(2020, 4, 1, 13, tzinfo=timezone.utc),
                sector='DK1',
                type=MeasurementType.PRODUCTION,
                amount=100
            )


            measurement_con_key = user_2_meter_5.ChildKey(26429040)
            measurement_con_address = generate_address(AddressPrefix.MEASUREMENT, measurement_con_key.PublicKey())
            measurement_con_request = PublishMeasurementRequest(
                address=measurement_con_address,
                begin=datetime(2020, 4, 1, 12, tzinfo=timezone.utc),
                end=datetime(2020, 4, 1, 13, tzinfo=timezone.utc),
                sector='DK1',
                type=MeasurementType.CONSUMPTION,
                amount=50
            )


            ggo_issue_address = generate_address(AddressPrefix.GGO, measurement_prod_key.PublicKey())
            ggo_issue_request = IssueGGORequest(
                measurement_address=measurement_prod_address,
                ggo_address=ggo_issue_address,
                tech_type='T124124',
                fuel_type='F12412'
            )

            batch = Batch(issuer_key.PrivateKey())
            batch.add_request(measurement_prod_request)
            batch.add_request(measurement_con_request)
            batch.add_request(ggo_issue_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)


            # ----------- Trade the GGO ----------- 
            split_request = SplitGGORequest(
                source_private_key=measurement_prod_key.PrivateKey(),
                source_address=ggo_issue_address,
                parts = [
                    SplitGGOPart(
                        address=generate_address(AddressPrefix.GGO, user_1_account.ChildKey(0).PublicKey()),
                        amount=50
                    ),
                    SplitGGOPart(
                        address=generate_address(AddressPrefix.GGO, user_1_account.ChildKey(1).PublicKey()),
                        amount=25
                    ),
                    SplitGGOPart(
                        address=generate_address(AddressPrefix.GGO, user_2_account.ChildKey(0).PublicKey()),
                        amount=25
                    )
                ]
            )

            batch = Batch(user_1_masterkey.PrivateKey())
            batch.add_request(split_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)

            # ----------- Trade the GGO ----------- 
            transfer_request = TransferGGORequest(
                source_private_key=user_1_account.ChildKey(1).PrivateKey(),
                source_address=generate_address(AddressPrefix.GGO, user_1_account.ChildKey(1).PublicKey()),

                destination_address=generate_address(AddressPrefix.GGO, user_2_account.ChildKey(1).PublicKey()),
            )

            batch = Batch(user_1_masterkey.PrivateKey())
            batch.add_request(transfer_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)


            # ----------- Retire GGO ----------- 

            settlement_address = generate_address(AddressPrefix.SETTLEMENT, measurement_con_key.PublicKey())
            retire_request = RetireGGORequest(
                settlement_address=settlement_address,
                measurement_address=measurement_con_address,
                measurement_private_key=measurement_con_key.PrivateKey(),
                parts=[
                    RetireGGOPart(
                        address=generate_address(AddressPrefix.GGO, user_2_account.ChildKey(0).PublicKey()),
                        private_key=user_2_account.ChildKey(0).PrivateKey()
                    ),
                    RetireGGOPart(
                        address=generate_address(AddressPrefix.GGO, user_2_account.ChildKey(1).PublicKey()),
                        private_key=user_2_account.ChildKey(1).PrivateKey()
                    )
                ]
            )

            batch = Batch(user_2_masterkey.PrivateKey())
            batch.add_request(retire_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)
