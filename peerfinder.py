#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

# Author: Alex Rad (alecsrad)
# Author: Ruairi Carroll (rucarrol)

# Purpose: Generate a table of common IX points between two ASNs.

import json
import argparse
import requests
from prettytable import PrettyTable


def main():

    args = getArgs()
    asns = args.asn
    pdata = dict() 
    for asn in asns: 
        pdata[asn] = getPeeringDB(asn)

    # Lets check to see if we have valid data in our replies. 
    try:
        for asn in pdata.keys():
            asn = pdata[str(asn)]['data'][0]['asn']
            peer_name = pdata[str(asn)]['data'][0]['name']
    except IndexError:
        print("Looks like an empty dataset, exiting")
        print("result: %s" % pdata[asn])
        exit(1)

    if args.ix_only:

        # Dump all our ix names into a list
        ixp = dict()
        for asn in pdata.keys():
            ixp[asn] = getFac(pdata[str(asn)], "netixlan_set")

        # For all our IXs, see if they have the same IX
        # Have to seed the common ix list with the first entry, otherwise the intersection of [] will always be []

        common_ix_list = ixp[ixp.keys()[0]]
        for asn in ixp:
            common_ix_list = list(set(ixp[asn]).intersection(common_ix_list))


        if len(common_ix_list) < 1:
            print("Didnt find any common IX, exiting...")
            exit(1)
        header = []
        header.append('IX')
        for asn in pdata.keys():
            header.append(pdata[asn]['data'][0]['name'])
        ix_tab = PrettyTable(header)
        ix_tab.print_empty = False

        for ix in common_ix_list:
            row = [ix]
            for asn in pdata.keys():
                for i in pdata[asn]['data'][0]['netixlan_set']:
                    if i['name'] not in common_ix_list:
                        continue
                    if ix == i['name']:
                        # Skip if ix is not in our shared list.
                        for entry in row:
                            if str(i['asn']) in entry:
                                row.remove(entry)
                                line = line + "\nv4: %s\nv6: %s" % (i['ipaddr4'],i['ipaddr6'])
                            else: 
                                line = "AS: %s\nv4: %s\nv6: %s" % (i['asn'],i['ipaddr4'],i['ipaddr6'])
                        row.append(line)
            ix_tab.add_row(row)

        ix_tab.hrules = 1
        print(ix_tab.get_string(sortby="IX"))


    if args.fac_only:
        # Dump all our ix names into a list
        priv = dict()
        for asn in pdata.keys():
            priv[asn] = getFac(pdata[str(asn)], "netfac_set")

        # For all our IXs, see if they have the same IX
        # Have to seed the common ix list with the first entry, otherwise the intersection of [] will always be []

        common_priv_list = priv[priv.keys()[0]]
        for asn in priv:
            common_priv_list = list(set(priv[asn]).intersection(common_priv_list))


        if len(common_priv_list) < 1:
            print("Didnt find any common Private facilities, exiting...")
            exit(1)
        header = ['Facility', 'City', 'Country']

        fac_tab = PrettyTable(header)
        fac_tab.print_empty = False

        for fac in common_priv_list:
            row = []
            for asn in pdata.keys():
                for i in pdata[asn]['data'][0]['netfac_set']:
                    if i['name'] not in common_priv_list:
                        continue
                    if fac == i['name']:
                        row = [i['name'], i['city'], i['country']]
            fac_tab.add_row(row)

        fac_tab.hrules = 1
        print(fac_tab.get_string(sortby="Facility"))

    exit(0)

def getArgs():
    help_text = "Generate a table for common points in an IX. -h for help"
    parser = argparse.ArgumentParser(help_text)
    parser.add_argument('--asn', nargs = '+', dest = 'asn', help = 'List of ASNs')

    xgroup = parser.add_mutually_exclusive_group()
    xgroup.add_argument('--ix-only',      dest='ix_only',  help='Print IX results only', action='store_true')
    xgroup.add_argument('--private-only', dest='fac_only', help='Print private facility results only', action='store_true')

    args = parser.parse_args()
    ## Validate args here
    return args


def getPeeringDB(ASN):
    """Function to connect to peeringDB and fetch results for a given ASN

    Args:
        ASN: A numeric, 32 bit number AS number.

    Returns:
        A dict which contains the dataset for a given ASN. Specific API docs here: https://api.peeringdb.com/apidocs/#!/net/Network_list

    """
    HTTP_OK = 200
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

if __name__ == "__main__":
    main()