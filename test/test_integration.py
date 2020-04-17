import unittest
import pytest
import time

from datetime import datetime, timezone

from bip32utils import BIP32Key
from testcontainers.compose import DockerCompose


from src.origin_ledger_sdk import Ledger, Batch, BatchStatus, MeasurementType, PublishMeasurementRequest, IssueGGORequest, TransferGGORequest, SplitGGORequest, SplitGGOPart, RetireGGORequest


class TestIntegration(unittest.TestCase):

    def wait_for_commit(self, ledger, handle):
        i = 0
        while True:
            status = ledger.get_batch_status(handle).data[0].status
            
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

        user_1_account = user_1_masterkey.ChildKey(1)
        user_1_meter_1 = user_1_masterkey.ChildKey(2)

        user_2_account = user_2_masterkey.ChildKey(1)
        user_2_meter_1 = user_2_masterkey.ChildKey(2)


        with DockerCompose("./test") as compose:
            time.sleep(5)

            host = compose.get_service_host('rest-api', 8008)
            port = compose.get_service_port('rest-api', 8008)
            url = f'http://{host}:{port}'

            ledger = Ledger(url)

            # ----------- Publish and Issue ----------- 
            measurement_prod_request = PublishMeasurementRequest(
                owner_key=user_1_meter_1.ChildKey(1),
                begin=datetime(2020, 4, 1, 12, tzinfo=timezone.utc),
                end=datetime(2020, 4, 1, 13, tzinfo=timezone.utc),
                sector='DK1',
                type=MeasurementType.PRODUCTION,
                amount=100
            )

            measurement_con_request = PublishMeasurementRequest(
                owner_key=user_2_meter_1.ChildKey(1),
                begin=datetime(2020, 4, 1, 12, tzinfo=timezone.utc),
                end=datetime(2020, 4, 1, 13, tzinfo=timezone.utc),
                sector='DK1',
                type=MeasurementType.CONSUMPTION,
                amount=50
            )

            issue_request = IssueGGORequest(
                owner_key=user_1_meter_1.ChildKey(1),
                tech_type='T124124',
                fuel_type='F12412'
            )

            batch = Batch(issuer_key)
            batch.add_request(measurement_prod_request)
            batch.add_request(measurement_con_request)
            batch.add_request(issue_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)


            # ----------- Trade the GGO ----------- 
            split_request = SplitGGORequest(
                user_1_meter_1.ChildKey(1),
                parts = [
                    SplitGGOPart(
                        key=user_1_account.ChildKey(1),
                        amount=50
                    ),
                    SplitGGOPart(
                        key=user_1_account.ChildKey(2),
                        amount=25
                    ),
                    SplitGGOPart(
                        key=user_2_account.ChildKey(1),
                        amount=25
                    )
                ]
            )

            batch = Batch(user_1_masterkey)
            batch.add_request(split_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)

            # ----------- Trade the GGO ----------- 
            transfer_request = TransferGGORequest(
                user_1_account.ChildKey(2),
                user_2_account.ChildKey(2)
            )

            batch = Batch(user_1_masterkey)
            batch.add_request(transfer_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)


            # ----------- Retire GGO ----------- 

            retire_request = RetireGGORequest(
                user_2_meter_1.ChildKey(1),
                ggo_keys=[
                    user_2_account.ChildKey(1),
                    user_2_account.ChildKey(2)
                ]
            )

            batch = Batch(user_2_masterkey)
            batch.add_request(retire_request)
            
            handle = ledger.execute_batch(batch)
            self.wait_for_commit(ledger, handle)
