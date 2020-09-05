#!/usr/bin/env python -tt
# -*- coding: utf-8 -*-

# Author: Alex Rad (alecsrad)
# Author: Ruairi Carroll (rucarrol)

# Purpose: Generate a table of common IX points between two ASNs.

import argparse
import requests
from prettytable import PrettyTable
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import List, Dict


class Error(Exception):
    """Base Error Handler."""


class NoIXFoundException(Error):
    """IX Not Found Exception."""


@dataclass
class IXP:
    """IXP represents a specific IXP entry.

    Attributes:
        name: The IXP name as per name key fac_set results set from PeeringDB.
        speed: Total port capacity in Mbit for this peer on this IX.
        subnet4: List of IPv4 subnets at this IXP.
        subnet6: List of IPv6 subnets at this IXP.
    """

    name: str
    speed: int
    subnet4: List[IPv4Address]
    subnet6: List[IPv6Address]


@dataclass
class Facility:
    """Facility represents a private peering facility.

    Attributes:
      name: The facility name.
      ASN: Local asn.
    """

    name: str
    ASN: int


@dataclass
class Peer:
    """Peer represents all IXPs a given Peer is on.

    Attributes:
      name: The peer name as per the name key in returned JSON blob from PeeringDB.
      ASN: Peers ASN.
      peering_on: All IXPs this given peer exists on.
    """

    name: str
    ASN: int
    peering_on: List[IXP]
    present_in: List[Facility]


def main():

    args = getArgs()
    pdata = dict()
    peers = list()
    [pdata.update({i: getPeeringDB(i)}) for i in args.asn]

    for asn, pdb in pdata.items():
        ix_dedup = _dedup_ixs(pdb["data"][0]["netixlan_set"])
        ix_set = [pdb_to_ixp(ix) for _, ix in ix_dedup.items()]
        netfac_set = [pdb_to_fac(ix) for ix in pdb["data"][0]["netfac_set"]]
        peers.append(pdb_to_peer(pdb["data"][0], ix_set, netfac_set))

    if args.ix_only:
        print_ixp(peers)

    if args.fac_only:
        print_fac(peers)

    if args.missing:
        print_uncommon(peers)

    exit(0)


def pdb_to_ixp(netixlan_set: Dict) -> IXP:
    """Convert an netixlan_set into an IXP."""
    return IXP(
        name=netixlan_set["name"],
        speed=netixlan_set["speed"],
        subnet4=[IPv4Address(i) for i in netixlan_set["ipaddr4"]],
        subnet6=[IPv6Address(i) if i else "0100::" for i in netixlan_set["ipaddr6"]],
    )


def pdb_to_peer(pdb: Dict, ixlan_set: List[IXP], netfac_set: List[Facility]) -> Peer:
    """Convert peeringDB reply to a Peer Object.

    Arguments:
        pdb: A dict from PeeringDB representing a given ASNs peering record.

    Returns:
        A Peer object.
    """
    return Peer(
        name=pdb["name"], ASN=pdb["asn"], peering_on=ixlan_set, present_in=netfac_set
    )


def pdb_to_fac(netfac_set: Dict) -> Facility:
    """Convert peeringDB reply to a Facility Object.

    Arguments:
        pdb: A dict from PeeringDB representing a given ASNs netfac_set.

    Returns:
        A Facility object.
    """
    return Facility(name=netfac_set["name"], ASN=netfac_set["local_asn"])


def _dedup_ixs(ixlan_set: Dict) -> Dict:
    """Since PeeringDB considers each v4/v6 entry unique, bundle all records per IX name.

    Arguments:
        netlax_set: A dict from PeeringDB that represents all the IXPs an ASN is on.

    Returns:
        A dict containing the name,v4 and v6 addr of a given IXP an ASN is on.
    """
    ix_dedup = dict()
    for ix in ixlan_set:
        if ix["name"] not in ix_dedup:
            ix_dedup[ix["name"]] = dict()
            ix_dedup[ix["name"]]["name"] = ix["name"]
            ix_dedup[ix["name"]]["speed"] = int(ix["speed"])
            ix_dedup[ix["name"]]["ipaddr4"] = [ix["ipaddr4"]]
            ix_dedup[ix["name"]]["ipaddr6"] = [ix["ipaddr6"]]
        else:
            ix_dedup[ix["name"]]["speed"] += int(ix["speed"])
            ix_dedup[ix["name"]]["ipaddr4"].append(ix["ipaddr4"])
            ix_dedup[ix["name"]]["ipaddr6"].append(ix["ipaddr6"])
    return ix_dedup


def fetch_ix_from_ixps(ix: str, ixps: List[IXP]) -> IXP:
    """Return the IXP object for a given IX.

    Arguments:
        ix: The name of an IX you want to match.
        ixps: A list of IXP objects from a given peer.

    Raises:
        NoIXFoundException: If IX not found in list.

    Returns:
        A single IXP entry matching the name of IX.

    """
    ret = [i for i in ixps if i.name == ix]
    if not ret:
        raise NoIXFoundException(f"No IX Found for {ix}")
    else:
        return ret.pop()


def fetch_fac_from_facilities(fac: str, facs: List[Facility]) -> Facility:
    """Return the Facility object for a given Facility.

    Arguments:
        fac: The name of an IX you want to match.
        ixps: A list of IXP objects from a given peer.

    Returns:
        A single Facility entry matching the name of Facility.

    """
    return next(i for i in facs if i.name == fac)


