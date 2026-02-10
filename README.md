
# IronVault - Secure Password Manager

IronVault is a robust, local-first password manager built with Python and PySide6, designed for security and simplicity.

## Features

- **Store & Organize**: Securely store passwords, notes, and sensitive data.
- **Strong Encryption**: Uses Argon2id for key derivation and AES-GCM for encryption.
- **Local Database**: Your data never leaves your device (stored in `vault.db`).
- **Modern UI**: Clean, dark-themed interface built with PySide6.
- **Portable**: Available as a single-file executable for Windows.

## Installation

### For Users
1. Download the latest `IronVault.exe` from the Releases page.
2. Run the executable.
3. Create a Master Password on first launch. **Do not forget this password!**

### For Developers

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Vault-password_manager.git
   cd Vault-password_manager
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## Building from Source

To create the executable:

```bash
pip install pyinstaller
pyinstaller IronVault.spec --clean --noconfirm
```

The output file will be in the `dist/` directory.

## Security

IronVault uses industry-standard cryptography:
- **Key Derivation**: Argon2id (memory-hard, resistant to GPU cracking).
- **Encryption**: AES-256-GCM (provides confidentiality and integrity).
- **Zero-Knowledge**: Validates your password hash without storing the actual key.

## License

MIT License.
