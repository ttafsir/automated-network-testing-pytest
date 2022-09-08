import pytest


@pytest.mark.underlay
@pytest.mark.ready_for_use
def test_underlay_p2p_link_neighbors_are_correct():
    ...


@pytest.mark.underlay
def test_underlay_p2p_bgp_peerings_are_established():
    ...


@pytest.mark.evpn
def test_underlay_bgp_evpn_peerings_are_established():
    ...
