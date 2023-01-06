from netmiko import ConnectHandler

netmikoList = ["a10", "accedian", "adtran_os", "alcatel_aos", "alcatel_sros", "allied_telesis_awplus", "apresia_aeos", "arista_eos", "aruba_os", "aruba_osswitch", "aruba_procurve", "avaya_ers", "avaya_vsp", "broadcom_icos", "brocade_fastiron", "brocade_fos", "brocade_netiron", "brocade_nos", "brocade_vdx", "brocade_vyos", "calix_b6", "cdot_cros", "centec_os", "checkpoint_gaia", "ciena_saos", "cisco_asa", "cisco_ftd", "cisco_ios", "cisco_nxos", "cisco_s300", "cisco_tp", "cisco_viptela", "cisco_wlc", "cisco_xe", "cisco_xr", "cloudgenix_ion", "coriant", "dell_dnos9", "dell_force10", "dell_isilon", "dell_os10", "dell_os6", "dell_os9", "dell_powerconnect", "dell_sonic", "dlink_ds", "eltex", "eltex_esr", "endace", "enterasys", "ericsson_ipos", "extreme", "extreme_ers", "extreme_exos", "extreme_netiron", "extreme_nos", "extreme_slx", "extreme_tierra", "extreme_vdx", "extreme_vsp", "extreme_wing", "f5_linux", "f5_ltm", "f5_tmsh", "flexvnf", "fortinet", "generic", "generic_termserver", "hp_comware", "hp_procurve", "huawei", "huawei_olt", "huawei_smartax", "huawei_vrpv8", "ipinfusion_ocnos", "juniper", "juniper_junos", "juniper_screenos", "keymile", "keymile_nos", "linux", "mellanox", "mellanox_mlnxos", "mikrotik_routeros", "mikrotik_switchos", "mrv_lx", "mrv_optiswitch", "netapp_cdot", "netgear_prosafe", "netscaler", "nokia_sros", "nokia_srl", "oneaccess_oneos", "ovs_linux", "paloalto_panos", "pluribus", "quanta_mesh", "rad_etx", "raisecom_roap", "ruckus_fastiron", "ruijie_os", "sixwind_os", "sophos_sfos", "supermicro_smis", "tplink_jetstream", "ubiquiti_edge", "ubiquiti_edgerouter", "ubiquiti_edgeswitch", "ubiquiti_unifiswitch", "vyatta_vyos", "vyos", "watchguard_fireware", "yamaha", "zte_zxros", "zyxel_os"]

with open('IPADDRESSES.txt') as file:
    lines = file.readlines()
    ipaddresses = [line.rstrip() for line in lines]

with open('COMMANDS.txt') as file:
    lines = file.readlines()
    config_commands = [line.rstrip() for line in lines]

print("Enter a Device type of type help to receive the device types")
while True:
    choice = input("Enter Device Type or 'Help': ")

    if choice.lower() == 'help':
        print("Enter a Device Type Listed bellow")
        for i in netmikoList:
            print(i)

    elif choice in netmikoList:
        netmikoChoice = choice
        break

    else:
        print("Enter a real device type or 'help!'")

UN = input("Please enter username for devices: ")
PW = input("Please enter password for devices: ")

for ip in ipaddresses:
    print('\n')
    print(ip)

    SSHDevice = {
        'device_type': netmikoChoice,
        'host': ip,
        'username': UN,
        'password': PW,
        'port': 22,
    }

    try:
        net_connect = ConnectHandler(**SSHDevice)
    except Exception as e:
        with open('IP.txt', 'a') as f:
            f.write(ip + "\tTCP connection to device failed\n" + str(e))
        continue

    commandOut = net_connect.send_config_set(config_commands)
    print(commandOut)

    output = net_connect.commit()
    print(output)
    with open('IP.txt', 'a') as f:
        f.write(ip + "\tCommands added\n")


    #output = net_connect.send_command('show ip int brief')
    #print(output)