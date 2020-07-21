import grpc
import google

from mcs_protos import validator_pb2, validator_pb2_grpc
from google.protobuf import empty_pb2
from client import client_validators,client_conf


def ValidatorStatus(public_key):
    try:    
        with grpc.insecure_channel(client_conf.server_address()) as channel:
            stub = validator_pb2_grpc.BeaconNodeValidatorStub(channel)
            response = stub.ValidatorStatus(
                validator_pb2.ValidatorStatusRequest(

                    public_key= public_key
                )
            )
            return response
    except Exception as e:
        print (e)
        raise e
