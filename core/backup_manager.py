
import os
import shutil
import time
from core.security import SecurityManager

class BackupManager:
    def __init__(self, config_file="backup_config.json"):
        self.config_file = config_file
        self.backup_path = self._load_path()

    def _load_path(self):
        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return data.get('backup_path', None)
            except:
                return None
        return None

    def set_backup_path(self, path):
        self.backup_path = path
        import json
        with open(self.config_file, 'w') as f:
            json.dump({'backup_path': path}, f)

    def backup_db(self, db_path="vault.db", encryption_key=None):
        if not self.backup_path or not os.path.exists(self.backup_path):
            return False, "Backup folder not selected or invalid."
        
        try:
            target_file = os.path.join(self.backup_path, "vault.enc")
            
            with open(db_path, 'rb') as f:
                data = f.read()
                
            if encryption_key:
                # Encrypt the entire file
                # We can reuse SecurityManager.encrypt? 
                # SecurityManager.encrypt returns (nonce, ciphertext) in base64 usually or tuple.
                # Let's check SecurityManager.
                # For file encryption, we want a single blob.
                # Let's assume we can use the same logic but serialize the nonce+ciphertext.
                # Actually, SecurityManager.encrypt takes (data, key) -> (nonce, ciphertext).
                
                # We need to construct a robust format: [NONCE (16 bytes)][CIPHERTEXT]
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                
                # We assume generic key is 32 bytes.
                aesgcm = AESGCM(encryption_key)
                nonce = os.urandom(12)
                ciphertext = aesgcm.encrypt(nonce, data, None)
                
                encrypted_blob = nonce + ciphertext
                
                with open(target_file, 'wb') as f_out:
                    f_out.write(encrypted_blob)
                    
                return True, f"Encrypted and backed up to {target_file}"
            else:
                # Fallback to plain copy if no key (shouldn't happen with our logic)
                target_file = os.path.join(self.backup_path, "vault.db")
                shutil.copy2(db_path, target_file)
                return True, f"Backed up (Unencrypted) to {target_file}"

        except Exception as e:
            return False, f"Backup failed: {e}"

    def restore_db(self, target_db_path="vault.db", encryption_key=None):
        if not self.backup_path or not os.path.exists(self.backup_path):
            return False, "Backup folder not selected or invalid."
        
        source_file = os.path.join(self.backup_path, "vault.enc")
        
        # Check for legacy unencrypted file
        if not os.path.exists(source_file):
            legacy_file = os.path.join(self.backup_path, "vault.db")
            if os.path.exists(legacy_file):
                # Restore plain
                try:
                    if os.path.exists(target_db_path):
                        shutil.copy2(target_db_path, target_db_path + ".bak")
                    shutil.copy2(legacy_file, target_db_path)
                    return True, "Restored (Unencrypted Legacy) successfully."
                except Exception as e:
                    return False, f"Restore failed: {e}"
            return False, "No 'vault.enc' or 'vault.db' found in backup folder."
            
        try:
            # Create safety backup of current local
            if os.path.exists(target_db_path):
                shutil.copy2(target_db_path, target_db_path + ".bak") 
            
            with open(source_file, 'rb') as f_in:
                encrypted_blob = f_in.read()
                
            if encryption_key:
                from cryptography.hazmat.primitives.ciphers.aead import AESGCM
                aesgcm = AESGCM(encryption_key)
                
                nonce = encrypted_blob[:12]
                ciphertext = encrypted_blob[12:]
                
                plaintext = aesgcm.decrypt(nonce, ciphertext, None)
                
                with open(target_db_path, 'wb') as f_out:
                    f_out.write(plaintext)
                    
                return True, "Restored and Decrypted successfully."
            else:
                 return False, "Encryption key required for restore."

        except Exception as e:
            return False, f"Restore failed: {e}"

    def get_last_modified_remote(self):
        if not self.backup_path:
            return 0
        source_file = os.path.join(self.backup_path, "vault.enc")
        if os.path.exists(source_file):
            return os.path.getmtime(source_file)
        return 0