def fetch_common_ixps(peers: List[Peer]) -> List[str]:
    """Return a list of common IXPs.

    Arguments:
        peers: A list of Peer objects for a given ASN.

    Returns:
        A list of common IX points, based in their name.
    """
    common_ix = set([i.name for i in peers[0].peering_on])
    for peer in peers:
        common_ix = common_ix.intersection(set([i.name for i in peer.peering_on]))
    return common_ix


def fetch_different_ixps(peers: List[Peer]) -> List[str]:
    """Return a list of IXPs which none of the peers have in common.

    Arguments:
        peers: A list of Peer objects for a given ASN.

    Returns:
        A list of uncommon IXPs, based in their name.
    """
    common_ix = fetch_common_ixps(peers)
    uncommon = list()
    for peer in peers:
        uncommon.extend([i.name for i in peer.peering_on if i.name not in common_ix])
    return uncommon


def fetch_common_facilities(facilities: List[Facility]) -> List[str]:
    """Return a list of common Facilities.

    Arguments:
        facilities: A list of Facility objects for a given ASN.

    Returns:
        A list of common Facilities, based in their name.
    """
    common_fac = set([i.name for i in facilities[0].present_in])
    for fac in facilities:
        common_fac = common_fac.intersection(set([i.name for i in fac.present_in]))
    return common_fac


def print_ixp(peers: List[Peer]) -> None:
    common_ix_list = fetch_common_ixps(peers)
    if len(common_ix_list) < 1:
        print("Didnt find any common IX, exiting...")
        exit(1)
    header = list()
    header.append("IX")
    for peer in peers:
        header.append(peer.name)

    ix_tab = PrettyTable(header)
    ix_tab.print_empty = False

    for ix in common_ix_list:
        row = [ix]
        for peer in peers:
            curr_ix = fetch_ix_from_ixps(ix, peer.peering_on)
            v4 = "v4: " + "\n".join([str(i) for i in curr_ix.subnet4])
            v6 = "v6: " + "\n".join(
                [str(i) for i in curr_ix.subnet6 if str(i) != "0100::"]
            )
            v6 = v6 if v6 != "v6: " else ""
            line = f"{v4}\n{v6}"
            row.append(line)
        ix_tab.add_row(row)

    ix_tab.hrules = 1
    print(ix_tab.get_string(sortby="IX"))
    return None


def print_fac(peers: List) -> None:
    common_fac_list = fetch_common_facilities(peers)
    if len(common_fac_list) < 1:
        print("Didnt find any common Facility, exiting...")
        exit(1)
    header = []
    header.append("Facility")
    for peer in peers:
        header.append(peer.name)

    ix_tab = PrettyTable(header)
    ix_tab.print_empty = False

    for fac in common_fac_list:
        row = [fac]
        for peer in peers:
            curr_fac = fetch_fac_from_facilities(fac, peer.present_in)
            line = f"ASN: {curr_fac.ASN}"
            row.append(line)
        ix_tab.add_row(row)

    ix_tab.hrules = 1
    print(ix_tab.get_string(sortby="Facility"))


def print_uncommon(peers: List) -> None:
    uncommon_ix_list = fetch_different_ixps(peers)
    if len(uncommon_ix_list) < 1:
        print("Didnt find any uncommon Facility, exiting...")
        exit(1)
    header = list()
    header.append("IX")
    for peer in peers:
        header.append(f"{peer.name} speed")

    ix_tab = PrettyTable(header)
    ix_tab.print_empty = False

    for ix in uncommon_ix_list:
        row = [ix]
        for peer in peers:
            try:
                curr_ix = fetch_ix_from_ixps(ix, peer.peering_on)
                speed = curr_ix.speed
                line = f"{speed}Mbit"
                row.append(line)
            except NoIXFoundException as e:
                line = ""
                row.append(line)
        ix_tab.add_row(row)

    ix_tab.hrules = 1
    print(ix_tab.get_string(sortby=f"{peer.name} speed", reversesort=True))


def getArgs():
    help_text = "Generate a table for common points in an IX. -h for help"
    parser = argparse.ArgumentParser(help_text)
    parser.add_argument("--asn", nargs="+", dest="asn", help="List of ASNs")
    parser.add_argument(
        "--missing", action="store_true", dest="missing", help="Print missing IXs", default=False,
    )
    parser.add_argument(
        "--ix", dest="ix_only", help="Print IX results", action="store_true", default=False,
    )
    parser.add_argument(
        "--private",
        dest="fac_only",
        help="Print private facility results",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()
    # Validate args here
    if not args.asn:
        print("--asn must be specified!")
        exit(1)
    if not any([args.ix_only, args.fac_only, args.missing]):
        print("Must specify --ix, --private or --missing!")
        exit(1)

    return args


def getPeeringDB(ASN: str) -> Dict:
    """Function to connect to peeringDB and fetch results for a given ASN

    Args:
        ASN: ASN to query against PeeringDB's API.

    Returns:
        r.json: a dict containing the results from PeeringDB

    """
    pdb_url = f"https://api.peeringdb.com/api/net?asn__in={ASN}&depth=2"
    print(f"Fetching PeeringDB info for {ASN}")
    r = requests.get(pdb_url)
    if r.status_code != requests.status_codes.codes.ALL_OK:
        print("Got unexpected status code, exiting")
        print("%s - %s" % (r.status, r.text))
        exit(1)
    if len(r.json()["data"]) != 1:
        print(
            f"Got unexpected number of replies for {ASN}(Does ASN exist in PeeringDB?). Exiting"
        )
        exit(1)
    return r.json()


if __name__ == "__main__":
    main()
