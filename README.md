## Project RelayX

***Built for Privacy, Funded by You.***

If you are interested in setting up a RelayX of your own, check out [SETUP.md](SETUP.md).

Credits at [CREDITS.md](GitHub-docs/CREDITS.md)

---

## Overview

RelayX is a *desktop messaging platform* designed for *maximum privacy and security*, without server dependence (semi-decentralized).  
It combines Tor networking with modern cryptography and a lightweight Flutter UI.

**Key highlights:**
- No central servers — messages are sent through the Tor network and user-maintained RelayX nodes.  
- Anonymous multi-hop messaging via Tor relays.  
- X25519-based key exchange with HKDF-derived session keys.  
- Signed messages with timestamping to prevent replay attacks.  
- Asynchronous communication for smooth user experience.  
- Zero metadata — privacy first, always.

---

## Architecture

- **Frontend:** Flutter desktop app (Windows/Linux).  
- **Backend:** Python FastAPI server handling user management, encryption, and routing.  
- **Cryptography:** X25519 Diffie–Hellman handshake, HKDF, Fernet encryption, AES-GCM, digital signatures.  
- **Persistence:** SQLite database via SQLAlchemy for user and message storage.

---

## Features

- **Anonymous Messaging:**  
  Messages route through multiple Tor relays and user-hosted RelayX relay servers.

- **Secure Key Management:**  
  Each user has a signature public key; session keys are derived securely.

- **Replay Protection:**  
  All messages are signed and timestamped.

- **Email Integration:**  
  New users automatically receive their signature public keys via email.

- **Cross-Platform Desktop:**  
  Flutter UI runs on Windows, Linux, and Android.

- **Zero Metadata:**  
  No unnecessary data is included in the envelope — privacy-first design.

---

## Installation

### Pre-built Installer (Recommended)

1. Download the latest installer for your OS.  
2. Run the installer; a desktop shortcut will be created.  
3. Launch the app — the backend and frontend start automatically.

---

### Developer Setup

```
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
cd Project-RelayX\Windows\RelayX && cls && python main.py
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
