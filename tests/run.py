from core.security import SecurityManager
import os
import sys

def main():
    print("--- IronVault Security Core Test ---")
    
    # 1. Simulate Master Password Input
    master_password = input("Enter Master Password: ")
    if not master_password:
        print("Password cannot be empty.")
        return

    # 2. Generate Salt (normally stored in DB)
    print("\n[1] Generating Salt...")
    salt = SecurityManager.generate_salt()
    print(f"Salt: {salt.hex()}")

    # 3. Derive Key
    print("\n[2] Deriving Key (Argon2id)...")
    try:
        key = SecurityManager.derive_key(master_password, salt)
        print(f"Derived Key (32 bytes): {key.hex()}")
    except Exception as e:
        print(f"Error deriving key: {e}")
        return

    # 4. Encrypt Data
    secret_data = "This is a secret note about TCG cards."
    print(f"\n[3] Encrypting Data: '{secret_data}'")
    try:
        nonce, ciphertext = SecurityManager.encrypt(secret_data, key)
        print(f"Nonce: {nonce.hex()}")
        print(f"Ciphertext: {ciphertext.hex()}")
    except Exception as e:
        print(f"Error encrypting data: {e}")
        return

    # 5. Decrypt Data
    print("\n[4] Decrypting Data...")
    try:
        decrypted_data = SecurityManager.decrypt(nonce, ciphertext, key)
        print(f"Decrypted: '{decrypted_data}'")
        
        if decrypted_data == secret_data:
            print("\nSUCCESS: Decrypted data matches original!")
        else:
            print("\nFAILURE: Data mismatch!")
    except Exception as e:
        print(f"Error decrypting data: {e}")

    try:
        input("\nPress Enter to exit...")
    except:
        pass

if __name__ == "__main__":
    main()
