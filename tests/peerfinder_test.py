import unittest
from unittest.mock import Mock
import mock
import peerfinder.peerfinder as peerfinder
import requests
from ipaddress import IPv6Address, IPv4Address


class testPeerFinder(unittest.TestCase):
    def setUp(self):
        self.netixlan_set = {
            "id": 1,
            "ix_id": 2,
            "name": "Test IX",
            "ixlan_id": 3,
            "notes": "",
            "speed": 1000,
            "asn": 65536,
            "ipaddr4": ["192.0.2.1"],
            "ipaddr6": ["0100::"],
            "is_rs_peer": True,
            "operational": True,
            "created": "2010-01-01T00:00:00Z",
            "updated": "2010-01-01T00:00:00Z",
            "status": "ok",
        }

        self.netfac_set = {
            "id": 1,
            "name": "Test Facility",
            "city": "Dublin",
            "country": "IE",
            "fac_id": 1,
            "local_asn": 65536,
            "created": "2010-01-01T00:00:00Z",
            "updated": "2010-01-01T00:00:00Z",
            "status": "ok",
        }
        self.peer = {"name": "Test Peer", "asn": 65536}

    def test_pdb_to_ixp(self):
        expected = peerfinder.IXP(
            name="Test IX",
            subnet4=[IPv4Address("192.0.2.1")],
            subnet6=[IPv6Address("0100::")],
            speed=1000,
        )
        self.assertEqual(expected, peerfinder.pdb_to_ixp(self.netixlan_set))

    def test_pdb_to_peer(self):
        ixp = peerfinder.pdb_to_ixp(self.netixlan_set)
        fac = peerfinder.pdb_to_fac(self.netfac_set)
        expected = peerfinder.Peer(
            name="Test Peer", ASN=65536, peering_on=ixp, present_in=fac,
        )
        self.assertEqual(expected, peerfinder.pdb_to_peer(self.peer, ixp, fac))

    def test_pdb_to_fac(self):
        expected = peerfinder.Facility(name="Test Facility", ASN=65536)
        self.assertEqual(expected, peerfinder.pdb_to_fac(self.netfac_set))

    def test__dedup_ixs(self):
        expected = {
            "Test IX": {
                "ipaddr4": [["192.0.2.1"], ["192.0.2.1"]],
                "ipaddr6": [["0100::"], ["0100::"]],
                "name": "Test IX",
                "speed": 2000,
            }
        }
        self.assertEqual(
            expected, peerfinder._dedup_ixs([self.netixlan_set, self.netixlan_set]),
        )

    def test_fetch_ix_from_ixps(self):
        expected = peerfinder.pdb_to_ixp(self.netixlan_set)
        ixp = [peerfinder.pdb_to_ixp(self.netixlan_set)]
        self.assertEqual(expected, peerfinder.fetch_ix_from_ixps("Test IX", ixp))

    def test_fetch_fac_from_facilities(self):
        expected = peerfinder.pdb_to_fac(self.netfac_set)
        fac = [peerfinder.pdb_to_fac(self.netfac_set)]
        self.assertEqual(expected, peerfinder.fetch_ix_from_ixps("Test Facility", fac))

    def test_fetch_common_ixps(self):
        ixp = [peerfinder.pdb_to_ixp(self.netixlan_set)]
        fac = [peerfinder.pdb_to_fac(self.netfac_set)]
        peer = [peerfinder.pdb_to_peer(self.peer, ixp, fac)]
        expected = {"Test IX"}
        self.assertEqual(expected, peerfinder.fetch_common_ixps(peer))

    def test_fetch_common_facilities(self):
        ixp = [peerfinder.pdb_to_ixp(self.netixlan_set)]
        fac = [peerfinder.pdb_to_fac(self.netfac_set)]
        peer = [peerfinder.pdb_to_peer(self.peer, ixp, fac)]
        expected = {"Test Facility"}
        self.assertEqual(expected, peerfinder.fetch_common_facilities(peer))

    @mock.patch.object(requests, "get", autospec=True)
    def test_getPeeringDBSuccess(self, requests_mock):
        r_mock = Mock()
        r_mock.status_code = 200
        r_mock.text = "some text"
        r_mock.json.return_value = {"data": [0]}
        requests_mock.return_value = r_mock
        expected = {"data": [0]}
        self.assertEqual(expected, peerfinder.getPeeringDB("23456"))

    def test_fetch_fac_from_facilities(self):
        fac = [peerfinder.pdb_to_fac(self.netfac_set)]
        fac_name = "Test Facility"
        expected = peerfinder.Facility(name="Test Facility", ASN=65536)
        self.assertEqual(expected, peerfinder.fetch_fac_from_facilities(fac_name, fac))

    def test_fetch_different_ixps(self):
        ix1 = peerfinder.IXP(
            name="Test IX1",
            subnet4=[IPv4Address("192.0.2.1")],
            subnet6=[IPv6Address("0100::")],
            speed=1000,
        )
        ix2 = peerfinder.IXP(
            name="Test IX2",
            subnet4=[IPv4Address("192.0.2.2")],
            subnet6=[IPv6Address("0100::")],
            speed=1000,
        )
        expected = ["Test IX1", "Test IX2"]
        peer1 = peerfinder.Peer(name="peer1", ASN=1, present_in=[], peering_on=[ix1])
        peer2 = peerfinder.Peer(name="peer2", ASN=1, present_in=[], peering_on=[ix2])
        self.assertEqual(expected, peerfinder.fetch_different_ixps([peer1, peer2]))

    def test_print_ixp(self):
        ix1 = peerfinder.IXP(
            name="Test IX1",
            subnet4=[IPv4Address("192.0.2.1")],
            subnet6=[IPv6Address("0100::")],
            speed=1000,
        )
        ix2 = peerfinder.IXP(
            name="Test IX2",
            subnet4=[IPv4Address("192.0.2.2")],
            subnet6=[IPv6Address("0100::")],
            speed=1000,
        )
        peer1 = peerfinder.Peer(name="peer1", ASN=1, present_in=[], peering_on=[ix1])
        peer2 = peerfinder.Peer(
            name="peer2", ASN=1, present_in=[], peering_on=[ix1, ix2]
        )
        self.assertIsNone(peerfinder.print_ixp([peer1, peer2]))

    def test_print_fac(self):
        fac1 = peerfinder.Facility(name="Test Facility 1", ASN=1,)
        fac2 = peerfinder.Facility(name="Test Facility 2", ASN=1,)
        peer1 = peerfinder.Peer(
            name="peer1", ASN=1, present_in=[fac1, fac2], peering_on=[]
        )
        peer2 = peerfinder.Peer(name="peer2", ASN=1, present_in=[fac1], peering_on=[])
        self.assertIsNone(peerfinder.print_fac([peer1, peer2]))

    def test_print_uncommon(self):
        ix1 = peerfinder.IXP(
            name="Test IX1",
            subnet4=[IPv4Address("192.0.2.1")],
            subnet6=[IPv6Address("0100::")],
            speed=1000,
        )
        ix2 = peerfinder.IXP(
            name="Test IX2",
            subnet4=[IPv4Address("192.0.2.2")],
            subnet6=[IPv6Address("0100::")],
            speed=1000,
        )
        peer1 = peerfinder.Peer(name="peer1", ASN=1, present_in=[], peering_on=[ix1])
        peer2 = peerfinder.Peer(
            name="peer2", ASN=1, present_in=[], peering_on=[ix1, ix2]
        )
        self.assertIsNone(peerfinder.print_uncommon([peer1, peer2]))


if __name__ == "__main__":
    unittest.main()
