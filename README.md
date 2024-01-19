# Wireguard-Opnsense-Manage
The provided script is a Python program that interacts with the OPNsense API for wireguad module. It allows you to perform various operations for servers or users, such as obtain, add, modify and delete.
API access is part of the local user authentication system, but uses key/secret pairs.

## General Help
![alt text](https://raw.githubusercontent.com/GuyGuy-59/Wireguard-Opnsense-Manage/main/pictures/WGmanage.png)

## Modules Help
#### CreateServer
Add an instance by giving it a name and the tunnel address(network/cidr)/port.
```sh
WG_Opnsense_manage.py -t fw.local --key APIkey --secret APIsecret -M CreateServer -d ServerName tunnelAddress tunnelPort
```
#### GetServers
Get all instances.
```sh
WG_Opnsense_manage.py -t fw.local --key APIkey --secret APIsecret -M GetServers
```
#### DeleteServer
Delete the instance with its UUID.
```sh
WG_Opnsense_manage.py  -t fw.local --key APIkey --secret APIsecret -M DeleteServer -D ServerUUID
```
#### GetState
Checking service.
```sh
WG_Opnsense_manage.py -t fw.local --key APIkey --secret APIsecret -M GetState
```
#### CreateClient
Add a peer by giving it a name, its address in the instance's tunnel range, and the peer's public key.
```sh
WG_Opnsense_manage.py -t fw.local --key APIkey --secret APIsecret -M CreateClient -D PeerName pubkey tunnelAddress
```
#### EnableClient
Associate a peer with the instance
```sh
WG_Opnsense_manage.py  -t fw.local --key APIkey --secret APIsecret -M EnableClient -D ServerName ServerUUID PeerName PeerUUID
```
#### DeleteClient
Delete the peer with its UUID
```sh
WG_Opnsense_manage.py -t fw.local --key APIkey --secret APIsecret -M DeleteClient -D PeerName PeerUUID
```
#### GetClients
Get all peer.
```sh
WG_Opnsense_manage.py  -t fw.local --key APIkey --secret APIsecret -M GetClients
```