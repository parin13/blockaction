import grpc
import google

from mcs_protos import beacon_chain_pb2, beacon_chain_pb2_grpc
from google.protobuf import empty_pb2
from client import client_validators,client_conf


def get_empty_data():
    return empty_pb2.Empty(

    )

def GetChainHead():
    try:    
        with grpc.insecure_channel(client_conf.server_address()) as channel:
            stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
            response = stub.GetChainHead(get_empty_data())
            return response
    except Exception as e:
        raise e
        return False

def getChainHeadStream():
    try:
        with grpc.insecure_channel(client_conf.server_address()) as channel:
            stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
            for data in stub.StreamChainHead(get_empty_data()):
                return_data = {
                    'headEpoch' : data.head_epoch,
                    'headSlot' : data.head_slot
                }

                yield return_data

            
    except Exception as e:
        print (e)
        raise e

def ListValidators(epoch=0,pageToken="0"):
    try:
        with grpc.insecure_channel(client_conf.server_address()) as channel:
            stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
            response = stub.ListValidators(
                beacon_chain_pb2.ListValidatorsRequest(
                    epoch = epoch,
                    page_token = pageToken
                )
            )
            return response
    except Exception as e:
        raise e
    

def ListValidatorBalances(public_keys):
    try:
        with grpc.insecure_channel(client_conf.server_address()) as channel:
            stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
            response = stub.ListValidatorBalances(
                beacon_chain_pb2.ListValidatorBalancesRequest(
                    public_keys=public_keys
                )
            )
            return response
    
    except Exception as e:
        raise e


def GetValidator(index):
    try:
        with grpc.insecure_channel(client_conf.server_address()) as channel:
            stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
            response = stub.GetValidator(
                beacon_chain_pb2.GetValidatorRequest(
                    index = index
                )
            )
            return response
    
    except Exception as e:
        raise e


def GetValidatorPerformance(public_keys):
    try:
        with grpc.insecure_channel(client_conf.server_address()) as channel:
            stub = beacon_chain_pb2_grpc.BeaconChainStub(channel)
            response = stub.GetValidatorPerformance(
                beacon_chain_pb2.ValidatorPerformanceRequest(
                    public_keys=public_keys
                )
            )
            return response
    
    except Exception as e:
        raise e

