import sys,os 
import requests
from flask_app import common
import ast
from flask_app import common
from flask_app.models import mongo_helper,redis_helper
import datetime
from bson.objectid import ObjectId


base_url = common.api()

# def get_current_ethereum_price():
#     try:
#         eth_price = redis_helper.get_key('eth_price')
#         if eth_price:
#             return eth_price
#         else:
#             return False
#     except Exception as e:
#         error = common.get_error_traceback(sys, e)
#         print (error)
#         raise 


#new 
def get_current_ethereum_price():
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.content.decode('UTF-8')
        data =  common.parse_dictionary(data)
        price = data['ethereum']
        price_eth = price['usd']
        set_eth_price = redis_helper.set_key('eth_price', price_eth)
        price = redis_helper.get_key('eth_price')
        return price
    else:
        return  common.send_error_msg()



def get_current_epoch():
    try:    
        uri = '/eth/v1alpha1/beacon/chainhead'
        url = base_url+uri
        response = requests.get(url)
        if response.status_code == 200:
            data = response.content.decode('UTF-8')    
            data = ast.literal_eval(data)
            return int(data.get('finalizedEpoch'))
    except Exception as e:
        print (e)
        return common.send_error_msg()


def get_current_slot():
    try:    
        uri = '/eth/v1alpha1/beacon/chainhead'
        url = base_url+uri
        response = requests.get(url)
        if response.status_code == 200:
            data = response.content.decode('UTF-8')    
            data = ast.literal_eval(data)
            return int(data.get('finalizedSlot'))
    except Exception as e:
        print (e)
        return common.send_error_msg()

def send_current_eth_price():
    price = redis_helper.get_key('eth_price')
    return common.send_sucess_msg({'price' :price})



def get_data_for_global_participation_rate(args):
    try:
        db_con = mongo_helper.mongo_conn()
        today = datetime.date.today()
        days = args.get("time", 1)
        DD = datetime.timedelta(days=int(days) - 1)
        earlier = today - DD
        earlier_str = earlier.strftime("%d/%m/%Y %H:%M:%S")

        datetime_object = datetime.datetime.strptime(earlier_str,"%d/%m/%Y %H:%M:%S")
        obj_id = ObjectId.from_datetime(datetime_object)

        if days == 1 or int(days) == 1:
            
            db_data = db_con.global_participation_new_altona.find({"_id":{"$gte": obj_id}}).sort([('_id',-1)])
        else:
            db_data = db_con.global_participation_new_altona.find({"_id":{"$gte": obj_id},"timestamp":{"$regex":'.*(00|16|08):*:*'}}).sort([('_id',-1)])

        timestamp_epoch_list = []
        voted_ether_list = []
        global_participation_list = []

        for data in db_data:
            ether = int(data.get('voted_ether'))/1000000000
            epoch = str(data.get('epoch'))
            timestamp_epoch_list.append([data.get('timestamp'),'Epoch '+epoch])
            voted_ether_list.append(ether)
            global_participation_list.append(round(data.get('global_participation')*100,2))

        global_participation_list.reverse()
        voted_ether_list.reverse()
        timestamp_epoch_list.reverse()

        return_dict = {
            'timestamp' : timestamp_epoch_list,
            'voted_ether' : voted_ether_list,
            'global_participation' : global_participation_list
        }
        return common.send_sucess_msg(return_dict)

    except Exception as e :
        error = common.get_error_traceback(sys,e)
        print (error)
        raise 




def get_data_for_validators_graph(args):
    try:
        db_con = mongo_helper.mongo_conn()
        today = datetime.date.today()
        days = args.get("time", 1)
        DD = datetime.timedelta(days=int(days) - 1)
        earlier = today - DD
        earlier_str = earlier.strftime("%d/%m/%Y %H:%M:%S")

        datetime_object = datetime.datetime.strptime(earlier_str,"%d/%m/%Y %H:%M:%S")
        obj_id = ObjectId.from_datetime(datetime_object)

        if days == 1 or int(days) == 1:
            
            db_data = db_con.new_graph_data_altona.find({"_id":{"$gte": obj_id}}).sort([('_id',-1)])
        else:
            db_data = db_con.new_graph_data_altona.find({"_id":{"$gte": obj_id},"timestamp":{"$regex":'.*(00|16|08):*:*'}}).sort([('_id',-1)])

        # db_data = db_con.new_graph_data_last.find({}).sort([('_id',-1)]).limit(24)

        timestamp_epoch_list = []
        eligible_ether_list = []
        active_validators_list = []

        for data in db_data:
            eligible_ether = int(data.get('eligible_ether'))/1000000000
            epoch = str(data.get('epoch'))
            timestamp_epoch_list.append([data.get('timestamp'),'Epoch '+epoch])
            eligible_ether_list.append(eligible_ether)
            active_validators_list.append(data.get('total_act_validators'))

        active_validators_list.reverse()
        eligible_ether_list.reverse()
        timestamp_epoch_list.reverse()

        return_dict = {
            'timestamp' : timestamp_epoch_list,
            'eligible_ether' : eligible_ether_list,
            'active_validators_count' : active_validators_list
        }
        return common.send_sucess_msg(return_dict)

    except Exception as e :
        error = common.get_error_traceback(sys,e)
        print (error)
        raise 



def get_vol_data(args):
    time = args.get("time", "")
    url = 'https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=' +time
    response = requests.get(url)
    if response.status_code == 200:
        data = response.content.decode('UTF-8')
        data =  common.parse_dictionary(data)

        total_volumes = data['total_volumes']
        count = len(total_volumes)

        usdPrice = []
        marketcapValue =[]
        dateTime = []
        marketVolume = []

        for x in range(count):
            timestamp = total_volumes[x][0]
            usdvalue = data['prices'][x][1]
            capvalue = data['market_caps'][x][1]
            volume = data['total_volumes'][x][1]

            dt_object = datetime.datetime.fromtimestamp(timestamp/1000) 
            t = dt_object.strftime('%a,%b %d %Y,%H:%M')
            
            dateTime.append(t)
            usdPrice.append(usdvalue)
            marketcapValue.append(capvalue)
            marketVolume.append(volume)

        return_data = {
            'dateTime' : dateTime,
            'volumeUsd' : marketVolume,
            'marketCapValue' : marketcapValue,
            'prices' : usdPrice
        
        }
        return  common.send_sucess_msg(return_data)
    else:
        return  common.send_error_msg()
