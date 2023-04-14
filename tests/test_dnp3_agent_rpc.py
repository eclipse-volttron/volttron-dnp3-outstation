"""
This test suits focus on exposed RPC calls.
It utilizes a vip agent to evoke the RPC calls.
The volltron instance and dnp3-agent is start manually.
Note: need to define VOLTTRON_HOME and vip-identity for dnp3 outstation agent
Note: The `launch-agent` script can be used to start the dnp3 outstation agent.
"""
import gevent
import pytest
import os
from volttron.client.vip.agent import build_agent
from time import sleep
import datetime
from dnp3_outstation.agent import Dnp3OutstationAgent
from dnp3_python.dnp3station.outstation_new import MyOutStationNew
import random
import subprocess
from volttron.utils import is_volttron_running

dnp3_vip_identity = "dnp3_outstation"


@pytest.fixture(scope="module")
def volttron_home():
    """
    VOLTTRON_HOME environment variable suggested to setup at pytest.ini [env]
    """
    volttron_home: str = os.getenv("VOLTTRON_HOME")
    assert volttron_home
    return volttron_home


def test_volttron_home_fixture(volttron_home):
    assert volttron_home
    print(volttron_home)


def test_testing_file_path():
    parent_path = os.getcwd()
    dnp3_agent_config_path = os.path.join(parent_path, "dnp3-outstation-config.json")
    print(dnp3_agent_config_path)


@pytest.fixture(scope="module")
def volttron_platform_wrapper_new(volttron_home):
    print("========== 1st", is_volttron_running(volttron_home))
    # start the platform, check status with flexible retry
    res = subprocess.Popen(["volttron"])  # use Popen, no-blocking
    max_try = 10
    while not is_volttron_running(volttron_home) and max_try > 0:
        gevent.sleep(1)
        print(f"starting platform, left to try: {max_try}")
        max_try -= 1
    print("========== 2nd", is_volttron_running(volttron_home))

    yield volttron_home

    subprocess.Popen(["vctl", "shutdown", "--platform"])
    max_try = 10
    while is_volttron_running(volttron_home) and max_try > 0:
        gevent.sleep(1)
        print(f"shutting down platform, left to try: {max_try}")
        max_try -= 1
    print("========== 3rd", is_volttron_running(volttron_home))

def test_volttron_platform_wrapper_new_fixture(volttron_platform_wrapper_new):
    print(volttron_platform_wrapper_new)


@pytest.fixture(scope="module")
def vip_agent(volttron_platform_wrapper_new):

    # build a vip agent
    a = build_agent()
    print(a)

    # # install a dnp3-outstation-agent
    # parent_path = os.getcwd()
    # dnp3_agent_config_path = os.path.join(parent_path, "dnp3-outstation-config.json")
    # cmd = f"vctl install volttron-dnp3-outstation --agent-config {dnp3_agent_config_path} " +\
    #       "--vip-identity dnp3_outstation --start --force"
    # res = subprocess.run(cmd.split(" "),
    #                      stdout=subprocess.PIPE)
    # print(f"=========== cmd {cmd}, res {res.stdout}")

    return a


def test_install_dnp3_outstation_agent(vip_agent):


    # install a dnp3-outstation-agent
    parent_path = os.getcwd()
    dnp3_agent_config_path = os.path.join(parent_path, "dnp3-outstation-config.json")
    cmd = f"vctl install volttron-dnp3-outstation --agent-config {dnp3_agent_config_path} " +\
          "--vip-identity dnp3_outstation --start --force"
    res = subprocess.run(cmd.split(" "),
                         stdout=subprocess.PIPE)
    print(f"=========== cmd {cmd}, res {res.stdout}")

    gevent.sleep(10)
    cmd = f"vctl status"
    res = subprocess.run(cmd.split(" "),
                         stdout=subprocess.PIPE)
    print(f"=========== cmd {cmd}, res {res.stdout}")

    res = vip_agent.vip.peerlist.list().get(10)
    print(f"=========== vip_agent.vip.peerlist.list().get(10), res {res}")


def test_sandbox():
    pass
    from volttrontesting.platformwrapper import PlatformWrapper
    pw = PlatformWrapper()
    res = pw.agent_pid("577a5e05-6ad6-43f8-a859-08399f8fe0cd")
    print("============", res)


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
