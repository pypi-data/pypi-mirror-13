#!/usr/bin/env python
# coding=utf-8
import time, snimpy, sys
from walt.server import snmp, status, network
from walt.server.network.tools import lldp_update
from waltvlanconf import configure_main_switch_if_needed
from walt.common.tools import do
from walt.server.mydocker import DockerClient
from walt.server.const import WALT_INTF, SETUP_INTF

MSG_WAITING_COMPANION_SERVICES = 'Waiting for companion services to be ready...'
MSG_DETECTING_MAIN_SWITCH = 'Detecting the main switch...'
MSG_AUTO_CONFIGURING_MAIN_SWITCH = 'Auto-configuring the main switch...'
MSG_ERROR_RESET_THE_SWITCH_REBOOT = '''\
Could not communicate with the main switch. Try to reset it to factory settings.
The server will reboot and retry this bootup procedure in a few seconds.
'''
MSG_DHCP_REQUEST = "Requesting an IP for this WalT server..."
MSG_CHECK_DOCKER = "Checking internet connection to the Docker Hub..."

EXPLAIN_NETWORK = u'''\
The following network setup is required:

┌───────────────┐
│main switch    │   port 1: Externally managed VLAN with DHCP and internet access
│1 2 3 4 5 6 7 8│   port 2: (this) walt server
└┼─┼─┼─┼─┼─┼─┼─┼┘   ports 3 and more: managed walt network (walt nodes, cascaded switches)
 │ │
 │ └ walt server
 └ to internet
'''

TODO_DETECTING_MAIN_SWITCH = u'''
If this is not the case already, please connect the main switch as described in order to continue.
Note that it may take a few minutes to detect the main switch even if it is connected.
'''

TODO_DHCP_REQUEST = u'''
The server (mac address %(mac)s) is now sending DHCP requests on the externally managed VLAN (switch port 1).
The setup process will continue when a DHCP offer is obtained.
'''

TODO_CHECK_DOCKER = u'''
The server failed to access hub.docker.com. Please verify that the server is allowed to reach internet.
The setup process will retry this periodically until it succeeds.
'''

def main_switch_conf_callback(local_ip, switch_ip, intf, ui):
    ui.task_running()
    if intf == WALT_INTF:
        # we could communicate with the switch and it is already
        # tagging packets of VLAN1 (since we communicated on eth0.1).
        # This implies it is already configured.
        return True
    else:
        configured = configure_main_switch_if_needed(
                            snmp.Proxy(str(switch_ip), vlan=True))
        return configured

def setup_needed(ui):
    # check if an ip was already assigned, which 
    # shows that setup was already done
    ui.task_start(MSG_WAITING_COMPANION_SERVICES)
    server_ip = str(network.tools.get_server_ip())
    res = None
    while True:
        try:
            snmp_local = snmp.Proxy('localhost', lldp=True)
            if server_ip in snmp_local.lldp.get_local_ips():
                res = False    # setup already done
            else:
                res = True     # setup needed
        except snimpy.snmp.SNMPNoSuchObject:
            ui.task_running()
            time.sleep(1)
        else:
            break
    ui.task_done()
    return res

def check_docker(ui):
    ui.task_start(  MSG_CHECK_DOCKER,
                    explain=EXPLAIN_NETWORK,
                    todo=TODO_CHECK_DOCKER)
    docker = DockerClient()
    while not docker.self_test():
        ui.task_running()
        time.sleep(1)
    ui.task_done()

def setup(ui):
    ui.task_start(  MSG_DETECTING_MAIN_SWITCH,
                    explain=EXPLAIN_NETWORK,
                    todo=TODO_DETECTING_MAIN_SWITCH)
    # retrieve info about the main switch by
    # using the local lldp & snmp daemons
    snmp_local = snmp.Proxy('localhost', lldp=True)
    while len(snmp_local.lldp.get_neighbors()) == 0:
        ui.task_running()
        lldp_update()
        time.sleep(1)
    ui.task_done()
    main_switch_info = snmp_local.lldp.get_neighbors().values()[0]
    print 'main switch:', main_switch_info
    switch_ip = network.tools.ip(main_switch_info['ip'])
    # if the switch ip is in walt network, this implies
    # it was configured already
    if not network.tools.is_walt_address(switch_ip):
        ui.task_start(MSG_AUTO_CONFIGURING_MAIN_SWITCH)
        do('ip link set %s up' % WALT_INTF);
        reached = False
        for intf in [ WALT_INTF, SETUP_INTF ]:
            # assign a temporary ip in order to communicate
            # with the main switch, and, if not done yet, set up
            # its vlan configuration
            ui.task_running()
            reached, configured = network.tools.assign_temp_ip_to_reach_neighbor(
                                        switch_ip,
                                        main_switch_conf_callback,
                                        intf,
                                        ui)
            if reached:
                ui.task_done()
                break
        if not reached:
            ui.task_failed(MSG_ERROR_RESET_THE_SWITCH_REBOOT)
            time.sleep(10)
            do('reboot')
            time.sleep(10)
            sys.exit()
    # set up the server static ip on eth0.1 (walt testbed network)
    network.tools.set_server_ip()
    # get a server ip on eth0.169 (external VLAN) using DHCP
    mac_addr = network.tools.get_mac_address(EXTERN_INTF)
    msg = MSG_DHCP_REQUEST
    explain = EXPLAIN_NETWORK
    todo = TODO_DHCP_REQUEST % dict(mac = mac_addr)
    network.tools.dhcp_wait_ip(EXTERN_INTF, ui, msg, explain, todo)
    # check connection to the docker hub
    check_docker(ui)
    return True     # ok

