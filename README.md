[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/automateyournetwork/pyats_ping_tests)

# pyats_ping_tests
A connectivity test starter kit for pyATS

## Installation

### Create virtual environment
```console
$ python3 -m venv ping_test
$ source ping_test/bin/activate
(ping_test) $
```

### Install prerequisites
```console
(ping_test) $ pip install pyats[full]
(ping_test) $ pip install tabulate
```

### Clone the repo
``` console
(ping_test) $ git clone https://github.com/automateyournetwork/pyats_ping_tests.git
(ping_test) $ cd pyats_ping_tests
(ping_test) pyats_ping_tests $ 
```

### Reserve Cisco DevNet CML Sandbox
![Cisco Modeling Labs Enterprise](images/CiscoModelingLabsEnterprise.png)
https://devnetsandbox.cisco.com/RM/Diagram/Index/45100600-b413-4471-b28e-b014eb824555?diagramType=Topology

### Connect to VPN 
### Wait for CML to fully initialize 
Please confirm you can SSH to the following devices before running the pyATS job:
10.10.20.175
10.10.20.176
10.10.20.177
10.10.20.178
## Run the pyATS Job 
(ping_test) pyats_ping_tests $ pyats run job pyats_ping_tests_job.py

## (Optional) View the logs with the pyATS Log Viewer
(ping_test) pyats_ping_tests $ pyats logs view

## Make adjustments
You can adjust the number of pings 

```python
number_of_pings = 5
```

You can adjust the minimum, maximum, and average millisecond response times

```python
ping_min_ms_threshold = 5
ping_max_ms_threshold = 10
ping_avg_ms_threshold = 7
```
