from hashlib import new
from signal import pause
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser
from matplotlib.animation import FuncAnimation
import numpy as np

def get_data_from_elastic(host='17',fromDate='now-10m/d',toDate='now', index='logs-nonaftluairfiber-default'):
    '''
        Description: The follow function will grab snmp data from elasticsearch in a specified topic and at a given time range
        Parameters: host - The ip address to filter out of the data
                    fromDate - The start time or date of the query
                    toDate - The end time or date of the query
                    index - The elasticsearch query you wish to pull data from
        Output: A pandas dataframe of all data associated to the query
        Source: https://theaidigest.in/extract-data-from-elasticsearch-using-python/
    '''
    # query: The elasticsearch query.
    query = {
    '''   "query": {
            "bool" : {
                "must" : [
                    {"match" : {
                        "iso.org.dod.internet.mgmt.mib-2.system.sysName.0":"mikrotik-rockland" # mikrotik-tvhill3
                    }},
                    {"range": {
                        "@timestamp": {
                        "gte": fromDate,
                        "lt": toDate
                        }
                    }}
                ]
            }
        }'''
    }

    # Scan function to get all the data. 
    rel = scan(client=es,                                           
               scroll='30s',
               index=index,
               preserve_order=True,
               raise_on_error=True,
               clear_scroll=True)

    # Keep response in a list.
    result = list(rel)
    temp = []

    # we need only the source to make pandas dataframe
    for hit in result:
        temp.append(hit['_source'])

    # Create a dataframe.
    df = pd.DataFrame(temp)
    return df

server = 'ncar-im-0.rc.unr.edu'
port = 30549
connectionScheme = 'http'

es = Elasticsearch(hosts = [{'host':server,'port':port,"scheme":connectionScheme}], verify_certs = 'False')

data = get_data_from_elastic()

data = data.sort_values(by='@timestamp')
data.to_json('all.json',orient='index',indent=2)

