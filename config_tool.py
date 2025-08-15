import argparse
from utils.config_manager import ConfigManager
import getpass

def main():
    parser = argparse.ArgumentParser(description="Configuration Management Tool")
    parser.add_argument("--env", default="development", help="Environment (development/production)")
    parser.add_argument("--encrypt", action="store_true", help="Encrypt and save configuration")
    parser.add_argument("--decrypt", action="store_true", help="Load and decrypt configuration")
    args = parser.parse_args()
    
    config = ConfigManager(env=args.env)
    
    if args.encrypt:
        password = getpass.getpass("Enter encryption password: ")
        confirm = getpass.getpass("Confirm password: ")
        
        if password != confirm:
            print("Passwords do not match!")
            return
        
        if not config.validate_config():
            print("Configuration validation failed. Please check your .env file.")
            return
        
        config.save_encrypted_config(password)
        print("Configuration encrypted and saved to config.enc")
    
    elif args.decrypt:
        password = getpass.getpass("Enter decryption password: ")
        config.load_encrypted_config(password)
        
        if config.validate_config():
            print("Configuration loaded and validated successfully!")
        else:
            print("Configuration validation failed after decryption.")
    
    else:
        if config.validate_config():
            print("Current configuration is valid.")
        else:
            print("Configuration validation failed. Please check your .env file.")

if __name__ == "__main__":
    main() 