"""
This test suits focus on the exposed RPC calls.
It utilizes a vip agent to evoke the RPC calls.
The volltron instance and dnp3-agent is start manually.
Note: need to define VOLTTRON_HOME at pytest.ini
    and vip-identity for dnp3 outstation agent (default "dnp3_outstation")
Note: several fixtures are used
    volttron_platform_wrapper_new
    vip_agent
    dnp3_outstation_agent
"""
import pathlib

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
import json
from utils.testing_utils import *

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
    print(f"==== 1st, is_volttron_running at volttron_home={volttron_home}:  {is_volttron_running(volttron_home)}")
    # start the platform, check status with flexible retry
    process = subprocess.Popen(["volttron"])  # use Popen, no-blocking
    retry_call(f=is_volttron_running, f_kwargs=dict(volttron_home=volttron_home), max_retries=10, delay_s=1,
               pass_criteria=True)
    print(f"==== 2nd, is_volttron_running at volttron_home={volttron_home}:  {is_volttron_running(volttron_home)}")
    if not is_volttron_running(volttron_home):
        raise f"VOLTTRON platform failed to start with volttron_home: {volttron_home}."

    yield volttron_home
    # TODO: add clean up options to remove volttron_home
    subprocess.Popen(["vctl", "shutdown", "--platform"])
    retry_call(f=is_volttron_running, f_kwargs=dict(volttron_home=volttron_home), max_retries=10, delay_s=1,
               wait_before_call_s=2,
               pass_criteria=False)
    print(f"==== 3rd, is_volttron_running at volttron_home={volttron_home}:  {is_volttron_running(volttron_home)}")


def test_volttron_platform_wrapper_new_fixture(volttron_platform_wrapper_new):
    print(volttron_platform_wrapper_new)


@pytest.fixture(scope="module")
def vip_agent(volttron_platform_wrapper_new):
    # build a vip agent
    a = build_agent()
    print(a)
    return a


def test_vip_agent_fixture(vip_agent):
    print(vip_agent)


@pytest.fixture(scope="module")
def dnp3_outstation_agent(volttron_platform_wrapper_new) -> str:
    """
    Install and start a dnp3-outstation-agent, return its vip-identity
    """
    # TODO: use yield and add clean-up
    # install a dnp3-outstation-agent
    parent_path = os.getcwd()
    dnp3_outstation_package_path = pathlib.Path(parent_path).parent
    dnp3_agent_config_path = os.path.join(parent_path, "dnp3-outstation-config.json")
    agent_vip_id = dnp3_vip_identity
    # Note: for volttron 10.0.3a7, `vctl install <package-name>` will pip install from Pypi,
    # which does not point to the current code source.
    # Use `vctl install <package-path>` instead
    cmd = f"vctl install {dnp3_outstation_package_path} --agent-config {dnp3_agent_config_path} " + \
          f"--vip-identity {agent_vip_id}"
    print(f"========== 1st test_dnp3_agent_install vctl --json status", vctl_json_status())

    res = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE)  # Need to use subprocess.run to wait for the process finish
    # print(res.stdout.decode())

    print(f"========== 1st(b) test_dnp3_agent_install vctl --json status", vctl_json_status())
    # check if installed successfully

    res = retry_call(f=is_agent_installed, f_kwargs=dict(agent_vip_identity=agent_vip_id), max_retries=60, delay_s=2,
                     wait_before_call_s=2, pass_criteria=True)
    print(f"========== 1st(b) retry_call", res)

    # starting agent
    uuid = get_agent_uuid(agent_vip_id)
    start_agent(uuid)
    # check if starting successfully
    print(f"========== 3rd test_dnp3_agent_install vctl --json status", vctl_json_status())
    res = retry_call(f=is_agent_running, f_kwargs=dict(agent_vip_identity=agent_vip_id), max_retries=15, delay_s=2,
                     wait_before_call_s=2, pass_criteria=True)
    print(f"========== 3rd retry_call", res)
    return agent_vip_id


def test_install_dnp3_outstation_agent_fixture(dnp3_outstation_agent):
    print(dnp3_outstation_agent)


def test_dummy(vip_agent, dnp3_outstation_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.rpc_dummy
    peer_method = method.__name__  # "rpc_dummy"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_reset(vip_agent, dnp3_outstation_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.reset_outstation
    peer_method = method.__name__  # "reset_outstation"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_get_db(vip_agent, dnp3_outstation_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.display_outstation_db
    peer_method = method.__name__  # "display_outstation_db"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_get_config(vip_agent, dnp3_outstation_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.get_outstation_config
    peer_method = method.__name__  # "get_outstation_config"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_is_connected(vip_agent, dnp3_outstation_agent):
    peer = dnp3_vip_identity
    method = Dnp3OutstationAgent.is_outstation_connected
    peer_method = method.__name__  # "is_outstation_connected"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)


def test_outstation_apply_update_analog_input(vip_agent, dnp3_outstation_agent):
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


def test_outstation_apply_update_analog_output(vip_agent, dnp3_outstation_agent):
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


def test_outstation_apply_update_binary_input(vip_agent, dnp3_outstation_agent):
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


def test_outstation_apply_update_binary_output(vip_agent, dnp3_outstation_agent):
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


def test_outstation_update_config_with_restart(vip_agent, dnp3_outstation_agent):
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
