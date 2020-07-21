import os, sys
from os.path import dirname, join, abspath
import  requests
import ast 
import time 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from client  import client_beacon_chain

import schedule

from flask_app import common,beacon,third_party,node
from flask_app.models import redis_helper, mongo_helper
from flask_app.app_helper import validator_Crawler


base_url = common.api()
config = common.get_config()


def get_current_chain_state_script():
    print("Executing Redis Crawler script")
    try:
        response = client_beacon_chain.GetChainHead()
        if response:
            finalizedEpoch = response.finalized_epoch
            finalizedSlot = response.finalized_slot
            currentEpoch = response.head_epoch
            currentSlot = response.head_slot
            finalized_epoch = redis_helper.hset(
                key_hash = 'chain_head_crawler',
                key = 'finalized_epoch',
                value = finalizedEpoch
            )

            print('crawled finalized_epoch is {}'.format(finalizedEpoch))

            finalized_slot = redis_helper.hset(
            key_hash = 'chain_head_crawler',
            key = 'finalized_slot',
            value = finalizedSlot
            )
            print('crawled finalized_slot is  {}'.format(finalizedSlot))

            current_epoch = redis_helper.hset(
                    key_hash = 'chain_head_crawler',
                    key = 'current_epoch',
                    value = currentEpoch
                )
            print('crawled current_epoch is  {}'.format(currentEpoch))

            current_slot = redis_helper.hset(
                key_hash = 'chain_head_crawler',
                key = 'current_slot',
                value = currentSlot
                )
            print('crawled current_slot is  {}'.format(currentSlot))

            print ('processing  from get participation API .........')
            voted_ether_data = beacon.get_participation_rate()
            if voted_ether_data:
                participation = voted_ether_data.get('participation')
                voted_ether_data =  int(participation.get('votedEther'))/1000000000
                eligible_ether_data =  int(participation.get('eligibleEther'))/1000000000

                voted_ether = redis_helper.hset(

                    key_hash = 'chain_head_crawler',
                    key = 'voted_ether',
                    value = voted_ether_data
                )
                print('crawled voted_ether is  {}'.format(voted_ether_data))
                
                eligible_ether = redis_helper.hset(

                    key_hash = 'chain_head_crawler',
                    key = 'eligible_ether',
                    value = eligible_ether_data
                )
                print('crawled eligible_ether is  {}'.format(eligible_ether_data))

           
            price = redis_helper.get_key('eth_price')
            if not price:
                raise 
            print ('processing from node_peers API .........')
            peers_data =  node.node_peers()
            peers_count =  len(peers_data.get('peers'))

            print ('processing from  API for  active and pending validators count.......')
            active_validator_count =  beacon.get_active_validators_count_head()
            pending_validators_count = beacon.get_pending_validators_count()

            peers_count = redis_helper.hset(

                    key_hash = 'chain_head_crawler',
                    key = 'peers_count',
                    value = peers_count
                )

            print('crawled peers_count is  {}'.format(peers_count))

            active_validator_count = redis_helper.hset(

                    key_hash = 'chain_head_crawler',
                    key = 'active_validator_count',
                    value = active_validator_count
                )
            print('crawled active_validator_count is  {}'.format(active_validator_count))

            pending_validators_count = redis_helper.hset(

                    key_hash = 'chain_head_crawler',
                    key = 'pending_validators_count',
                    value = pending_validators_count
                )
            print('crawled pending_validators_count is  {}'.format(pending_validators_count))

        else:
                print ('skipping redis operation')
    
    except Exception as e:
        error =  common.get_error_traceback(sys, e)
        print (error)


schedule.every().seconds.do(get_current_chain_state_script)

def crawl_chain_head():
    print ('Executing Crawler script....')
    try:
        for chain_head_data in  client_beacon_chain.getChainHeadStream():
            current_epoch = int(chain_head_data.get('headEpoch'))
            current_slot  = int(chain_head_data.get('headSlot'))
            
            crawled_slot = int(redis_helper.hget(
                hash= 'chain_head',
                key = 'current_slot_'
            ))
            print('crawled slot is {} current slot is {}'.format(crawled_slot,current_slot))

            if crawled_slot < current_slot:
                diffrence = current_slot - crawled_slot

                if diffrence > 1 :
                    #case of skipped block
                    print ('processing skipped block')
                    for i in range(diffrence -1):
                        crawled_slot = crawled_slot + 1

                        print ('processing skipped block: {} '.format(crawled_slot))

                        db_conn = mongo_helper.mongo_conn()

                        db_status = db_conn.latest_block_altona.insert({
                            'epoch' : int(current_epoch),
                            'slot' : int(crawled_slot),
                            'proposer' : 'NA',
                            'attestian_count' : 0,
                            'status' : 'Skipped'
                        })
                        print (db_status)
     

        
                print ('processing redis operation.........')
                redis_set_slot = redis_helper.hset(
                    key_hash = 'chain_head',
                    key = 'current_slot_',
                    value = current_slot
                )

                crawled_epoch = int(redis_helper.hget(
                    hash= 'chain_head',
                    key = 'current_epoch_'
                ))
                
                if crawled_epoch < current_epoch:
                    redis_set_epoch = redis_helper.hset(
                        key_hash = 'chain_head',
                        key = 'current_epoch_',
                        value = current_epoch
                    )
                slot_data = beacon.get_slot_data(current_slot)[0]
                attestian_count = slot_data.get('attestations_count', '0')
                proposer = slot_data.get('proposer', 'NA')

                print ('processing_db operation')

                db_conn = mongo_helper.mongo_conn()
                db_status = db_conn.latest_block_altona.insert({
                    'epoch' : int(current_epoch),
                    'slot' : int(current_slot),
                    'proposer' : proposer,
                    'attestian_count' : attestian_count,
                    'status' : 'proposed'
                })
                print (db_status)
                get_current_chain_state_script()
                # process validator crawling
                validator_Crawler.validator_crawler(current_epoch)


            else:
                print ('skipping redis operation')
        else:
            print ('No Response from Blockchain')
    except Exception as e:
        error =  common.get_error_traceback(sys, e)
        print (error)



crawl_chain_head()




while True:
    print ("*"*30)
    print ('Running python shedular for Get Current Chain State')
    schedule.run_pending()
    time.sleep(10)