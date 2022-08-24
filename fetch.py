from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser
from matplotlib.animation import FuncAnimation
import numpy as np

def get_data_from_elastic(host='10.22.2.254',fromDate='now-30d/d',toDate='now/d', index='logs-snmpdevices-default'):
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
                    {"match" : {
                        "host.name": host
                    }},
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
               scroll='1m',
               index='logs-snmpdevices-default',
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

        value = (array[current] - array[previous]) / ((time[current] - time[previous]).total_seconds() + 1E-9)
        # set value to zero if times are equivalent
        if(time[current] == time[previous]):
            value = 0

        if value < 0:
            # logic to actually grab the wanted value properly circumnavigating the overflow
            value = 4294967295 - array[previous] + array[current]
        elif np.isnan(value):
            value = 0
        newArray[previous] = value
    newArray[array.index[-1]]=0
    return newArray[newArray.index]

server = 'ncar-im-0.rc.unr.edu' # 134.197.75.31
port = 30549
connectionScheme = 'http'

es = Elasticsearch(hosts = [{'host':server,'port':port,"scheme":connectionScheme}], verify_certs = 'False')

# printing out elasticsearch information
print(es.info())

data = get_data_from_elastic()


'''print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.1'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.2'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.3'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.4'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.5'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.6'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.7'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.8'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.9'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.10'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.12'][0])'''


sort_times = np.vectorize(parser.parse)
data['@timestamp'] = sort_times(data['@timestamp'])

columns = list(data.columns)
columns.sort()

interfaceFields = [ column for column in columns if 'ifDescr' in column]
interfaceNames = [data[name][0] for name in interfaceFields]
interfaceSpeed = [column for column in columns if 'ifSpeed' in column]

#grabbing all outoctet fields 
outOctets = [column for column in columns if 'OutOctets' in column]
inOctets = [column for column in columns if 'InOctets' in column]

data = data.sort_values(by='@timestamp')

data.to_csv('all.csv')

values = {}
nan_to_zero = lambda x: 0 if np.isnan(x) else x
nan_to_zero = np.vectorize(nan_to_zero)
for outOctet in outOctets:
    data[outOctet] = nan_to_zero(data[outOctet]) 
    values[outOctet] = processData(data[outOctet].copy(),data['@timestamp'].copy())

for inOctet in inOctets:
    data[inOctet] = nan_to_zero(data[inOctet])
    values[inOctet] = processData(data[inOctet].copy(),data['@timestamp'].copy())


time = data['@timestamp']
print(time)
time.to_csv('time.csv')
for i in range(len(outOctets)):
    values[outOctets[i]].to_csv('out'+interfaceNames[i]+'.csv')
    plt.figure(interfaceNames[i]+'egress',figsize=(10,10))
    plt.plot(time, values[outOctets[i]])
    plt.yscale('linear')
    plt.savefig(interfaceNames[i]+'egress.png')
    plt.close(interfaceNames[i]+'egress')

for i in range(len(inOctets)):
    values[inOctets[i]].to_csv('in'+interfaceNames[i]+'.csv')
    plt.figure(interfaceNames[i]+'ingress',figsize=(10,10))
    plt.plot(time, values[inOctets[i]])
    plt.yscale('linear')
    plt.savefig(interfaceNames[i]+'ingress.png')
    plt.close(interfaceNames[i]+'ingress')

#plt.tight_layout()
#plt.show()


