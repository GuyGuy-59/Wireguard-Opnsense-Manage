import requests, json, ipaddress, urllib3, argparse
urllib3.disable_warnings()


def Getoverlappingnetworks(Realms, Realm):
    overlapping = []
    for entry in sum([item.split(",") for item in Realms], []):
        network = ipaddress.ip_network(entry)
        if network.overlaps(Realm):
            overlapping.append(network)
    return overlapping

def Get_Servers():
    r = requests.get(f'{opnsenseURL}/api/wireguard/server/searchServer/',auth=(APIkey, APIsecret), verify=False)
    if r.status_code == 200:
         return(json.dumps(r.json(), indent=4))
    else:    
        return(r.text)

def Get_Server(ServerUUID):
    r = requests.get(f'{opnsenseURL}/api/wireguard/server/getServer/{ServerUUID}',auth=(APIkey, APIsecret), verify=False)
    if r.status_code == 200:
         #print(json.dumps(r.json(), indent=4))
         return (json.dumps(r.json(), indent=4))
    else:    
        print(r.text)

def Create_Server(ServerName, tunnelAddress, tunnelPort):
    r = requests.get(f'{opnsenseURL}/api/wireguard/server/key_pair/',auth=(APIkey, APIsecret), verify=False)
    if r.status_code == 200:
        privkey = r.json()["privkey"]
        pubkey = r.json()["privkey"]
        createInstance = {
            "server": {
                "carp_depend_on": "",
                "disableroutes": "0",
                "dns": "",
                "enabled": "1",
                "gateway": "",
                "mtu": "",
                "name": ServerName,
                "peers": "",
                "port": tunnelPort,
                "privkey": privkey,
                "pubkey": pubkey,
                "tunneladdress": tunnelAddress
            }
        }
    r = requests.post(f'{opnsenseURL}/api/wireguard/server/addServer/', data=json.dumps(createInstance),headers={'content-type': 'application/json'}, auth=(APIkey, APIsecret), verify=False)
    if r.status_code == 200:
        if r.json()["uuid"]:
            print('{"uuid":"'+r.json()["uuid"]+'"}')
        else:
            print(r.text)
    else:
        print(r.text)

def Delete_Server(ServerUUID):
    wireguardsServer = Get_Server(ServerUUID)
    if wireguardsServer :
        print(f'Server {ServerUUID} exist')
        r = requests.post(f'{opnsenseURL}/api/wireguard/server/delServer/{ServerUUID}', auth=(APIkey, APIsecret), verify=False)
        if r.status_code == 200:
            print(r.text)


def Get_Status_Service():
    r = requests.get(f'{opnsenseURL}/api/wireguard/general/getStatus',auth=(APIkey, APIsecret), verify=False)
    if r.status_code == 200:
         return(json.dumps(r.json(), indent=4))
    else:    
        return(r.text)
    r = requests.get(f'{opnsenseURL}/api/wireguard/service/showconf',auth=(APIkey, APIsecret), verify=False)
    if r.status_code == 200:
         return(json.dumps(r.json(), indent=4))
    else:    
        return(r.text)

def Reconfigure():
    r = requests.post(f'{opnsenseURL}/api/wireguard/service/reconfigure', data='{}',headers={'content-type': 'application/json'}, auth=(APIkey, APIsecret), verify=True)
    print(r.text)

def Get_clients():
    r = requests.get(f'{opnsenseURL}/api/wireguard/client/searchClient/',auth=(APIkey, APIsecret),verify=False)
    if r.status_code == 200:
        #print(json.dumps(r.json(), indent=4))
        return (json.dumps(r.json(), indent=4))
    else:
        print(r.text)

def Get_client(PeerUUID):
    r = requests.get(f'{opnsenseURL}/api/wireguard/client/getClient/{PeerUUID}',auth=(APIkey, APIsecret),verify=False)
    if r.status_code == 200:
        #print(json.dumps(r.json(), indent=4))
        return (json.dumps(r.json(), indent=4))
    else:
        print(r.text)

