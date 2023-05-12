.. _DNP3-Agent:

==========
DNP3 Outstation Agent
==========

`DNP3 <https://en.wikipedia.org/wiki/DNP3>`_ (Distributed Network Protocol) is a set of communications protocols that
are widely used by utilities such as electric power companies, primarily for
`SCADA <https://en.wikipedia.org/wiki/SCADA>`_ purposes.  It was adopted in 2010 as
`IEEE Std 1815-2010 <http://ieeexplore.ieee.org/document/5518537/?reload=true>`_,
later updated to `1815-2012 <https://standards.ieee.org/findstds/standard/1815-2012.html>`_.

VOLTTRON's DNP3 Agent is an implementation of a DNP3 Outstation as specified in IEEE Std 1815-2012.  It engages in
bidirectional network communications with a DNP3 Master, which might be located at a power utility.

Like some other VOLTTRON protocol agents (e.g. IEEE2030_5Agent), the DNP3 Agent can optionally be front-ended by a DNP3
device driver running under VOLTTRON's PlatformDriverAgent.  This allows a DNP3 Master to be treated like any other device
in VOLTTRON's ecosystem.

The VOLTTRON DNP3 Agent implementation of an Outstation is built on PyDNP3, an open-source library from Kisensum
containing Python language bindings for Automatak's C++ `opendnp3 <https://www.automatak.com/opendnp3/>`_ library, the
de facto reference implementation of DNP3.

The DNP3 Agent exposes DNP3 application-layer functionality, creating an extensible base from which specific custom
behavior can be designed and supported.  By default, the DNP3 Agent acts as a simple transfer agent, publishing data
received from the Master on the VOLTTRON Message Bus, and responding to RPCs from other VOLTTRON agents by sending data
to the Master.


Requirements
============

dnp3-python can be installed in an activated environment with:

.. code-block:: bash

    pip install volttron-dnp3-outstation


RPC Calls
---------

The DNP3 Agent exposes the following VOLTTRON RPC calls:

.. code-block:: python

    def reset_outstation(self):
        """update`self._dnp3_outstation_config`, then init a new outstation.
        For post-configuration and immediately take effect.
        Note: will start a new outstation instance and the old database data will lose"""

    def display_outstation_db(self) -> dict:
        """expose db"""

    def get_outstation_config(self) -> dict:
        """expose get_config"""

    def is_outstation_connected(self) -> bool:
        """expose is_connected, note: status, property"""

    def apply_update_analog_input(self, val: float, index: int) -> dict:
        """public interface to update analog-input point value
        val: float
        index: int, point index
        """

    def apply_update_analog_output(self, val: float, index: int) -> dict:
        """public interface to update analog-output point value
        val: float
        index: int, point index
        """

    def apply_update_binary_input(self, val: bool, index: int):
        """public interface to update binary-input point value
        val: bool
        index: int, point index
        """

    def apply_update_binary_output(self, val: bool, index: int):
        """public interface to update binary-output point value
        val: bool
        index: int, point index
        """

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



Data Dictionary of Point Definitions
------------------------------------

The DNP3 Agent loads and uses a data dictionary of point definitions, which are maintained by agreement between the
(DNP3 Agent) Outstation and the DNP3 Master.  The data dictionary is stored in the agent's registry.


Current Point Values
--------------------

The DNP3 Agent tracks the most-recently-received value for each point definition in its data dictionary, regardless of
whether the point value's source is a VOLTTRON RPC call or a message from the DNP3 Master.


Agent Configuration
-------------------

The DNP3Agent configuration file specifies the following fields:

- **outstation_ip**: (string) outstation IP address. Default: "0.0.0.0".
- **master_id**: (integer) master ID.  Default: 2.
- **outstation_id**: (integer) outstation ID.  Default: 1.
- **port**: (integer) port number.  Default: 21000.
- **link_remote_addr**: (integer) Link layer remote address.  Default: 1.

A sample DNP3 Agent configuration file is as follows:

.. code-block:: json

    {
     "outstation_ip": "0.0.0.0",
     "master_id": 2,
     "outstation_id": 1,
     "port":  21000
    }

