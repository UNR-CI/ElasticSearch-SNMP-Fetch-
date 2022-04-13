from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import pandas as pd
def get_data_from_elastic(host='10.22.2.254',fromDate='now-20d/d',toDate='now/d', index='logs-snmpdevices-default'):
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


server = 'ncar-im-0.rc.unr.edu' # 134.197.75.31
port = 30549
connectionScheme = 'http'

es = Elasticsearch(hosts = [{'host':server,'port':port,"scheme":connectionScheme}], verify_certs = 'False')

# printing out elasticsearch information
print(es.info())

data = get_data_from_elastic()

# iterating over timestamps -- timestamps are in order
for i in data['@timestamp']:
    print(i)

# printing out values for output bytes for interface
for i in data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifOutOctets.3']:
    print(i)

print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.1'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.2'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.3'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.4'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.5'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.6'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.7'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.8'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.9'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.10'][0])
print(data['iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifDescr.12'][0])

columns = list(data.columns)

print('Listing all columns out of elasticsearch record:')
print(columns)

interfaceFields = [ column for column in columns if 'ifDescr' in column]
interfaceNames = [data[name][0] for name in interfaceFields]

print(interfaceFields)
print(interfaceNames)

#grabbing all outoctet fields 
outOctets = [column for column in columns if 'OutOctets' in column]
inOctets = [column for column in columns if 'InOctets' in column]


print(interfaceNames)
print(columns)

