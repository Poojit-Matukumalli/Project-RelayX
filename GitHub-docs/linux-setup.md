# Developer setup for linux (Ubuntu)

### Details :
- 1. tor subprocess using python can be quite finnicky, because linux tor is strict about file ownership and permissions
- 2. This setup explains all about the Linux setup for tor.

## Pre Setup steps:

#### Incase of a fresh install, First setup git, python and pip.
#### 1. Git
```
sudo apt install git
```
#### 2. Python:
```
sudo add-apt-repository ppa:deadsnakes/ppa
```
- Default python version from apt would be lower than the requirement.

```
sudo apt update && sudo apt install ppython3.13
```
- Installing pip
```
sudo apt install python3-pip
```
- The pre-req are done.

## Installation:
### Clone the repo:
```
git clone https://github.com/Poojit-Matukumalli/Project-RelayX
```

#### Install dependencies:
```
cd ~/Project-RelayX/GitHub-docs && pip install -r requirements.txt
```
- Wait for it to finish installing everything

## Setup & Post installation

By default, permissions and ownership are not set-up properly. 

### Setup permissions:
#### 1. Pluggable transports:
```
cd ~/Project-RelayX/Linux/Networking/tor/pluggable_transports && chmod +x conjure-client lyrebird
```
#### 2. Tor executable
```
cd ~/Project-RelayX/Linux/Networking/tor && chmod +x tor
```
#### 3. Test tor
```
./tor
```
If it says libevent is missing, insrtall it by running
```
sudo apt install libevent-2.1-7
```
#### 4. Changing file Permissions
```
cd ~ && chmod 700 Project-RelayX/Linux/Networking/data Project-RelayX/Linux/Networking/data/HiddenService
```

## Final step:
Run the main file
```
cd ~/Project-RelayX/Linux/RelayX && clear && python3 main.py
```

## Contact :
If any issues pop up, Contact me.

Email : projectrelayx@gmail.com