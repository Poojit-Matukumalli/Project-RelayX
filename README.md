## RelayX Messenger

***Built for Privacy, Funded by You.***

If you are interested in setting up a RelayX of your own, check out [SETUP.md](GitHub-docs/SETUP.md).
Also known as 'Project RelayX'
Credits at [CREDITS.md](GitHub-docs/CREDITS.md). 

---

## Overview

RelayX Messenger is a *desktop messaging platform* designed for *maximum privacy and security*, without server dependence (semi-decentralized).  
It combines Tor networking with modern cryptography and a lightweight Flutter UI.

**Key highlights:**
- No central servers. Messages are sent through the Tor network and user-maintained RelayX relays.  
- Anonymous multi-hop messaging via Tor relays.  
- X25519-based key exchange (ECDH) with HKDF-derived session keys.  
- Asynchronous communication for smooth user experience.  
- Very minimal metadata — privacy first, always.

---

## Architecture

- **Frontend:** Flutter desktop app (Windows/Linux) (Unfinished).  
- **Backend:** Python FastAPI server handling user management, encryption, and routing (Complete).  
- **Cryptography:** X25519 Diffie–Hellman handshake, HKDF, Fernet encryption (at-rest), AES-GCM. 
- **Persistence:** SQLite database via SQLAlchemy for user and message storage.

---

## Features

- **Anonymous Messaging:**  
  Messages route through multiple Tor relays and user-hosted RelayX relay servers.

- **Secure Key Management:**  
  Each user has a signature public key; session keys are derived securely.

- **Cross-Platform Desktop:**  
  Flutter UI runs on Windows, Linux, and Android.

- **Minimal Metadata:**  
  No Sensitive data is included in the envelope — privacy-first design. All details at [Packet info](GitHub-docs/packet_info.md)

---

## Installation

### Application

1. Visit [RelayX-Build](https://github.com/RelayX-Messenger/RelayX-Build) for the application (Program Files) format. 
2. Go to the releases and download the latest one (v0.1) and extract it to C:\Program Files\RelayX
3. Program Files does not allow executables to do malware behavior like extracting to the working dir (Program Files blocks it).
4. If unsure, Extract to a VM and let virustotal analyze all executables individually.  
5. Launch the C:\Program Files\RelayX\RelayX.exe and use FastAPI's SwaggerUI for using endpoints.

---

### Developer Setup
The steps below are for Windows users.
```
git clone https://github.com/Poojit-Matukumalli/Project-RelayX.git
```
```
cd Project-RelayX
```
```
pip install -r requirements.txt
```
Run backend :
For Windows:
```
cd Project-RelayX\Windows\RelayX && cls && python main.py
```
For Linux:
```
Build a version of it (swap tor and its executables and recompile chunker.so (Project-RelayX/Windows/utilities/chunker.so) and rename Project-RelayX/Windows to Project-RelayX/Linux if you prefer.

It needs a separate build for linux. also make sure to swap paths in Project-RelayX/RelayX/utils/paths.py and use the build from https://github.com/RelayX-Messenger/RelayX-Build.
```
---

## Usage :

1. cURL
2. SwaggerUI

---

## Contributing :

We welcome contributions! Guidelines:

1. Keep code well-documented.

2. Avoid & review before committing private keys or sensitive data.

3. Update requirements.txt with any new dependencies.

4. Submit pull requests or open issues for bug reports/features.

---
## License :

Project RelayX is licensed under the custom **RelayX Non-Commercial License**.

For full terms, see [LICENSE.md](GitHub-docs/LICENSE.md).

## 📬 Contact

By The Project-RelayX Team.
Founded by - Poojit Matukumalli.

Reach out via email or open an issue on GitHub.
If Emailing about any issues, Please summarize the issue in 10 words or less in the Subject line.
Anyone can reach out casually if they want.

Thank you for using the RelayX Messenger.

Email : projectrelayx@gmail.com
