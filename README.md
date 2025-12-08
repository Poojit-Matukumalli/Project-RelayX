## - Project RelayX -

***Built for Privacy, Funded by You.***

If you are interested in setting up a RelayX of your own, check out [SETUP.md](SETUP.md)


---

## Overview :

RelayX is a *desktop messaging platform* designed for *maximum privacy and security*, without server dependence (Semi-Decentralized), combining Tor networking with modern cryptography and a lightweight Flutter UI.

Key highlights:
- No servers, messages are sent using tor infrastructure and user maintained RelayX nodes.
- Anonymous multi-hop messaging through Tor relays.
- X25519-based key exchange and HKDF session keys for secure communication.
- Signed messages and timestamping to prevent replays.
- Asynchronous communication for smooth UX.
- Zero metadata. Your privacy, always first.

---

## Architecture

- *Frontend:* Flutter desktop app (Windows/Linux).  
- *Backend:* Python FastAPI server handling user management, encryption, and routing.  
- *Cryptography:* X25519 DH handshake, Fernet encryption, digital signatures, AESCGM, HKDF.  
- *Persistence:* SQLite database via SQLAlchemy for user and message storage.

---

## Features :

- *Anonymous Messaging:* Messages route through multiple Tor relays and Multiple user set-up RelayX relay servers
- *Secure Key Management:* Each user has a signature public key; session keys derived securely.  
- *Replay Protection:* Messages are signed and timestamped.  
- *Email Integration:* New users receive signature public keys via email automatically.  
- *Cross-Platform Desktop:* Flutter UI runs on Windows, Linux, and Android.  
- *Zero Metadata:* No nnecessary data sent in the envelope; privacy-first approach.  

---

## Installation

### Pre-built Installer (Recommended)
1. Download the latest installer for your OS.  
2. Run the installer; a desktop shortcut will be created.  
3. Launch the app—the backend and frontend start automatically.

### Developer Setup
```bash
git clone https://github.com/Poojit-Matukumalli/Project-RelayX.git
```
```
cd Project-RelayX
```
```
pip install -r requirements.txt
```
```
flutter build windows (or) linux
```
Run backend and frontend separately :
For Windows:
```
cd Project-RelayX\Windows\RelayX.py && cls && python main.py
```
---

## Usage :

1. Launch the app.


2. Add a new user by entering their username.


3. RelayX generates cryptographic IDs internally and provides a QR code.


4. Start secure messaging over Tor relays immediately.


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

For full terms, see [LICENSE.md](LICENSE.md).

## 📬 Contact

By The Project-RelayX Team.
Founded by - Poojit Matukumalli.

Reach out via email or open an issue on GitHub.
If Emailing about any issues, Please summarize the issue in 10 words or less in the Subject line.
Anyone can reach out casually if they want.

Thank you for using Project RelayX.

Email : projectrelayx@gmail.com
