from hashlib import new
from signal import pause
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser as timeparser
from matplotlib.animation import FuncAnimation
import numpy as np
import argparse
import json
#matplotlib.use('Agg')
class SplitArgs(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split(','))

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
        "query": {
            "bool" : {
                "must" : [
                    {"range": {
                        "@timestamp": {
                        "gte": fromDate,
                        "lt": toDate
                        }
                    }}
                ]
            }
        }
    }

    # Scan function to get all the data. 
    rel = scan(client=es,             
               query=query,                                     
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

def processData(array,time):
    newArray = array.copy()
    for i in range(1,len(array)):
        current = array.index[i]
        previous = array.index[i-1]

        value = (array[current] - array[previous]) / 30.0 #((time[current] - time[previous]).total_seconds() + 1E-9)
        # set value to zero if times are equivalent
        if(time[current] == time[previous]):
            value = 0

        if value < 0:
            # logic to actually grab the wanted value properly circumnavigating the overflow
            value = 0#4294967295 - array[previous] + array[current]
        elif np.isnan(value):
            value = 0

        if (value > 1E9):
            print('alert', array[previous], array[current],value)
        newArray[previous] = value
    newArray[array.index[-1]]=0
    print(newArray[newArray.index].shape)
    print(time[newArray.index].shape)
    return pd.concat([newArray[newArray.index], time[newArray.index]],axis = 1)


handle = open('mapping.json','r')
mapping = handle.read()
handle.close()
mapping = json.loads(mapping)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='Plot From Elastic Search',
                        description='The following program will plot any values specified to this program.',
                        epilog='Text at the bottom of help')
    fields = ['capacityrx','capacitytx']
    parser.add_argument('-fields', default=fields, action=SplitArgs)
    parser.add_argument('-index',default='logs-nonaftluairfiber-default')
    parser.add_argument('-pastdelta',default='10m')

    arguments = parser.parse_args()
    fields = arguments.fields

    server = 'ncar-im-0.rc.unr.edu' # 134.197.75.31
    port = 30549
    connectionScheme = 'http'

    es = Elasticsearch(hosts = [{'host':server,'port':port,"scheme":connectionScheme}], verify_certs = 'False')

    # printing out elasticsearch information
    print(es.info())

    if (arguments.index == 'logs-nonaftluairfiber-default'):
        mapping = mapping['nonaftlu']
        fields = list(mapping.keys())
        fields.remove('host')
    elif (arguments.index == 'logs-aftluairfiber-default'):
        mapping = mapping['aftlu']
        fields = list(mapping.keys())
        fields.remove('host')

    data = get_data_from_elastic(index=arguments.index,fromDate='now-'+arguments.pastdelta)
    data['timestamp'] = pd.to_datetime(data['@timestamp'])
    #sort_times = np.vectorize(timeparser.parse)
    #data['@timestamp'] = sort_times(data['@timestamp'])
    data = data.sort_values(by='timestamp')
    #data = data.sort_index()
    print(data)
    for field in fields:
        print('start' + field)
        #ax = plt.figure(arguments.index + '_' + field ,figsize=(5,5))
        # make plots set timestamps to year-month-day and make ticks have less things 
        # vega does not work as intended 
        fig, ax = plt.subplots(figsize=(5,5))
        print(mapping)
        ax.set_title(mapping['host'] + ' ' + mapping[field])
        ax.plot(data['timestamp'], data[field])
        #print(data['timestamp'].dtype)
        cdf = matplotlib.dates.ConciseDateFormatter(ax.xaxis.get_major_locator())
        ax.xaxis.set_major_formatter(cdf)
        #print(ax.get_axes())
        #print(data['@timestamp'])
        #print(data[field])
        fig.savefig(field+'.png')
        print('done' + field)
        #plt.show()
    plt.tight_layout()
    #plt.savefig
    plt.show()