

import marshmallow_dataclass

from typing import List
from dataclasses import dataclass, field
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey as PrivateKey

from .helpers import get_signer
from .abstract_request import AbstractRequest

from ..ledger_dto.requests import SplitGGORequest as LedgerSplitGGORequest
from ..ledger_dto.requests import SplitGGOPart as LedgerSplitGGOPart

split_ggo_schema = marshmallow_dataclass.class_schema(LedgerSplitGGORequest)

@dataclass
class SplitGGOPart():
    """
    :param str address: The address of where to move this part of the new GGO.
    :param str amount: The amount to transfer to this new GGO.
    """
    address: str = field()
    amount: int = field()


@dataclass
class SplitGGORequest(AbstractRequest):
    """
    :param bytes source_private_key: The source private key as a byte-string of the GGO to transfer
    :param str source_address: The source address of the GGO to transfer
    :param List[SplitGGOPart] parts: A list of the new GGOs to split the current GGO into.
    """

    source_private_key: bytes = field()
    source_address: str = field()

    parts: List[SplitGGOPart] = field()

    def get_signed_transactions(self, batch_signer) -> List[Transaction]:

        addresses = [self.source_address]
        parts = []

        for part in self.parts:
            ggo_part = LedgerSplitGGOPart(
                address=part.address,
                amount=part.amount
            )

            addresses.append(part.address)
            parts.append(ggo_part)
            
        request = LedgerSplitGGORequest(
            origin=self.source_address,
            parts=parts)

        byte_obj = self._to_bytes(split_ggo_schema, request)

        return [self.sign_transaction(
            batch_signer,
            get_signer(self.source_private_key),
            byte_obj,
            inputs=addresses,
            outputs=addresses,
            family_name=LedgerSplitGGORequest.__name__,
            family_version='0.1')]
