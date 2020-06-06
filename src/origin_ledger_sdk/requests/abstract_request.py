

from hashlib import sha512
from abc import ABC, abstractmethod
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from typing import List

class AbstractRequest(ABC):

    dependencies = []

    @abstractmethod
    def get_signed_transactions(self, batch_signer) -> List[Transaction]:
        raise NotImplementedError


    def get_header_signature(self):
        return self.get_signed_transactions[-1].header_signature

    
    def add_dependency(self, request):
        self.dependencies.append(request)


    def sign_transaction(self,
            batch_signer, 
            transaction_signer,
            payload_bytes,
            inputs,
            outputs,
            family_name,
            family_version) -> Transaction:

        header = TransactionHeader(
            batcher_public_key=batch_signer.get_public_key().as_hex(),
            dependencies=[dep.get_header_signature() for dep in self.dependencies],
            family_name=family_name,
            family_version=family_version,
            inputs=inputs,
            outputs=outputs,
            payload_sha512=sha512(payload_bytes).hexdigest(),
            signer_public_key=transaction_signer.get_public_key().as_hex()
        )

        transaction_header_bytes = header.SerializeToString()
        signature = transaction_signer.sign(transaction_header_bytes)

        transaction = Transaction(
            header=transaction_header_bytes,
            header_signature=signature,
            payload=payload_bytes
        )
        
        return transaction

 
    def _to_bytes(self, schema, obj):
        return schema().dumps(obj=obj).encode('utf8')
