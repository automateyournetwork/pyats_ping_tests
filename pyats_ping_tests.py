import json
import logging
from pyats import aetest
from pyats.log.utils import banner
from tabulate import tabulate

# ----------------
# Get logger for script
# ----------------

log = logging.getLogger(__name__)

# ----------------
# AE Test Setup
# ----------------
class common_setup(aetest.CommonSetup):
    """Common Setup section"""
# ----------------
# Connected to devices
# ----------------
    @aetest.subsection
    def connect_to_devices(self, testbed):
        """Connect to all the devices"""
        testbed.connect(log_stdout=False)
# ----------------
# Mark the loop for Input Discards
# ----------------
    @aetest.subsection
    def loop_mark(self, testbed):
        aetest.loop.mark(PING_Public_IPs, device_name=testbed.devices)
        aetest.loop.mark(PING_Linux_Hosts, device_name=testbed.devices)
        aetest.loop.mark(PING_CDP_Neighbors, device_name=testbed.devices)

# ----------------
# Test Case #1 - PING public IP addresses
# ----------------
class PING_Public_IPs(aetest.Testcase):
    """Try to PING CDP Neighbors from the Interface they are discovered on"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
    
    @aetest.test
    def ping_1_1_1_1(self):
        number_of_pings = 5
        self.ping_1_1_1_1_results = {}
        self.ping_1_1_1_1_results[self.device.alias] = {}
        if self.device.os == "iosxe":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if "172.16.252" in value['ip_address']:
                    parsed_ping = self.device.parse(f"ping 1.1.1.1 source { interface } repeat { number_of_pings }")
                    self.ping_1_1_1_1_results[self.device.alias][interface] = parsed_ping
        elif self.device.os == "nxos":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if 'Vlan' in interface:
                    for key,sub_value in value.items():
                        for next_key,deep_value in sub_value.items():
                            if "172.16." in deep_value['ip_address']:
                                parsed_ping = self.device.parse(f"ping 1.1.1.1 source { interface } count 5")
                                self.ping_1_1_1_1_results[self.device.alias][interface] = parsed_ping
                else: 
                    if "172.16." in value['ip_address']:
                        parsed_ping = self.device.parse(f"ping 1.1.1.1 source { interface } count 5")
                        self.ping_1_1_1_1_results[self.device.alias][interface] = parsed_ping

    @aetest.test
    def ping_8_8_8_8(self):
        number_of_pings = 5
        self.ping_8_8_8_8_results = {}
        self.ping_8_8_8_8_results[self.device.alias] = {}
        if self.device.os == "iosxe":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if "172.16.252" in value['ip_address']:
                    parsed_ping = self.device.parse(f"ping 8.8.8.8 source { interface } repeat { number_of_pings }")
                    self.ping_8_8_8_8_results[self.device.alias][interface] = parsed_ping
        elif self.device.os == "nxos":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if 'Vlan' in interface:
                    for key,sub_value in value.items():
                        for next_key,deep_value in sub_value.items():
                            if "172.16." in deep_value['ip_address']:
                                parsed_ping = self.device.parse(f"ping 8.8.8.8 source { interface } count 5")
                                self.ping_8_8_8_8_results[self.device.alias][interface] = parsed_ping
                else: 
                    if "172.16." in value['ip_address']:
                        parsed_ping = self.device.parse(f"ping 8.8.8.8 source { interface } count 5")
                        self.ping_8_8_8_8_results[self.device.alias][interface] = parsed_ping

    @aetest.test
    def create_files(self):
        # Create .JSON file
        with open(f'JSON/{self.device.alias}_PING_1_1_1_1_Test.json', 'w') as f:
            f.write(json.dumps(self.ping_1_1_1_1_results, indent=4, sort_keys=True))

        with open(f'JSON/{self.device.alias}_PING_8_8_8_8_Test.json', 'w') as f:
            f.write(json.dumps(self.ping_8_8_8_8_results, indent=4, sort_keys=True))

    @aetest.test
    def test_1_1_1_1_success_rate_percentage(self):
        # Test for ping success rate
        self.failed_1_1_1_1_success_rate={}
        self.no_ping_response_1_1_1_1 = False
        table_data = []
        for interface,value in self.ping_1_1_1_1_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['success_rate_percent'] == 0:
                self.no_ping_response_1_1_1_1 = True            
            if value['ping']['statistics']['success_rate_percent'] == 100.0:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])                
                table_row.append('Failed')
                self.failed_1_1_1_1_success_rate = "Failed"
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface', 'Success Rate Percentage', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_1_1_1_1_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had Less Than 100% PING against 172.16.101.11')
        else:
            self.passed(f'All Interfaces on { self.device } Had 100% PING against 172.16.101.11')

    @aetest.test
    def test_8_8_8_8_success_rate_percentage(self):
        # Test for ping success rate
        self.failed_8_8_8_8_success_rate={}
        self.no_ping_response_8_8_8_8 = False
        table_data = []
        for interface,value in self.ping_8_8_8_8_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['success_rate_percent'] == 0:
                self.no_ping_response_8_8_8_8 = True
            if value['ping']['statistics']['success_rate_percent'] == 100.0:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])                
                table_row.append('Failed')
                self.failed_8_8_8_8_success_rate = "Failed"
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface', 'Success Rate Percentage', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_8_8_8_8_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had Less than 100% PING against 172.16.102.11')
        else:
            self.passed(f'All Interfaces on { self.device } Had 100% PING Success against 172.16.102.11')

    @aetest.test
    def test_1_1_1_1_min_ms(self):
        # Test for ping minimum ms
        self.failed_min_ms={}
        if self.no_ping_response_1_1_1_1:
            log.info("PING Failed - No Minumum MS to Measure")
        else:
            ping_min_ms_threshold = 5
            table_data = []
            for interface,value in self.ping_1_1_1_1_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['min_ms'] <= ping_min_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])                
                    table_row.append('Failed')
                    self.failed_min_ms = value['ping']['statistics']['round_trip']['min_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Minimum MS Threshold', 'Actual Minimum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_min_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.101.11 above the minimum millisecond threshold')
        elif self.no_ping_response_1_1_1_1:
            self.failed("There were no responses to PING - Unable to test minimum millisecond threshold")
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.101.11 within the minimum millisecond threshold')

    @aetest.test
    def test_8_8_8_8_min_ms(self):
        # Test for ping minimum ms
        self.failed_min_ms={}
        if self.no_ping_response_8_8_8_8:
            log.info("PING Failed - No Minumum MS to Measure")
        else:        
            ping_min_ms_threshold = 5
            table_data = []
            for interface,value in self.ping_8_8_8_8_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['min_ms'] <= ping_min_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])                
                    table_row.append('Failed')
                    self.failed_min_ms = value['ping']['statistics']['round_trip']['min_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Minimum MS Threshold', 'Actual Minimum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_min_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.102.11 above the minimum millisecond threshold')
        elif self.no_ping_response_8_8_8_8:
            self.failed("There were no responses to PING - Unable to test minimum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.102.11 within the minimum millisecond threshold')

    @aetest.test
    def test_1_1_1_1_max_ms(self):
        # Test for ping minimum ms
        self.failed_max_ms={}
        if self.no_ping_response_1_1_1_1:
            log.info("PING Failed - No Maximum MS to Measure")
        else:        
            ping_max_ms_threshold = 10
            self.failed_max_ms={}
            table_data = []
            for interface,value in self.ping_1_1_1_1_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['max_ms'] <= ping_max_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])                
                    table_row.append('Failed')
                    self.failed_max_ms = value['ping']['statistics']['round_trip']['max_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Maximum MS Threshold', 'Actual Maximum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_max_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.101.11 above the maximum millisecond threshold')
        elif self.no_ping_response_1_1_1_1:
            self.failed("There were no responses to PING - Unable to test maximum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.101.11 within the maximum millisecond threshold')

    @aetest.test
    def test_8_8_8_8_max_ms(self):
        # Test for ping minimum ms
        self.failed_max_ms={}
        if self.no_ping_response_8_8_8_8:
            log.info("PING Failed - No Maximum MS to Measure")
        else:        
            ping_max_ms_threshold = 10
            self.failed_max_ms={}
            table_data = []
            for interface,value in self.ping_8_8_8_8_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['max_ms'] <= ping_max_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])                
                    table_row.append('Failed')
                    self.failed_max_ms = value['ping']['statistics']['round_trip']['max_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Maximum MS Threshold', 'Actual Maximum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_max_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.102.11 above the maximum millisecond threshold')
        elif self.no_ping_response_8_8_8_8:
            self.failed("There were no responses to PING - Unable to test maximum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.102.11 within the maximum millisecond threshold')

    @aetest.test
    def test_1_1_1_1_avg_ms(self):
        # Test for ping minimum ms
        self.failed_avg_ms={}
        if self.no_ping_response_1_1_1_1:
            log.info("PING Failed - No Average MS to Measure")
        else:        
            ping_avg_ms_threshold = 7
            self.failed_avg_ms={}
            table_data = []
            for interface,value in self.ping_1_1_1_1_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['avg_ms'] <= ping_avg_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])                
                    table_row.append('Failed')
                    self.failed_avg_ms = value['ping']['statistics']['round_trip']['avg_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Average MS Threshold', 'Actual Average MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_avg_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.101.11 above the average millisecond threshold')
        elif self.no_ping_response_1_1_1_1:
            self.failed("There were no responses to PING - Unable to test maximum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.101.11 within the average millisecond threshold')

    @aetest.test
    def test_8_8_8_8_avg_ms(self):
        # Test for ping minimum ms
        self.failed_avg_ms={}
        if self.no_ping_response_8_8_8_8:
            log.info("PING Failed - No Average MS to Measure")
        else:        
            ping_avg_ms_threshold = 7
            table_data = []
            for interface,value in self.ping_8_8_8_8_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['avg_ms'] <= ping_avg_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])                
                    table_row.append('Failed')
                    self.failed_avg_ms = value['ping']['statistics']['round_trip']['avg_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Average MS Threshold', 'Actual Average MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_avg_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.102.11 above the average millisecond threshold')
        elif self.no_ping_response_8_8_8_8:
            self.failed("There were no responses to PING - Unable to test average millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.102.11 within the average millisecond threshold')

# ----------------
# Test Case #2 - PING the 2 Linux Hosts
# ----------------
class PING_Linux_Hosts(aetest.Testcase):
    """Try to PING Linux Hosts with static IPs"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing
    
    @aetest.test
    def ping_172_16_101_11(self):
        number_of_pings = 5
        self.ping_172_16_101_11_results = {}
        self.ping_172_16_101_11_results[self.device.alias] = {}
        if self.device.os == "iosxe":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if "172.16.252" in value['ip_address']:
                    parsed_ping = self.device.parse(f"ping 172.16.101.11 source { interface } repeat { number_of_pings }")
                    self.ping_172_16_101_11_results[self.device.alias][interface] = parsed_ping
        elif self.device.os == "nxos":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if 'Vlan' in interface:
                    for key,sub_value in value.items():
                        for next_key,deep_value in sub_value.items():
                            if "172.16." in deep_value['ip_address']:
                                parsed_ping = self.device.parse(f"ping 172.16.101.11 source { interface } count 5")
                                self.ping_172_16_101_11_results[self.device.alias][interface] = parsed_ping
                else: 
                    if "172.16." in value['ip_address']:
                        parsed_ping = self.device.parse(f"ping 172.16.101.11 source { interface } count 5")
                        self.ping_172_16_101_11_results[self.device.alias][interface] = parsed_ping

    @aetest.test
    def ping_172_16_102_11(self):
        number_of_pings = 5
        self.ping_172_16_102_11_results = {}
        self.ping_172_16_102_11_results[self.device.alias] = {}
        if self.device.os == "iosxe":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if "172.16.252" in value['ip_address']:
                    parsed_ping = self.device.parse(f"ping 172.16.101.11 source { interface } repeat { number_of_pings }")
                    self.ping_172_16_102_11_results[self.device.alias][interface] = parsed_ping
        elif self.device.os == "nxos":
            interface_list = self.device.parse("show ip interface brief")
            for interface,value in interface_list['interface'].items():
                if 'Vlan' in interface:
                    for key,sub_value in value.items():
                        for next_key,deep_value in sub_value.items():
                            if "172.16." in deep_value['ip_address']:
                                parsed_ping = self.device.parse(f"ping 172.16.101.11 source { interface } count 5")
                                self.ping_172_16_102_11_results[self.device.alias][interface] = parsed_ping
                else: 
                    if "172.16." in value['ip_address']:
                        parsed_ping = self.device.parse(f"ping 172.16.101.11 source { interface } count 5")
                        self.ping_172_16_102_11_results[self.device.alias][interface] = parsed_ping

    @aetest.test
    def create_files(self):
        # Create .JSON file
        with open(f'JSON/{self.device.alias}_PING_172_16_101_11_Test.json', 'w') as f:
            f.write(json.dumps(self.ping_172_16_101_11_results, indent=4, sort_keys=True))

        with open(f'JSON/{self.device.alias}_PING_172_16_102_11_Test.json', 'w') as f:
            f.write(json.dumps(self.ping_172_16_102_11_results, indent=4, sort_keys=True))

    @aetest.test
    def test_172_16_101_11_success_rate_percentage(self):
        # Test for ping success rate
        self.failed_172_16_101_11_success_rate={}
        self.no_ping_response_172_16_101_11 = False
        table_data = []
        for interface,value in self.ping_172_16_101_11_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['success_rate_percent'] == 0:
                self.no_ping_response_172_16_101_11 = True            
            if value['ping']['statistics']['success_rate_percent'] == 100.0:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])                
                table_row.append('Failed')
                self.failed_172_16_101_11_success_rate = value['ping']['statistics']['success_rate_percent']
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface', 'Success Rate Percentage', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_172_16_101_11_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had Less Than 100% PING against 172.16.101.11')
        else:
            self.passed(f'All Interfaces on { self.device } Had 100% PING against 172.16.101.11')

    @aetest.test
    def test_172_16_102_11_success_rate_percentage(self):
        # Test for ping success rate
        self.failed_172_16_102_11_success_rate={}
        self.no_ping_response_172_16_102_11 = False    
        table_data = []
        for interface,value in self.ping_172_16_102_11_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['success_rate_percent'] == 0:
                self.no_ping_response_172_16_102_11 = True
            if value['ping']['statistics']['success_rate_percent'] == 100.0:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['statistics']['success_rate_percent'])                
                table_row.append('Failed')
                self.failed_172_16_102_11_success_rate = value['ping']['statistics']['success_rate_percent']
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Interface', 'Success Rate Percentage', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_172_16_102_11_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had Less than 100% PING against 172.16.102.11')
        else:
            self.passed(f'All Interfaces on { self.device } Had 100% PING Success against 172.16.102.11')

    @aetest.test
    def test_172_16_101_11_min_ms(self):
        # Test for ping minimum ms
        self.failed_min_ms={}
        if self.no_ping_response_172_16_102_11:
            log.info("PING Failed - No Minumum MS to Measure")
        else:        
            ping_min_ms_threshold = 5
            table_data = []
            for interface,value in self.ping_172_16_101_11_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['min_ms'] <= ping_min_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])                
                    table_row.append('Failed')
                    self.failed_min_ms = value['ping']['statistics']['round_trip']['min_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Minimum MS Threshold', 'Actual Minimum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_min_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.101.11 above the minimum millisecond threshold')
        elif self.no_ping_response_172_16_101_11:
            self.failed("There were no responses to PING - Unable to test minimum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.101.11 within the minimum millisecond threshold')

    @aetest.test
    def test_172_16_102_11_min_ms(self):
        # Test for ping minimum ms
        self.failed_min_ms={}
        if self.no_ping_response_172_16_102_11:
            log.info("PING Failed - No Minumum MS to Measure")
        else:        
            ping_min_ms_threshold = 5
            table_data = []
            for interface,value in self.ping_172_16_102_11_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['min_ms'] <= ping_min_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_min_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['min_ms'])                
                    table_row.append('Failed')
                    self.failed_min_ms = value['ping']['statistics']['round_trip']['min_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Minimum MS Threshold', 'Actual Minimum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_min_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.102.11 above the minimum millisecond threshold')
        elif self.no_ping_response_172_16_102_11:
            self.failed("There were no responses to PING - Unable to test minimum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.102.11 within the minimum millisecond threshold')

    @aetest.test
    def test_172_16_101_11_max_ms(self):
        # Test for ping minimum ms
        self.failed_max_ms={}
        if self.no_ping_response_172_16_101_11:
            log.info("PING Failed - No Maximum MS to Measure")
        else:        
            ping_max_ms_threshold = 10
            table_data = []
            for interface,value in self.ping_172_16_101_11_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['max_ms'] <= ping_max_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])                
                    table_row.append('Failed')
                    self.failed_max_ms = value['ping']['statistics']['round_trip']['max_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Maximum MS Threshold', 'Actual Maximum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_max_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.101.11 above the maximum millisecond threshold')
        elif self.no_ping_response_172_16_101_11:
            self.failed("There were no responses to PING - Unable to test maximum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.101.11 within the maximum millisecond threshold')

    @aetest.test
    def test_172_16_102_11_max_ms(self):
        # Test for ping minimum ms
        self.failed_max_ms={}
        if self.no_ping_response_172_16_102_11:
            log.info("PING Failed - No Maximum MS to Measure")
        else:        
            ping_max_ms_threshold = 10
            table_data = []
            for interface,value in self.ping_172_16_102_11_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['max_ms'] <= ping_max_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_max_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['max_ms'])                
                    table_row.append('Failed')
                    self.failed_max_ms = value['ping']['statistics']['round_trip']['max_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Maximum MS Threshold', 'Actual Maximum MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_max_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.102.11 above the maximum millisecond threshold')
        elif self.no_ping_response_172_16_102_11:
            self.failed("There were no responses to PING - Unable to test maximum millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.102.11 within the maximum millisecond threshold')

    @aetest.test
    def test_172_16_101_11_avg_ms(self):
        # Test for ping minimum ms
        self.failed_avg_ms={}
        if self.no_ping_response_172_16_101_11:
            log.info("PING Failed - No Average MS to Measure")
        else:        
            ping_avg_ms_threshold = 7
            table_data = []
            for interface,value in self.ping_172_16_101_11_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['avg_ms'] <= ping_avg_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])                
                    table_row.append('Failed')
                    self.failed_avg_ms = value['ping']['statistics']['round_trip']['avg_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Average MS Threshold', 'Actual Average MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_avg_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.101.11 above the average millisecond threshold')
        elif self.no_ping_response_172_16_101_11:
            self.failed("There were no responses to PING - Unable to test average millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.101.11 within the average millisecond threshold')

    @aetest.test
    def test_172_16_102_11_avg_ms(self):
        # Test for ping minimum ms
        self.failed_avg_ms={}
        if self.no_ping_response_172_16_102_11:
            log.info("PING Failed - No Average MS to Measure")
        else:        
            ping_avg_ms_threshold = 7
            table_data = []
            for interface,value in self.ping_172_16_102_11_results[self.device.alias].items():
                table_row = []
                if value['ping']['statistics']['round_trip']['avg_ms'] <= ping_avg_ms_threshold:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])
                    table_row.append('Passed')
                else:
                    table_row.append(self.device.alias)
                    table_row.append(interface)
                    table_row.append(ping_avg_ms_threshold)                
                    table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])                
                    table_row.append('Failed')
                    self.failed_avg_ms = value['ping']['statistics']['round_trip']['avg_ms']
                table_data.append(table_row)
                # display the table
            log.info(tabulate(table_data,
                                headers=['Device', 'Interface', 'Average MS Threshold', 'Actual Average MS', 'Passed/Failed'],
                                tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_avg_ms:
            self.failed(f'{ self.device } Has An Interface PING to 172.16.102.11 above the average millisecond threshold')
        elif self.no_ping_response_172_16_102_11:
            self.failed("There were no responses to PING - Unable to test average millisecond threshold")            
        else:
            self.passed(f'All Interfaces on { self.device } PING 172.16.102.11 within the average millisecond threshold')

# ----------------
# Test Case #3 - Get CDP Neighbors and try to ping them
# ----------------
class PING_CDP_Neighbors(aetest.Testcase):
    """PING CDP Neighbor IPs from Interface they were discovered on"""

    @aetest.test
    def setup(self, testbed, device_name):
        """ Testcase Setup section """
        # connect to device
        self.device = testbed.devices[device_name]
        # Loop over devices in tested for testing

    @aetest.test
    def ping_CDP_Neighbors(self):
        number_of_pings = 5
        self.ping_cdp_neighbors_results = {}
        self.ping_cdp_neighbors_results[self.device.alias] = {}
        if self.device.os == "iosxe":
            self.cdp_neighbor_list = self.device.parse("show cdp neighbors detail")          
            for neighbor,value in self.cdp_neighbor_list['index'].items():
                for entry in value['entry_addresses']:
                    try: 
                        parsed_ping = self.device.parse(f"ping { entry } source { value['local_interface'] } repeat { number_of_pings }")
                        self.ping_cdp_neighbors_results[self.device.alias][neighbor] = parsed_ping
                    except: 
                        parsed_ping = "Invalid PING"
                        log.info(f"Sorry but we cannot ping { entry } from { value['local_interface'] } ")
        elif self.device.os == "nxos":
            self.cdp_neighbor_list = self.device.parse("show cdp neighbors detail")
            for neighbor,value in self.cdp_neighbor_list['index'].items():
                for entry in value['interface_addresses']:
                    try:
                        parsed_ping = self.device.parse(f"ping { entry } source { value['local_interface'] } count 5")
                        self.ping_cdp_neighbors_results[self.device.alias][neighbor] = parsed_ping
                    except:
                        parsed_ping = "Invalid PING"
                        log.info((f"Sorry but we cannot ping { entry } from { value['local_interface'] } "))

    @aetest.test
    def test_CDP_Neighbor_ping_success_rate_percentage(self):
        # Test for ping success rate
        self.failed_success_rate={}
        table_data = []
        for interface,value in self.ping_cdp_neighbors_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['success_rate_percent'] == 100.0:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(value['ping']['statistics']['success_rate_percent'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(value['ping']['statistics']['success_rate_percent'])                
                table_row.append('Failed')
                self.failed_success_rate = value['ping']['statistics']['success_rate_percent']
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Neighbor', 'Destination', 'Success Rate Percentage', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had Less Than 100% PING Aginst CDP Neighbor')
        else:
            self.passed(f'All Interfaces on { self.device } Had 100% PING Success Against CDP Neighbor')

    @aetest.test
    def test_CDP_Neighbor_ping_min_ms(self):
        # Test for ping minimum ms
        ping_min_ms_threshold = 2
        self.failed_success_rate={}
        table_data = []
        for interface,value in self.ping_cdp_neighbors_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['round_trip']['min_ms'] <= ping_min_ms_threshold:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(ping_min_ms_threshold)
                table_row.append(value['ping']['statistics']['round_trip']['min_ms'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(ping_min_ms_threshold)
                table_row.append(value['ping']['statistics']['round_trip']['min_ms'])               
                table_row.append('Failed')
                self.failed_success_rate = value['ping']['statistics']['round_trip']['min_ms']
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Neighbor', 'Destination', 'Minimum MS Threshold', 'Actual Minimum MS', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had above the minimum millisecond threshold PING Aginst CDP Neighbor')
        else:
            self.passed(f'All Interfaces on { self.device } within the minimum millisecond threshold PING Against CDP Neighbor')

    @aetest.test
    def test_CDP_Neighbor_ping_max_ms(self):
        # Test for ping maximum ms
        ping_max_ms_threshold = 4
        self.failed_success_rate={}
        table_data = []
        for interface,value in self.ping_cdp_neighbors_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['round_trip']['max_ms'] <= ping_max_ms_threshold:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(ping_max_ms_threshold)
                table_row.append(value['ping']['statistics']['round_trip']['max_ms'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(ping_max_ms_threshold)
                table_row.append(value['ping']['statistics']['round_trip']['max_ms'])               
                table_row.append('Failed')
                self.failed_success_rate = value['ping']['statistics']['round_trip']['max_ms']
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Neighbor', 'Destination', 'Maximum MS Threshold', 'Actual Maximum MS', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had above the maximum millisecond threshold PING Aginst CDP Neighbor')
        else:
            self.passed(f'All Interfaces on { self.device } within the maximum millisecond threshold PING Against CDP Neighbor')

    @aetest.test
    def test_CDP_Neighbor_ping_avg_ms(self):
        # Test for ping average ms
        ping_avg_ms_threshold = 3
        self.failed_success_rate={}
        table_data = []
        for interface,value in self.ping_cdp_neighbors_results[self.device.alias].items():
            table_row = []
            if value['ping']['statistics']['round_trip']['avg_ms'] <= ping_avg_ms_threshold:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(ping_avg_ms_threshold)
                table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])
                table_row.append('Passed')
            else:
                table_row.append(self.device.alias)
                table_row.append(interface)
                table_row.append(value['ping']['address'])
                table_row.append(ping_avg_ms_threshold)
                table_row.append(value['ping']['statistics']['round_trip']['avg_ms'])               
                table_row.append('Failed')
                self.failed_success_rate = value['ping']['statistics']['round_trip']['avg_ms']
            table_data.append(table_row)
            # display the table
        log.info(tabulate(table_data,
                            headers=['Device', 'Neighbor', 'Destination', 'Average MS Threshold', 'Actual Average MS', 'Passed/Failed'],
                            tablefmt='orgtbl'))
        # should we pass or fail?
        if self.failed_success_rate:
            self.failed(f'{ self.device } Has An Interface That Had above the average millisecond threshold PING Aginst CDP Neighbor')
        else:
            self.passed(f'All Interfaces on { self.device } within the average millisecond threshold PING Against CDP Neighbor')

    @aetest.test
    def create_files(self):
        # Create .JSON files
        with open(f'JSON/{self.device.alias}_CDP_Neighbors.json', 'w') as f:
            f.write(json.dumps(self.cdp_neighbor_list, indent=4, sort_keys=True))

        with open(f'JSON/{self.device.alias}_CDP_Neighbor_PING_Test.json', 'w') as f:
            f.write(json.dumps(self.ping_cdp_neighbors_results, indent=4, sort_keys=True))

# for running as its own executable
if __name__ == '__main__':
    aetest.main()