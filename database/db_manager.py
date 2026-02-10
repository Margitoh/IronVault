import sqlite3
import os
import json
from core.security import SecurityManager

class DBManager:
    def __init__(self, db_path="vault.db"):
        self.db_path = db_path
        self.conn = None
        # Connect immediately to ensure tables exist or to check if it's a new vault
        self._connect()
        self._create_tables()
        self._check_schema()

    def _connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # Metadata table: Stores the salt and the verifier (hash of the key)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value BLOB
            )
        """)
        
        # Entries table: Stores the encrypted passwords
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                uuid TEXT PRIMARY KEY,
                category TEXT,
                title TEXT,
                username TEXT,
                email TEXT,
                ciphertext BLOB,
                nonce BLOB
            )
        """)
        self.conn.commit()

    def _check_schema(self):
        """Checks for missing columns and adds them (Migration)."""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(entries)")
        columns = [row['name'] for row in cursor.fetchall()]
        
        if 'email' not in columns:
            print("Migrating DB: Adding 'email' column...")
            cursor.execute("ALTER TABLE entries ADD COLUMN email TEXT")
            self.conn.commit()

    def is_new_vault(self) -> bool:
        """Returns True if the vault has no master password set."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM metadata WHERE key='salt'")
        return cursor.fetchone() is None

    def initialize_vault(self, password: str) -> tuple[bool, str]:
        """
        Sets up the vault with a new master password.
        Returns (Success, ErrorMessage).
        """
        try:
            salt = SecurityManager.generate_salt()
            key = SecurityManager.derive_key(password, salt)
            verifier = SecurityManager.hash_key(key)
            
            cursor = self.conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)", ('salt', salt))
            cursor.execute("INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)", ('verifier', verifier))
            self.conn.commit()
            return True, ""
        except Exception as e:
            return False, str(e)

    def verify_password(self, password: str) -> bytes:
        """
        Checks if the password is correct.
        Returns the Derived Key if correct, None otherwise.
        """
        try:
            cursor = self.conn.cursor()
            
            # Get Salt
            cursor.execute("SELECT value FROM metadata WHERE key='salt'")
            salt_row = cursor.fetchone()
            if not salt_row:
                return None
            salt = salt_row['value']
            
            # Get Verifier
            cursor.execute("SELECT value FROM metadata WHERE key='verifier'")
            verifier_row = cursor.fetchone()
            if not verifier_row:
                return None
            stored_verifier = verifier_row['value']
            
            # Derive Key and Check Hash
            derived_key = SecurityManager.derive_key(password, salt)
            computed_verifier = SecurityManager.hash_key(derived_key)
            
            if computed_verifier == stored_verifier:
                return derived_key
            else:
                return None
        except Exception as e:
            print(f"Error verifying password: {e}")
            return None

    def add_entry(self, encryption_key: bytes, category: str, title: str, username: str, email: str, password: str, note: str):
        """
        Encrypts the secret data (password + note) and saves it to the DB.
        """
        import uuid
        entry_uuid = str(uuid.uuid4())
        
        # Store password and note in a JSON object before encryption
        secret_payload = {
            "password": password,
            "note": note
        }
        secret_json = json.dumps(secret_payload)
        
        nonce, ciphertext = SecurityManager.encrypt(secret_json, encryption_key)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (uuid, category, title, username, email, ciphertext, nonce)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (entry_uuid, category, title, username, email, ciphertext, nonce))
        self.conn.commit()

    def get_all_entries(self):
        """
        Returns all entries (ciphertext is still encrypted).
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM entries")
        return cursor.fetchall()

    def delete_entry(self, uuid: str):
        """Deletes an entry by UUID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM entries WHERE uuid=?", (uuid,))
        self.conn.commit()

    def update_entry(self, uuid: str, encryption_key: bytes, category: str, title: str, username: str, email: str, password: str, note: str):
        """Updates an existing entry."""
        secret_payload = {
            "password": password,
            "note": note
        }
        secret_json = json.dumps(secret_payload)
        
        nonce, ciphertext = SecurityManager.encrypt(secret_json, encryption_key)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE entries 
            SET category=?, title=?, username=?, email=?, ciphertext=?, nonce=?
            WHERE uuid=?
        """, (category, title, username, email, ciphertext, nonce, uuid))
        self.conn.commit()

    def delete_all(self):
        """For testing: Wipes the DB."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM metadata")
        cursor.execute("DELETE FROM entries")
        self.conn.commit()
