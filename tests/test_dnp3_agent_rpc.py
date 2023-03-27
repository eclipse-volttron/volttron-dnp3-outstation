"""
This test suits focus on exposed RPC calls.
It utilizes a vip agent to evoke the RPC calls.
The volltron instance and dnp3-agent is start manually.
Note: need to define VOLTTRON_HOME and vip-identity for dnp3 outstation agent
Note: The `launch-agent` script can be used to start the dnp3 outstation agent.
"""
import pytest
import os
from volttron.client.vip.agent import build_agent
from time import sleep
import datetime
from dnp3_outstation.agent import Dnp3OutstationAgent
from dnp3_python.dnp3station.outstation_new import MyOutStationNew
import random

dnp3_vip_identity = "dnp3_outstation"


@pytest.fixture(scope="module")
def vip_agent():
    a = build_agent()
    print(a)
    return a


def test_vip_agent(vip_agent):
    print(vip_agent)


def test_dummy(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.rpc_dummy
    peer_method = method.__name__  # "rpc_dummy"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_reset(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.reset_outstation
    peer_method = method.__name__  # "reset_outstation"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_get_db(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.display_outstation_db
    peer_method = method.__name__  # "display_outstation_db"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_get_config(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.get_outstation_config
    peer_method = method.__name__  # "get_outstation_config"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_is_connected(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.is_outstation_connected
    peer_method = method.__name__  # "is_outstation_connected"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_apply_update_analog_input(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.apply_update_analog_input
    peer_method = method.__name__  # "apply_update_analog_input"
    val, index = random.random(), random.choice(range(5))
    print(f"val: {val}, index: {index}")
    rs = vip_agent.vip.rpc.call(peer, peer_method, val, index).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)

    # verify
    val_new = rs.get("Analog").get(str(index))
    assert val_new == val


def test_outstation_apply_update_analog_output(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.apply_update_analog_output
    peer_method = method.__name__  # "apply_update_analog_output"
    val, index = random.random(), random.choice(range(5))
    print(f"val: {val}, index: {index}")
    rs = vip_agent.vip.rpc.call(peer, peer_method, val, index).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)

    # verify
    val_new = rs.get("AnalogOutputStatus").get(str(index))
    assert val_new == val


def test_outstation_apply_update_binary_input(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.apply_update_binary_input
    peer_method = method.__name__  # "apply_update_binary_input"
    val, index = random.choice([True, False]), random.choice(range(5))
    print(f"val: {val}, index: {index}")
    rs = vip_agent.vip.rpc.call(peer, peer_method, val, index).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)

    # verify
    val_new = rs.get("Binary").get(str(index))
    assert val_new == val


def test_outstation_apply_update_binary_output(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.apply_update_binary_output
    peer_method = method.__name__  # "apply_update_binary_output"
    val, index = random.choice([True, False]), random.choice(range(5))
    print(f"val: {val}, index: {index}")
    rs = vip_agent.vip.rpc.call(peer, peer_method, val, index).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)

    # verify
    val_new = rs.get("BinaryOutputStatus").get(str(index))
    assert val_new == val


def test_outstation_update_config_with_restart(vip_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.update_outstation
    peer_method = method.__name__  # "update_outstation"
    port_to_set = 20001
    rs = vip_agent.vip.rpc.call(peer, peer_method, port=port_to_set).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)

    # verify
    rs = vip_agent.vip.rpc.call(peer, "get_outstation_config").get(timeout=5)
    port_new = rs.get("port")
    # print(f"========= port_new {port_new}")
    assert port_new == port_to_set
