

import marshmallow_dataclass

from typing import List
from dataclasses import dataclass, field
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction

from .abstract_request import AbstractRequest

from ..ledger_dto.requests import IssueGGORequest as LedgerIssueGGORequest

issue_ggo_schema = marshmallow_dataclass.class_schema(LedgerIssueGGORequest)

@dataclass
class IssueGGORequest(AbstractRequest):
    """
    :param str measurement_address: The address of the production measurement.
    :param str ggo_address: The address where to issue the GGO.
    :param str tech_type: The technology type of the GGO. 'T020001' is 'Onshore Wind'
    :param str fuel_type: The fuel type of the GGO. 'F01050100' is 'Mechanical wind'

    The tech_type and fuel_type follows AIB fact sheet 5:
    https://www.aib-net.org/sites/default/files/assets/eecs/facts-sheets/AIB-2019-EECSFS-05%20EECS%20Rules%20Fact%20Sheet%2005%20-%20Types%20of%20Energy%20Inputs%20and%20Technologies%20-%20Release%207.7%20v5.pdf
    """

    measurement_address: str = field()
    ggo_address: str = field()
    tech_type: str = field()
    fuel_type: str = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        request = LedgerIssueGGORequest(
            origin=self.measurement_address,
            destination=self.ggo_address,
            tech_type=self.tech_type,
            fuel_type=self.fuel_type)

        byte_obj = self._to_bytes(issue_ggo_schema, request)

        return [self.sign_transaction(
            batch_signer,
            batch_signer,
            byte_obj,
            inputs=[self.measurement_address, self.ggo_address],
            outputs=[self.ggo_address],
            family_name=LedgerIssueGGORequest.__name__,
            family_version='0.1')]
