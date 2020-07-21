import os, sys
from os.path import dirname, join, abspath

import requests 

import json 
import datetime
import schedule
import time
import pymongo
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from flask_app import beacon, common, third_party
from  flask_app.models import redis_helper,mongo_helper
from flask_app.app_helper import time_calculator
base_url = common.api()



def global_participation_script():
    try:
        print ("#"*30)
        print("Executing global_participation_script")
        
        db_con = mongo_helper.mongo_conn()
        crawled_data = db_con.latest_block_altona.find_one({},sort=[('_id',  pymongo.DESCENDING)]) 
        data = beacon.get_participation_rate()
        
        if data:
            participation = data.get('participation')
            if crawled_data.get('epoch') == data.get('epoch'):
                raise('skipping operation')
            
            insert_data = {
                'epoch' : data.get('epoch'),
                'voted_ether' : participation.get('votedEther'),
                'global_participation' : participation.get('globalParticipationRate'),
                'eligible_ether' : participation.get('eligibleEther'),
                'timestamp' : time_calculator.get_epoch_time(int(data.get('epoch')))
            }    
            db_con = mongo_helper.mongo_conn()
            db_status = db_con.global_participation_new_altona.insert(insert_data)
            print (db_status)
        else:
            print ('No data')
            False

    except Exception as e:
        error =  common.get_error_traceback(sys,e)
        print (error)


def global_participation_history_crawler():
    epoch_no = 170
    while (epoch_no < 1745):
        data = False
        data = beacon.get_participation_rate(epoch=epoch_no)        
        if data:
            participation = data.get('participation')  
            epoch_timestamp = time_calculator.get_epoch_time(epoch_no)      
            timestamp = datetime.datetime.strptime(epoch_timestamp,'%Y-%m-%dT%H:%M:%SZ')
            obj_id = ObjectId.from_datetime(timestamp)

            insert_data = {
                '_id': obj_id,
                'epoch' : int(data.get('epoch')),
                'voted_ether' : participation.get('votedEther'),
                'global_participation' : participation.get('globalParticipationRate'),
                'eligible_ether' : participation.get('eligibleEther'),
                'timestamp' : epoch_timestamp
            }        
            db_con = mongo_helper.mongo_conn()
            db_status = db_con.global_participation_new_altona.insert(insert_data)    

            print('processing epoch {} with data {}'.format(epoch_no, str(insert_data)))
        epoch_no = epoch_no+1

# global_participation_history_crawler()
schedule.every(7).minutes.do(global_participation_script)




# New Scripts
def total_act_validators_script():
    try:
        print ("#"*30)
        print("Executing Total Active Validators Count")
        
        db_con = mongo_helper.mongo_conn()
        crawled_data = db_con.latest_block_altona.find_one({},sort=[('_id',  pymongo.DESCENDING)]) 
        data = beacon.get_participation_rate()
        if data:
            data2 =  beacon.get_active_validators_count_head()
            data = beacon.get_participation_rate()
            participation = data.get('participation')
            if crawled_data.get('epoch') == data.get('epoch'):
                raise('skipping operation')
            insert_data = {
                'eligible_ether' : participation.get('eligibleEther'),
                'epoch' : int(data.get('epoch')),
                'timestamp' : time_calculator.get_epoch_time(int(data.get('epoch'))),
                'total_act_validators': data2

            }    
            db_con = mongo_helper.mongo_conn()
            db_status = db_con.new_graph_data_altona.insert(insert_data)
            print (db_status)
        else:
            print ('No data')
            False

    except Exception as e:
        error =  common.get_error_traceback(sys,e)
        print (error)




# New graph data Crwaler Script
def new_graph_history_crawler():
    epoch_no = 2357
    while (epoch_no < 2440):
        data = False
        data = beacon.get_participation_rate(epoch=epoch_no)        
        if data:
            participation = data.get('participation')  
            epoch_timestamp = time_calculator.get_epoch_time(epoch_no)      
            timestamp = datetime.datetime.strptime(epoch_timestamp,'%Y-%m-%dT%H:%M:%SZ')
            obj_id = ObjectId.from_datetime(timestamp)
            data2 =  beacon.get_active_validators_count(epoch=epoch_no)

            insert_data = {
                '_id': obj_id,
                'eligible_ether' : participation.get('eligibleEther'),
                'epoch' : int(data.get('epoch')),
                'timestamp' : epoch_timestamp,
                'total_act_validators' : data2
            }        
            db_con = mongo_helper.mongo_conn()
            db_status = db_con.new_graph_data_altona.insert(insert_data)    

            print('processing epoch {} with data {}'.format(epoch_no, str(insert_data)))
        epoch_no = epoch_no+1

# new_graph_history_crawler()
schedule.every(7).minutes.do(total_act_validators_script)



def get_eth1_price_from_third_party_script():
    print ("#"*30)
    print("Executing get_eth1_price_from_third_party")
    price = third_party.get_current_ethereum_price()
    if price:
        price = price
        print (price)
    else:
        False

schedule.every().hour.do(get_eth1_price_from_third_party_script)








while True:
    print ("*"*30)
    print ('Running python shedular for graph data')
    schedule.run_pending()
    time.sleep(10)