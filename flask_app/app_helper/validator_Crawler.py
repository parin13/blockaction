import os, sys
from os.path import dirname, join, abspath
import  requests
import ast 
import time 
import json
import base64
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from client  import client_beacon_chain,client_schlesi,client_validators

import schedule

from flask_app import common,beacon
from flask_app.models import redis_helper, mongo_helper



base_url = common.api()
config = common.get_config()


def validator_crawler(epoch=0, pageToken = '0'):
    try:
        for data in  client_beacon_chain.getChainHeadStream():
            list_validators = client_beacon_chain.ListValidators(epoch=epoch, pageToken=pageToken)
            for data in list_validators.validator_list:
                #todo process validator data here
                total_size = list_validators.total_size
                validators = data.validator
                index = data.index
                public_key = validators.public_key
                pkB64 = base64.b64encode(public_key).decode()
                pkHex = common.decode_public_key(pkB64)
                effective_balance = float(validators.effective_balance)/ 1000000000
                exit_epoch = validators.exit_epoch
                withdrawable_epoch = validators.withdrawable_epoch
                #from GetValidator client
                get_validators = client_beacon_chain.GetValidator(index=index)
                activation_epoch = get_validators.activation_epoch
                activation_eligibility_epoch = get_validators.activation_eligibility_epoch
                slashed = get_validators.slashed
                #Get validators Status
                get_validators_status = client_validators.ValidatorStatus(public_key)
                status_key = get_validators_status.status
                status = {0:'UNKNOWN_STATUS', 1:'DEPOSITED', 2:'PENDING', 3: 'ACTIVE', 4:'EXITING', 5:'SLASHING', 6:'EXITED'}
                #GetValidatorsBalance
                get_validators_balance = client_beacon_chain.ListValidatorBalances([public_key])
                balances_data = get_validators_balance.balances[0]
                balance = int(balances_data.balance)/ 1000000000
                #insert in validator table
                db_con = mongo_helper.mongo_conn()
                db_data = db_con.validators_list.insert({
                    'index' : index,
                    'effective_balance' : effective_balance,
                    'balance' : balance,
                    'public_key' : pkHex,
                    'total_size' : total_size,
                    'activation_epoch': activation_epoch,
                    'activation_eligibility_epoch': activation_eligibility_epoch,
                    'slashed' : slashed,
                    'status': status[status_key]


                })

            if not (list_validators.next_page_token == ''):
                validator_crawler(epoch = epoch, pageToken= list_validators.next_page_token)
            return

    except Exception as e:
        error =  common.get_error_traceback(sys, e)
        print (error)

validator_crawler()



