# volttron-dnp3-outstation

[//]: # (TODO: get the badges)

Distributed Network Protocol (DNP
or [DNP3](https://en.wikipedia.org/wiki/DNP3))
has achieved a large-scale acceptance since its introduction in 1993. This
protocol is an immediately deployable solution for monitoring remote sites because it was developed for communication of
critical infrastructure status, allowing for reliable remote control.

DNP3 is typically used between centrally located masters and distributed remotes.
Application layer fragments from Master DNP3 stations are typically requests for operations on data
objects, and application layer fragments from Slave DNP3 stations (i.e., Outstation) are typically responses to those
requests. A DNP3 Outstation may also transmit a message without a request (an unsolicited response).
The volttron-dnp3-outstation is an implementation of the DNP3 master following
the [VOLTTRON Agent Specifications](https://volttron.readthedocs.io/en/main/developing-volttron/developing-agents/specifications/index.html?highlight=agent#agent-specifications).

Note: to fully desmonstate the volttron-dnp3-outstation features, including polling data, setting point
values, etc., it is suggested to establish connection between an outstation and a DNP3 master instance.
The [dnp3-python](https://github.com/VOLTTRON/dnp3-python) can provide the essential master functionality,
and as
part of the volttron-dnp3-outstation dependency, it is immediately available after the volttron-dnp3-outstation is
installed.

# Prerequisites

* Python 3 (tested with Python3.8, Python3.9, Python3.10)

## Python

<details>
<summary>To install specific Python version (e.g., Python 3.8), we recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```shell
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.8
pyenv install 3.8.10

# make it available globally
pyenv global system 3.8.10
```

</details>

# Installation

The following recipe walks through the steps to install and configure a DNP3 agent. Note that it uses default setup to
work out-of-the-box. Please feel free to refer to related documentations for details.

1. Create and activate a virtual environment.

   It is recommended to use a virtual environment for installing volttron.

    ```shell
    python -m venv env
    source env/bin/activate
    
    pip install volttron
    ```

1. Install volttron and start the platform.

   > **Note**:
   > According to the [volttron-core#README](https://github.com/eclipse-volttron/volttron-core#readme), setup VOLTTRON_HOME
   > environment variable is mandatory:

   > ... if you have/had in the past, a monolithic VOLTTRON version that used the default VOLTTRON_HOME
   > $HOME/.volttron. This modular version of VOLTTRON cannot work with volttron_home used by monolithic version of
   > VOLTTRON(version 8.3 or earlier)

    ```shell
    # Setup environment variable `VOLTTRON_HOME`
    export VOLTTRON_HOME=<path-to-volttron_home-dir>
    
    # Start platform with output going to volttron.log
    volttron -vv -l volttron.log &
    ```

1. Install the "volttron-dnp3-outstation" dependency.

   There are two options to install the DNP3 Driver. You can install this library using the version on PyPi or install
   it from the source code (`git clone` might be required.)
   Note: the `vctl install` command in the following step can handle dependency installation using pypi. However, in
   this demo we
   demonstrate what is happening under the neath the hood by separating the dependency installation and agent registry
   steps.

    ```shell
    # option 1: install from pypi
    pip install volttron-dnp3-outstation
    
    # option 2: install from the source code (Note: `-e` option to use editable mode, useful for development.)
    pip install [-e] <path-to-the-source-code-root>/volttron-dnp3-outstation/
    ```

1. Install and start the "volttron-dnp3-outstation" agent.

   Prepare the default config files:

    ```shell
    # Create config file place holders
    mkdir config
    touch config/dnp3-outstation-config.json
    ```

   Edit the `dnp3-outstation-config.json` as follows:
    ```json
    {
     "outstation_ip": "0.0.0.0",
     "master_id": 2,
     "outstation_id": 1,
     "port":  21000
    }
    ```

   Use `vctl install` command to register to the volttron home path.
   Note: for demo purposes and reproducibility, we assign vip-identity as "dnp3_outstation", but you can choose
   any other valid agent identity as desired.

    ```shell
    vctl install volttron-dnp3-outstation --agent-config <path-to-agent-config> \
   --vip-identity dnp3_outstation \
   --start
    ```

   (Optional) Use `vctl stauts` to verify the installation
   ```shell
   (env) kefei@ubuntu-22:~/sandbox/dnp3-outstation-sandbox$ vctl status
   UUID   AGENT                             IDENTITY        TAG PRIORITY STATUS          HEALTH
   e      volttron-dnp3-outstation-0.0.1rc0 dnp3_outstation              running [3408]  GOOD
   ```

# Basic Usage Example

Like other VOLTTRON agent, the volttron-dnp3-outstation agent provides public interface and can be evoked by VOLTTRON
RPC calls. The volttron-dnp3-outstation provided a commandline interface `vdnp3_outstation` as an RPC method wrapper.
Please see [run_volttron_dnp3_outstation_cli.py](./src/vdnp3_outstation/run_volttron_dnp3_outstation_cli.py) for
implementation details of the RPC examples.

1. (Optional) Inspect the dnp3 outstation cli help menu.

   ```shell
   (env) kefei@ubuntu-22:~/sandbox/dnp3-driver-sandbox$ python -m vdnp3_outstation.run_volttron_dnp3_outstation_cli -h
   usage: dnp3-outstation [-h] [-aid <peer-name>]
   
   Run a dnp3 outstation agent. Specify agent identity, by default `dnp3_outstation`
   
   options:
     -h, --help            show this help message and exit
     -aid <peer-name>, --agent-identity <peer-name>
                           specify agent identity (parsed as peer-name for rpc call), default 'dnp3_outstation'.

   ```

1. Start the dnp3 outstation cli

   Start the volttron-dnp3-outstation cli with `vdnp3_outstation --agent-identity <agent-id>`. If you
   follow along this demo, the agent vip-identity should be "dnp3_outstation".

   ```shell
   (env) kefei@ubuntu-22:~/sandbox/dnp3-agent-sandbox$ python -m vdnp3_outstation.run_volttron_dnp3_outstation_cli --agent-identity dnp3_outstation
   2023-03-23 11:51:25,975 root DEBUG: Creating ZMQ Core None
   2023-03-23 11:51:25,975 volttron.client.vip.agent.core DEBUG: address: ipc://@/home/kefei/.volttron/run/vip.socket
   2023-03-23 11:51:25,975 volttron.client.vip.agent.core DEBUG: identity: 08953498-18e6-4070-9576-521bad3e82be
   2023-03-23 11:51:25,975 volttron.client.vip.agent.core DEBUG: agent_uuid: None
   2023-03-23 11:51:25,975 volttron.client.vip.agent.core DEBUG: serverkey: None
   2023-03-23 11:51:25,976 volttron.client.vip.agent.core DEBUG:  environ keys: dict_keys(['SHELL', 'SESSION_MANAGER', 'QT_ACCESSIBILITY', 'COLORTERM', 'XDG_CONFIG_DIRS', 'SSH_AGENT_LAUNCHER', 'XDG_MENU_PREFIX', 'GNOME_DESKTOP_SESSION_ID', 'CONDA_EXE', '_CE_M', 'GNOME_SHELL_SESSION_MODE', 'SSH_AUTH_SOCK', 'HOMEBREW_PREFIX', 'XMODIFIERS', 'DESKTOP_SESSION', 'GTK_MODULES', 'PWD', 'LOGNAME', 'XDG_SESSION_DESKTOP', 'XDG_SESSION_TYPE', 'MANPATH', 'SYSTEMD_EXEC_PID', 'XAUTHORITY', 'VOLTTRON_HOME', 'HOME', 'USERNAME', 'IM_CONFIG_PHASE', 'LANG', 'LS_COLORS', 'XDG_CURRENT_DESKTOP', 'VIRTUAL_ENV', 'VTE_VERSION', 'WAYLAND_DISPLAY', 'GNOME_TERMINAL_SCREEN', 'INFOPATH', 'GNOME_SETUP_DISPLAY', 'LESSCLOSE', 'XDG_SESSION_CLASS', 'TERM', '_CE_CONDA', 'LESSOPEN', 'USER', 'HOMEBREW_CELLAR', 'GNOME_TERMINAL_SERVICE', 'CONDA_SHLVL', 'DISPLAY', 'SHLVL', 'QT_IM_MODULE', 'HOMEBREW_REPOSITORY', 'VIRTUAL_ENV_PROMPT', 'CONDA_PYTHON_EXE', 'XDG_RUNTIME_DIR', 'PS1', 'XDG_DATA_DIRS', 'PATH', 'GDMSESSION', 'DBUS_SESSION_BUS_ADDRESS', '_', 'RABBITMQ_NOT_AVAILABLE'])
   2023-03-23 11:51:25,976 volttron.client.vip.agent.core DEBUG: server key from env None
   2023-03-23 11:51:25,976 volttron.client.vip.agent.core DEBUG: AGENT RUNNING on ZMQ Core 08953498-18e6-4070-9576-521bad3e82be
   2023-03-23 11:51:25,976 volttron.client.vip.agent.core DEBUG: keys: server: _M0Ds3SfjECMrmXulHQZtPIlsYW7JwzXMXJH1Koy2T4 public: _M0Ds3SfjECMrmXulHQZtPIlsYW7JwzXMXJH1Koy2T4, secret: yfjc9g5znWMEjTSX3kfINGwhCvaDI80fK8vN76-C7SQ
   2023-03-23 11:51:25,977 volttron.client.vip.zmq_connection DEBUG: ZMQ connection 08953498-18e6-4070-9576-521bad3e82be
   2023-03-23 11:51:25,977 volttron.client.vip.zmq_connection DEBUG: connecting to url ipc://@/home/kefei/.volttron/run/vip.socket?publickey=_M0Ds3SfjECMrmXulHQZtPIlsYW7JwzXMXJH1Koy2T4&secretkey=yfjc9g5znWMEjTSX3kfINGwhCvaDI80fK8vN76-C7SQ&serverkey=_M0Ds3SfjECMrmXulHQZtPIlsYW7JwzXMXJH1Koy2T4
   2023-03-23 11:51:25,977 volttron.client.vip.zmq_connection DEBUG: url type is <class 'str'>
   2023-03-23 11:51:25,981 volttron.client.vip.agent.core INFO: Connected to platform: identity: 08953498-18e6-4070-9576-521bad3e82be version: 1.0
   2023-03-23 11:51:25,981 volttron.client.vip.agent.core DEBUG: Running onstart methods.
    
   ========================= MENU ==================================
   <ai> - set analog-input point value
   <ao> - set analog-output point value
   <bi> - set binary-input point value
   <bo> - set binary-output point value
    
   <dd> - display database
   <di> - display (outstation) info
   <cr> - config then restart outstation
   =================================================================
    
   !!!!!!!!! WARNING: The outstation is NOT connected !!!!!!!!!
   {'outstation_ip_str': '0.0.0.0', 'port': 20000, 'masterstation_id_int': 2, 'outstation_id_int': 1, 'peer': 'dnp3_outstation'}
    
   ======== Your Input Here: ==(DNP3 OutStation Agent)======
 
   ```

1. Start a dnp3 master to establish connection.

   If there is no connection between an outstation and a master, you may see the
   warning `!!!!!!!!! WARNING: The outstation is NOT connected !!!!!!!!!`. To establish such a connection, **open
   another terminal**, and
   run `dnp3demo master`. (More details about the "dnp3demo" module, please
   see [dnp3demo-Module.md](https://github.com/VOLTTRON/dnp3-python/blob/main/docs/dnp3demo-Module.md))

   ```shell
    ===== Master Operation MENU ==================================
    <ao> - set analog-output point value (for remote control)
    <bo> - set binary-output point value (for remote control)
    <dd> - display/polling (outstation) database
    <dc> - display configuration
    =================================================================

    
    ======== Your Input Here: ==(master)======
    ```

   Note: by default, both the volttron-dnp3-outstation and the dnp3demo master uses configurations to
   assure valid connection out-of-the-box. e.g., port=20000. Feel free to configure the connection parameters as
   desired.

1. Basic volttron-dnp3-outstation operations
     ```
   ======== Your Input Here: ==(DNP3 OutStation Agent)======
   ai
   You chose <ai> - set analog-input point value
   Type in <float> and <index>. Separate with space, then hit ENTER. e.g., `1.4321, 1`.
   Type 'q', 'quit', 'exit' to main menu.

    ======== Your Input Here: ==(DNP3 OutStation Agent)======
    0.1212 0
    {'Analog': {0: 0.1212, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}}
    You chose <ai> - update analog-input point value (for local reading)
    Type in <float> and <index>. Separate with space, then hit ENTER.
    Type 'q', 'quit', 'exit' to main menu.
     
     
    ======== Your Input Here: ==(DNP3 OutStation Agent)======
    1.2323 1
    {'Analog': {0: 0.1212, 1: 1.2323, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}}
    You chose <ai> - update analog-input point value (for local reading)
    Type in <float> and <index>. Separate with space, then hit ENTER.
    Type 'q', 'quit', 'exit' to main menu.
   ```
     <details>
     <summary>Example of interaction with the `vdnp3_outstation` module </summary>

     ```shell
     (env) kefei@ubuntu-22:~/sandbox/dnp3-agent-sandbox$ python -m vdnp3_outstation.run_volttron_dnp3_outstation_cli --agent-identity dnp3_outstation
     dnp3demo.run_outstation {'command': 'outstation', 'outstation_ip=': '0.0.0.0', 'port=': 20000, 'master_id=': 2, 'outstation_id=': 1}
     ms(1678770551216) INFO    manager - Starting thread (0)
     2023-03-14 00:09:11,216	control_workflow_demo	INFO	Connection Config
     2023-03-14 00:09:11,216	control_workflow_demo	INFO	Connection Config
     2023-03-14 00:09:11,216	control_workflow_demo	INFO	Connection Config
     ms(1678770551216) INFO    server - Listening on: 0.0.0.0:20000
     2023-03-14 00:09:11,216	control_workflow_demo	DEBUG	Initialization complete. Outstation in command loop.
     2023-03-14 00:09:11,216	control_workflow_demo	DEBUG	Initialization complete. Outstation in command loop.
     2023-03-14 00:09:11,216	control_workflow_demo	DEBUG	Initialization complete. Outstation in command loop.
     Connection error.
     Connection Config {'outstation_ip_str': '0.0.0.0', 'port': 20000, 'masterstation_id_int': 2, 'outstation_id_int': 1}
     Start retry...
     Connection error.
     Connection Config {'outstation_ip_str': '0.0.0.0', 'port': 20000, 'masterstation_id_int': 2, 'outstation_id_int': 1}
     ms(1678770565247) INFO    server - Accepted connection from: 127.0.0.1
     ==== Outstation Operation MENU ==================================
     <ai> - update analog-input point value (for local reading)
     <ao> - update analog-output point value (for local control)
     <bi> - update binary-input point value (for local reading)
     <bo> - update binary-output point value (for local control)
     <dd> - display database
     <dc> - display configuration
     =================================================================
      
      
     ======== Your Input Here: ==(DNP3 OutStation Agent)======
     ai
     You chose <ai> - update analog-input point value (for local reading)
     Type in <float> and <index>. Separate with space, then hit ENTER.
     Type 'q', 'quit', 'exit' to main menu.
      
      
     ======== Your Input Here: ==(DNP3 OutStation Agent)======
     0.1212 0
     {'Analog': {0: 0.1212, 1: None, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}}
     You chose <ai> - update analog-input point value (for local reading)
     Type in <float> and <index>. Separate with space, then hit ENTER.
     Type 'q', 'quit', 'exit' to main menu.
      
      
     ======== Your Input Here: ==(DNP3 OutStation Agent)======
     1.2323 1
     {'Analog': {0: 0.1212, 1: 1.2323, 2: None, 3: None, 4: None, 5: None, 6: None, 7: None, 8: None, 9: None}}
     You chose <ai> - update analog-input point value (for local reading)
     Type in <float> and <index>. Separate with space, then hit ENTER.
     Type 'q', 'quit', 'exit' to main menu.
      
      
     ======== Your Input Here: ==(DNP3 OutStation Agent)======
     ```
     </details>

# Development

Please see the following for contributing
guidelines [contributing](https://github.com/eclipse-volttron/volttron-core/blob/develop/CONTRIBUTING.md).

Please see the following helpful guide
about [developing modular VOLTTRON agents](https://github.com/eclipse-volttron/volttron-core/blob/develop/DEVELOPING_ON_MODULAR.md)

# Disclaimer Notice

This material was prepared as an account of work sponsored by an agency of the
United States Government. Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or any
information, apparatus, product, software, or process disclosed, or represents
that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
