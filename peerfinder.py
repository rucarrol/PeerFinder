#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

# Author: Alex Rad (alecsrad)
# Author: Ruairi Carroll (rucarrol)

# Purpose: Generate a table of common IX points between two ASNs.

import json
import argparse
import requests
from prettytable import PrettyTable

def getPeeringDB(ASN):
    HTTP_OK = 200
    ## Get my data, their data
    pdb_url = 'https://api.peeringdb.com/api/net?asn__in=%s&depth=2' % ASN
    print("Fetching PeeringDB info for %s" % ASN)
    r = requests.get(pdb_url)
    if r.status_code != HTTP_OK:
        print("Got unexpected status code, exiting")
        print("%s - %s" % (r.status, r.text))
        exit(1)
    pdb_res = r.json()
    return pdb_res

def getFac(pdb, nettype):
    fac_set = []
    for item in pdb['data'][0][nettype]:
        fac_set.append(item['name'])
    return fac_set

help_text = "Generate a table for common points in an IX. -h for help"
parser = argparse.ArgumentParser(help_text)
parser.add_argument('--myasn', help='My ASN', default='13414')
parser.add_argument('--peerasn', help='Peer ASN', default='13414')

xgroup = parser.add_mutually_exclusive_group()
xgroup.add_argument('--ix-only', dest='ix_only', help='Print IX results only', action='store_false', default=True)
xgroup.add_argument('--private-only', dest='fac_only',
                    help='Print private facility results only', action='store_false', default=True)

args = parser.parse_args()

results_mine = getPeeringDB(args.myasn)
results_theirs = getPeeringDB(args.peerasn)

try:
    asn = results_theirs['data'][0]['asn']
    peer_name = results_theirs['data'][0]['name']
except IndexError:
    print("Looks like an empty dataset, exiting")
    print("result: %s" % results_theirs)
    exit(1)

if args.ix_only:

    # Dump all our ix names into a list
    my_ix_list = getFac(results_mine, "netixlan_set")
    peer_ix_list = getFac(results_theirs, "netixlan_set")

    # For all our IXs, see if they have the same IX
    common_ix_list = list(set(my_ix_list).intersection(peer_ix_list))
    if len(common_ix_list) < 1:
        print("Didnt find any common IX")

    ix_tab = PrettyTable(['IX', 'ASN', 'IPv4', 'IPv6'])
    ix_tab .print_empty = False

    for i in results_theirs['data'][0]['netixlan_set']:
        # Skip if ix is not in our shared list.
        ix = i['name']
        if ix not in common_ix_list:
            continue
        # populate the dict : router->IX->Peering info
        ix_tab.add_row([ix, i['asn'], i['ipaddr4'], i['ipaddr6']])

    print(ix_tab.get_string(sortby="IX"))


if args.fac_only:
    # Dump all our ix names into a list
    my_priv_list = getFac(results_mine, "netfac_set")
    peer_priv_list = getFac(results_theirs, "netfac_set")

    # For all our IXs, see if they have the same IX
    common_priv_list = list(set(my_priv_list).intersection(peer_priv_list))
    if len(common_priv_list) < 1:
        print("Didnt find any common private facilities")

    # Find common facilities - only need city/country here.
    priv_tab = PrettyTable(['Facility', 'City', 'Country'])
    priv_tab.print_empty = False

    for i in results_theirs['data'][0]['netfac_set']:
        # Skip if ix is not in our shared list.
        ix = i['name']
        if ix not in common_priv_list:
            continue
        # populate the dict : router->IX->Peering info
        priv_tab.add_row([ix, i['city'], i['country']])

    print(priv_tab.get_string(sortby="Facility"))

exit(0)