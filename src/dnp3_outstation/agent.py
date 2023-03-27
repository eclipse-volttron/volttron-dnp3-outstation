# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2022 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===

from pathlib import Path
from pprint import pformat
from typing import Callable, Dict

from volttron.client.messaging import (headers)
from volttron.utils import (format_timestamp, get_aware_utc_now, load_config,
                            setup_logging, vip_main)

import logging
import sys
import gevent

from dnp3_python.dnp3station.outstation_new import MyOutStationNew
from pydnp3 import opendnp3
from volttron.client.vip.agent import Agent, Core, RPC

setup_logging()
_log = logging.getLogger(__name__)
__version__ = "1.0"


class Dnp3OutstationAgent(Agent):
    """This is class is a subclass of the Volttron Agent;
        This agent is an implementation of a DNP3 outstation;
        The agent overrides @Core.receiver methods to modify agent life cycle behavior;
        The agent exposes @RPC.export as public interface utilizing RPC calls.
    """

    def __init__(self, config_path: str, **kwargs) -> None:
        super().__init__(enable_web=True, **kwargs)

        # default_config, mainly for developing and testing purposes.
        default_config: dict = {'outstation_ip': '0.0.0.0', 'port': 20000, 'master_id': 2, 'outstation_id': 1}
        # agent configuration using volttron config framework
        # self._dnp3_outstation_config = default_config
        config_from_path = self._parse_config(config_path)

        # TODO: improve this logic by refactoring out the MyOutstationNew init,
        #  and add config from "config store"
        try:
            _log.info("Using config_from_path {config_from_path}")
            self._dnp3_outstation_config = config_from_path
            self.outstation_application = MyOutStationNew(**self._dnp3_outstation_config)
        except Exception as e:
            _log.error(e)
            _log.info(f"Failed to use config_from_path {config_from_path}"
                      f"Using default_config {default_config}")
            self._dnp3_outstation_config = default_config
            self.outstation_application = MyOutStationNew(**self._dnp3_outstation_config)

        # SubSystem/ConfigStore
        self.vip.config.set_default("config", default_config)
        self.vip.config.subscribe(
            self._config_callback_dummy,  # TODO: cleanup: used to be _configure_ven_client
            actions=["NEW", "UPDATE"],
            pattern="config",
        )  # TODO: understand what vip.config.subscribe does

    @property
    def dnp3_outstation_config(self):
        return self._dnp3_outstation_config

    @dnp3_outstation_config.setter
    def dnp3_outstation_config(self, config: dict):
        # TODO: add validation
        self._dnp3_outstation_config = config

    def _config_callback_dummy(self, config_name: str, action: str,
                               contents: Dict) -> None:
        pass

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.
        Usually not needed if using the configuration store.
        """

        # for dnp3 outstation
        self.outstation_application.start()

        # Example publish to pubsub
        # self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")
        #
        # # Example RPC call
        # # self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        # pass
        # self._create_subscriptions(self.setting2)

    # ***************** Helper methods ********************
    def _parse_config(self, config_path: str) -> Dict:
        """Parses the agent's configuration file.

        :param config_path: The path to the configuration file
        :return: The configuration
        """
        # TODO: added capability to configuration based on tabular config file (e.g., csv)
        try:
            config = load_config(config_path)
        except NameError as err:
            _log.exception(err)
            raise err
        except Exception as err:
            _log.error("Error loading configuration: {}".format(err))
            config = {}
        # print(f"============= def _parse_config config {config}")
        if not config:
            raise Exception("Configuration cannot be empty.")
        return config

    @RPC.export
    def rpc_dummy(self) -> str:
        """
        For testing rpc call
        """
        return "This is a dummy rpc call"

    @RPC.export
    def reset_outstation(self):
        """update`self._dnp3_outstation_config`, then init a new outstation.
        For post-configuration and immediately take effect.
        Note: will start a new outstation instance and the old database data will lose"""
        # self.dnp3_outstation_config(**kwargs)
        # TODO: this method might be refactored as internal helper method for `update_outstation`
        try:
            self.outstation_application.shutdown()
            outstation_app_new = MyOutStationNew(**self.dnp3_outstation_config)
            self.outstation_application = outstation_app_new
            self.outstation_application.start()
            _log.info(f"Outstation has restarted")
        except Exception as e:
            _log.error(e)

    @RPC.export
    def display_outstation_db(self) -> dict:
        """expose db"""
        return self.outstation_application.db_handler.db

    @RPC.export
    def get_outstation_config(self) -> dict:
        """expose get_config"""
        return self.outstation_application.get_config()

    @RPC.export
    def is_outstation_connected(self) -> bool:
        """expose is_connected, note: status, property"""
        return self.outstation_application.is_connected

    @RPC.export
    def apply_update_analog_input(self, val: float, index: int) -> dict:
        """public interface to update analog-input point value
        val: float
        index: int, point index
        """
        if not isinstance(val, float):
            raise f"val of type(val) should be float"
        self.outstation_application.apply_update(opendnp3.Analog(value=val), index)
        _log.debug(f"Updated outstation analog-input index: {index}, val: {val}")

        return self.outstation_application.db_handler.db

    @RPC.export
    def apply_update_analog_output(self, val: float, index: int) -> dict:
        """public interface to update analog-output point value
        val: float
        index: int, point index
        """

        if not isinstance(val, float):
            raise f"val of type(val) should be float"
        self.outstation_application.apply_update(opendnp3.AnalogOutputStatus(value=val), index)
        _log.debug(f"Updated outstation analog-output index: {index}, val: {val}")

        return self.outstation_application.db_handler.db

    @RPC.export
    def apply_update_binary_input(self, val: bool, index: int):
        """public interface to update binary-input point value
        val: bool
        index: int, point index
        """
        if not isinstance(val, bool):
            raise f"val of type(val) should be bool"
        self.outstation_application.apply_update(opendnp3.Binary(value=val), index)
        _log.debug(f"Updated outstation binary-input index: {index}, val: {val}")

        return self.outstation_application.db_handler.db

    @RPC.export
    def apply_update_binary_output(self, val: bool, index: int):
        """public interface to update binary-output point value
        val: bool
        index: int, point index
        """
        if not isinstance(val, bool):
            raise f"val of type(val) should be bool"
        self.outstation_application.apply_update(opendnp3.BinaryOutputStatus(value=val), index)
        _log.debug(f"Updated outstation binary-output index: {index}, val: {val}")

        return self.outstation_application.db_handler.db

    @RPC.export
    def update_outstation(self,
                          outstation_ip: str = None,
                          port: int = None,
                          master_id: int = None,
                          outstation_id: int = None,
                          **kwargs):
        """
        Update dnp3 outstation config and restart the application to take effect. By default,
        {'outstation_ip': '0.0.0.0', 'port': 20000, 'master_id': 2, 'outstation_id': 1}
        """
        config = self._dnp3_outstation_config.copy()
        for kwarg in [{"outstation_ip": outstation_ip},
                      {"port": port},
                      {"master_id": master_id}, {"outstation_id": outstation_id}]:
            if list(kwarg.values())[0] is not None:
                config.update(kwarg)
        self._dnp3_outstation_config = config
        self.reset_outstation()


def main():
    """Main method called to start the agent."""
    vip_main(Dnp3OutstationAgent)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
