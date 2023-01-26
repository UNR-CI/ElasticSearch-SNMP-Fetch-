logstash-airfiber-snmp.conf 
-----

Contains snmp logging for grabbing snmp metrics from the airfiber radios.
Tag exec is for airfiber non-aftlu being sent to logs-nonaftluairfiber-default
Tag snmp is for airfiber aftlu sent to logs-aftluairfiber-default

aftlu: https://mibs.observium.org/mib/UBNT-AFLTU-MIB/
------
The following snmp ids are gathered with logstashs snmp module:

walk
1.3.6.1.4.1.41112.1.10.1.4.1.3 afLTUStaTxCapacity Kbps
1.3.6.1.4.1.41112.1.10.1.4.1.4 afLTUStaRxCapacity Kbps

get    
1.3.6.1.4.1.41112.1.10.1.5.3.0 afLTURxBytes Bytes 
1.3.6.1.4.1.41112.1.10.1.5.1.0 afLTUTxBytes Bytes

airfiber non-aftlu: https://mibs.observium.org/mib/UBNT-AirFIBER-MIB/
------

The following snmp ids are acquired with snmpget:
1.3.6.1.4.1.41112.1.3.3.1.64.1 throughputx  txoctetsAll Bytes
1.3.6.1.4.1.41112.1.3.3.1.66.1 throughputrx rxoctetsAll Bytes
1.3.6.1.4.1.41112.1.3.2.1.6.1 capacitytx txCapacity bits/second
1.3.6.1.4.1.41112.1.3.2.1.5.1 capacityrx  rxCapacity 	bits/second
1.3.6.1.4.1.41112.1.3.1.1.14.1 sysname  linkName


