'''
Description grabs snmp from a switch and outputs to a csv file
'''
import asyncio
from asyncio import run
from puresnmp import Client, V2C, PyWrapper
from pysnmp.smi import view, builder
from pysnmp.hlapi import *
import pandas as pd
import time
import argparse



async def getSnmpData(ip="172.20.133.133", community='public', oid="1.3.6.1.2.1.2.2.1"):
    '''
    Gets snmp data from the switch
    '''
    date = time.time()
    client = PyWrapper(Client(ip, V2C(community)))
    output = client.walk(oid)
    test = []
    async for i in output:
        test.append(i)
    return date, test
def get_data(duration=300, ip="172.20.133.133", community="public", oid="1.3.6.1.2.1.2.2.1", outfile='out.csv'):   
    mibViewController = view.MibViewController(builder.MibBuilder())

    # need to find a way to set the mib view controller to see OIDs as IF-MIB
    foo = ObjectIdentity('IF-MIB', 'ifEntry').resolveWithMib(mibViewController) 
    now = start = time.time()
    columns = {'time':[]}

    while now - start <= duration:
        date, data = run(getSnmpData(ip=ip,community=community,oid=oid))
        columns['time'].append(date)

        
        for i in data:
            prettyOid = ObjectIdentity(i.oid).resolveWithMib(mibViewController).prettyPrint()
            if columns.get(prettyOid,None) == None: # get the column names
                columns[prettyOid] = []
            columns[prettyOid].append(i.value)
        now = time.time()
        time.sleep(20)

    df = pd.DataFrame(columns)
    df.to_csv(outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-ip", default='172.20.133.133', help="Host to get ip snmp from.", required=False)
    parser.add_argument("-community", default='public', help="SNMP community to connect to.", required=False)
    parser.add_argument("-oid", default="1.3.6.1.2.1.2.2.1", help="SNMP oid to walk across.", required=False)
    parser.add_argument("-outfile", default='out.csv', help="Output file for saving the csv from snmp.", required=False)
    parser.add_argument("-duration", default=300, help='Sets the duration of the collection process.', required=False)
    args = parser.parse_args()


    get_data(ip=args.ip, community=args.community, oid=args.oid, outfile=args.outfile)
