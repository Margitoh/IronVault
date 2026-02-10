# Project: IronVault (Local Password Manager)
**Target Stack:** Python 3.11+, PySide6 (Qt), SQLite + Cryptography
**User Vision:** A beautiful, offline, desktop-first replacement for a physical password notebook.
**Design Aesthetic:** Minimalist, "Obsidian-like" dark mode, clean typography, distinct "Card" layout.

---

## 1. Core Philosophy
* **Offline First:** No cloud syncing, no servers. Data lives in a local encrypted file (`vault.db`).
* **Zero Knowledge:** The application never stores the Master Password. It uses it only to derive the decryption key in memory.
* **Visual Organization:** Not just a list. We organize by "Life Areas" (e.g., TCG Shop, Etsy, Freelance).

---

## 2. Technical Stack (Strict Constraints)
* **GUI Framework:** `PySide6` (Qt for Python).
    * *Reasoning:* Allows for CSS-like styling (QSS) to achieve the "pretty/minimal" look better than Tkinter.
* **Database:** `SQLite3` (Standard library).
* **Security/Encryption:** `cryptography` library.
    * **Key Derivation:** Argon2id (for hashing the master password).
    * **Encryption:** Fernet (AES-128-CBC with HMAC) or AES-GCM for field-level encryption.
* **Packaging:** `PyInstaller` (to create the .exe).

---

## 3. Feature Specifications

### A. The "Vault" View (UI)
* **Sidebar:** Vertical tabs for Categories (e.g., "TCG Market", "Etsy Shop", "Personal", "Freelance/Upwork").
* **Search Bar:** Global "Fuzzy Search" at the top.
    * *Behavior:* Typing "Upwork" instantly filters the list. Typing "Free" shows Freelance category items.
* **Card Grid:** Passwords show as "Cards" with a Logo/Icon and Title.
* **Action:** Hovering over a card reveals "Copy Username" and "Copy Password" buttons.
    * *Security:* Clipboard clears automatically after 30 seconds.

### B. The Data Structure
Each entry must support:
* **Title** (e.g., "Cardmarket")
* **Category** (e.g., "TCG Shop")
* **Username/Email**
* **Password** (Hidden by default, toggle to view)
* **2FA/Recovery Codes** (Multi-line secure notes area)
* **Custom Tags**

### C. Import/Export
* **Export:** JSON format (Encrypted with Master Password).
* **Import:** Ability to ingest the encrypted JSON file (for moving from PC to Laptop).

---

## 4. Security Architecture (Agent Rules)
* **Rule 1:** NEVER store the Master Password in a file or DB.
* **Rule 2:** When the app closes, wipe the key from memory.
* **Rule 3:** The database file is just a container for *encrypted blobs*. If someone steals `vault.db`, they should see garbage data.

---

## 5. Development Phases

**Phase 1: The Secure Core**
* Build the `CryptoManager` class.
* Implement `generate_key(master_password)` and `encrypt/decrypt` functions.
* Verify Argon2 hashing is working.

**Phase 2: The UI Skeleton**
* Build the Main Window with PySide6.
* Implement the Sidebar and "Card Grid" layout.
* Apply the "Dark Minimalist" stylesheet (QSS).

**Phase 3: The Glue**
* Connect the UI "Add Password" form to the Secure Core.
* Implement the Search filtering logic.
* Add Clipboard utilities.