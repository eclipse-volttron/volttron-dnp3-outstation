"""
Utils for volttron platform integration testing
"""

import json
import subprocess
import gevent

import logging
import random
import time

from functools import partial

# from retry.compat import decorator


logging_logger = logging.getLogger(__name__)


def is_agent_in_peerlist(agent_vip_identity: str):
    """
    It means the agent is available at the message bus.
    """
    cmd = "vctl peerlist"
    res = subprocess.run(cmd, shell=True,
                         stdout=subprocess.PIPE)
    # print("==============", res.stdout)

    list_decode = res.stdout.decode().split("\n")
    peer_list = [peer for peer in list_decode if peer]  # note: last element in list_decode is empty (i.e., "")
    return agent_vip_identity in peer_list


def vctl_json_status() -> json:
    """
    internal method, returned a decoded json object when running `vctl --json status`
    Note: use retry_call with exception handling. (`vctl --json status` might not json-parsable)
    """
    cmd = "vctl --json status"

    # helper function to facilitate retry_call
    def _vctl_json_status(_cmd: str) -> json:
        res = subprocess.run(_cmd, shell=True,
                             stdout=subprocess.PIPE)

        json_decode = json.loads(res.stdout.decode('utf-8'))
        return json_decode

    return retry_call(f=_vctl_json_status, f_kwargs=dict(_cmd=cmd), max_retries=15, delay_s=2)


def is_agent_installed(agent_vip_identity: str):
    """
    In other word, it is available using `vctl status`
    """
    json_decode = vctl_json_status()

    return agent_vip_identity in json_decode


def is_agent_running(agent_vip_identity: str):
    """
    Decode and parse `vctl -json status` command result json_decode
    check json_decode[agent_vip_identity]["status"] filed.
    Possible result "0", "1", "running [<pid>]"
    """

    json_decode = vctl_json_status()

    if is_agent_installed(agent_vip_identity):
        return "running" in json_decode[agent_vip_identity]["status"]
    else:
        # raise ValueError(f"agent_vip_identity: {agent_vip_identity} is not in the peerlist")
        pass


def get_agent_uuid(agent_vip_identity: str) -> str:
    """
    Get (full) uuid from agent_vip_identity, e.g., return "3cddb413-c53b-4961-a4b2-0ab04d17ff22"
    """
    json_decode = vctl_json_status()

    if is_agent_installed(agent_vip_identity):
        return json_decode[agent_vip_identity]["agent_uuid"]
    else:
        # raise ValueError(f"agent_vip_identity: {agent_vip_identity} is not in the peerlist")
        pass


def start_agent(uuid: str) -> str:
    """
    start an agent using (full) uuid
    """
    cmd = f"vctl start {uuid}"
    res = subprocess.run(cmd, shell=True,
                         stdout=subprocess.PIPE)
    return res.stdout.decode()
    # process = subprocess.Popen(cmd, shell=True,
    #                            stdout=subprocess.PIPE)
    # return process.stdout.read().decode('utf-8')


def stop_agent(uuid: str) -> str:
    """
    start an agent using (full) uuid
    """
    cmd = f"vctl stop {uuid}"
    res = subprocess.run(cmd, shell=True,
                         stdout=subprocess.PIPE)
    return res.stdout.decode()


def restart_agent(uuid: str) -> str:
    """
    start an agent using (full) uuid
    """
    cmd = f"vctl restart {uuid}"
    res = subprocess.run(cmd, shell=True,
                         stdout=subprocess.PIPE)
    return res.stdout.decode()


class RetryCallExeption(Exception):
    """
    For def retry_call
    """
    pass


def retry_call(f: callable, f_args: list = None, f_kwargs: dict = None,
               pass_criteria: any = None,
               max_retries: int = 100, delay_s: int = 1, wait_before_call_s: int = 0,
               logger=None):
    """
    A retry_call wrapper, check f(*f_args, **f_kwargs)'s result,
    control 1: if pass_criteria is not None, then _is_check_exception_only=False:
        if result = pass_criteria return result, otherwise retry
    control 2: otherwise, i.e., only handle exception
        retry if there is an exception
    Note: not guarantee retry will succeed

    EXAMPLE:
        def add(a, b, c):
            return 100 * a + 10 * b + c
        retry_call(f=add, f_kwargs=dict(a=3, b=1, c=2), pass_criteria=100)  # will retry
        retry_call(f=add, f_kwargs=dict(a=3, b=1, c=2), pass_criteria=312)  # will pass
    """
    if f_args is None:
        f_args = []
    if f_kwargs is None:
        f_kwargs = {}
    if logger is None:
        logger = logging_logger

    # wait before call
    gevent.sleep(wait_before_call_s)

    # control workflows
    _is_check_exception_only: bool
    if pass_criteria is not None:
        _is_check_exception_only = False
    else:
        _is_check_exception_only = True

    count = 0
    # main_retry_logic
    while count <= max_retries:
        try:
            result = f(*f_args, **f_kwargs)
            if not _is_check_exception_only and result != pass_criteria:
                raise RetryCallExeption(f"result=={f.__name__}(args=*list({f_args}), kwargs=**{f_kwargs}) != "
                                        f"pass_criteria=={pass_criteria}. ")
            return result

        except Exception as e:
            # logging_logger.warning(e)
            count += 1
            logging_logger.warning(
                f"{e} \n" 
                f"Starting retry no. {count} (out of max retries={max_retries}), "
                f"after delay for {delay_s} seconds.")
            gevent.sleep(delay_s)

