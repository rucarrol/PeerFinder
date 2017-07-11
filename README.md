# PeeringTools

[![Build Status](https://travis-ci.org/rucarrol/PeerFinder.png)](https://travis-ci.org/rucarrol/PeerFinder)

## Intro

PeerFinder is a simple python script to see the common points of presence between two ASNs as reported by [PeeringDB](peeringdb.com). 

The tool takes two mandatory arguments: `--myasn` and `--peerasn`. There are two optional arguments to control output: `--ix-only` and `--private-only`. 

```
$ python peerfinder.py --myasn 13414 --peerasn 2603 --ix-only
Fetching PeeringDB info for 13414
Fetching PeeringDB info for 2603
+------------------------------------+------+-----------------+-------------------------+
|                 IX                 | ASN  |       IPv4      |           IPv6          |
+------------------------------------+------+-----------------+-------------------------+
|               AMS-IX               | 2603 |  80.249.209.203 | 2001:7f8:1::a500:2603:1 |
|       DE-CIX Frankfurt: Main       | 2603 |  80.81.192.241  |    2001:7f8::a2b:0:1    |
|          Equinix Ashburn           | 2603 | 206.126.236.230 |   2001:504:0:2::2603:1  |
|          Equinix Chicago           | 2603 | 206.223.119.151 |   2001:504:0:4::2603:1  |
|         Equinix Palo Alto          | 2603 |  198.32.176.208 |    2001:504:d::2603:1   |
|                HKIX                | 2603 |  123.255.91.213 |           None          |
|          LINX LON1: Main           | 2603 |  195.66.225.24  |    2001:7f8:4::a2b:1    |
|                NOTA                | 2603 |  198.32.125.73  |    2001:478:124::1073   |
|               NYIIX                | 2603 |  198.32.160.21  | 2001:504:1::a500:2603:1 |
| Netnod Stockholm: STH-A -- MTU1500 | 2603 |  194.68.123.24  |    2001:7f8:d:ff::24    |
| Netnod Stockholm: STH-A -- MTU4470 | 2603 |  195.245.240.24 |    2001:7f8:d:fc::24    |
| Netnod Stockholm: STH-B -- MTU1500 | 2603 |  194.68.128.24  |    2001:7f8:d:fe::24    |
| Netnod Stockholm: STH-B -- MTU4470 | 2603 |  195.69.119.24  |    2001:7f8:d:fb::24    |
+------------------------------------+------+-----------------+-------------------------+


$ python peerfinder.py --myasn 13414 --peerasn 2603 --private-only
Fetching PeeringDB info for 13414
Fetching PeeringDB info for 2603
+----------------------------------------------------+-----------+---------+
|                      Facility                      |    City   | Country |
+----------------------------------------------------+-----------+---------+
|             Equinix Ashburn (DC1-DC11)             |  Ashburn  |    US   |
|           Equinix Chicago (CH1/CH2/CH4)            |  Chicago  |    US   |
|           Equinix London Docklands (LD8)           |   London  |    GB   |
|              Equinix Palo Alto (SV8)               | Palo Alto |    US   |
| Interxion Stockholm (STO1, STO2, STO3, STO4, STO5) | Stockholm |    SE   |
|                   Verizon Miami                    |   Miami   |    US   |
+----------------------------------------------------+-----------+---------+
```


## Bugs

Probably many. PRs or bug reports very welcome. 

## Feature requests 

TODO: Make installable via pip