def Create_client(PeerName, pubkey, tunnelAddress):
    wireguardsClients = Get_clients()
    wireguardsClients = json.loads(wireguardsClients)
    if PeerName in [item["name"] for item in wireguardsClients["rows"]]:
        print(f'Client {PeerName} name exists. This is OPNsense-wise valid, but not recommended. Make manual configuration in WebGUI if wanted.')
    else:    
        try:
            tunnelNetwork=ipaddress.ip_network(tunnelAddress)
            print(f'Tunnel Address {tunnelAddress} is valid.')
        except:
            print(f'Tunnel Address {tunnelAddress} is not valid.')

        overlapping = Getoverlappingnetworks([client['tunneladdress'] for client in wireguardsClients["rows"]],tunnelNetwork)
        if overlapping:
            print(f'Client Adress {tunnelNetwork} overlaps with existing tunnels. This is OPNsense-wise valid, but not recommended. Make manual configuration in WebGUI if wanted.')
            exit
        else:
            createPeer = {
                "client": {
                    "enabled": '1',
                    "name": PeerName,
                    "pubkey": pubkey,
                    "tunneladdress": tunnelAddress,
                    "keepalive ": '25'
                }
            }
            r = requests.post(f'{opnsenseURL}/api/wireguard/client/addClient/', data=json.dumps(createPeer),headers={'content-type': 'application/json'}, auth=(APIkey, APIsecret), verify=False)
            if r.status_code == 200:
                if r.json()["uuid"]:
                    print('{"uuid":"'+r.json()["uuid"]+'"}')
                else:
                    print(r.text)
            else:
                print(r.text)

def Delete_client(PeerName,PeerUUID):
    wireguardsClients = Get_client(PeerUUID)
    wireguardsClients = json.loads(wireguardsClients)
    if PeerName in wireguardsClients["client"]["name"]:
        print(f'Client {PeerName} exists')
        r = requests.post(f'{opnsenseURL}/api/wireguard/client/delClient/{PeerUUID}',auth=(APIkey, APIsecret), verify=False)
        if r.status_code == 200:
            print(r.text)

def Enable_client(ServerName,ServerUUID, PeerName, PeerUUID):
    # get currently selected peers from server
    wireguardsServer = Get_Server(ServerUUID)
    wireguardsServer = json.loads(wireguardsServer)
    wireguardsClients = Get_client(PeerUUID)
    wireguardsClients = json.loads(wireguardsClients)
    if ServerName in wireguardsServer["server"]["name"] and PeerName in wireguardsClients["client"]["name"]:
        print(f'Client {PeerName} exists and Server {ServerName} exists')
        ServerPeers = wireguardsServer['server']['peers']
        selectedPeers = [peer for peer in ServerPeers if ServerPeers[peer]['selected']]
        peersToSelect = ','.join(selectedPeers + [PeerUUID])
        wireguardInstanceInfo = {'server': {'peers': peersToSelect}}
        r = requests.post(f'{opnsenseURL}/api/wireguard/server/setServer/{ServerUUID}', data=json.dumps(wireguardInstanceInfo), headers={'content-type': 'application/json'}, auth=(APIkey, APIsecret), verify=False)
        print(r.text)
    else:
        print(r.text)


if __name__ == '__main__':
    module_functions = {
    'GetClients': Get_clients,
    'CreateClient': Create_client,
    'EnableClient': Enable_client,
    'DeleteClient': Delete_client,
    'GetServers': Get_Servers,
    'CreateServer': Create_Server,
    'DeleteServer': Delete_Server,
    'GetState': Get_Status_Service
    }

    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-t', '--target', help='Target IP or Domain OPNSense', type=str,required=True)
    parser.add_argument('--key', help='https://docs.opnsense.org/development/how-tos/api.html', type=str,required=True)
    parser.add_argument('--secret', help='https://docs.opnsense.org/development/how-tos/api.html', type=str,required=True)
    parser.add_argument('-M', '--module',  choices=module_functions.keys(), help='Specify the module to execute')
    parser.add_argument('-d', '--data', nargs='+', help='Additional data to pass to the specified module.')
    args= parser.parse_args()



    APIkey=f'{args.key}'
    APIsecret=f'{args.secret}'
    opnsenseURL=f"https://{args.target}"
    module = args.module
    selected_function = module_functions.get(module, None)
    if args.data:
        selected_function(*args.data)
    else:
        print(selected_function())

