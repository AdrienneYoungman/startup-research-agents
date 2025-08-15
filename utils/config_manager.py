import os
from typing import Dict, Optional
from dotenv import load_dotenv
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class ConfigManager:
    def __init__(self, env: str = "development"):
        self.env = env
        self.config: Dict = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration based on environment"""
        # Load base .env file
        load_dotenv()
        
        # Load environment-specific .env file if it exists
        env_file = f".env.{self.env}"
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Load configuration
        self.config = {
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "supabase_url": os.getenv("SUPABASE_URL"),
            "supabase_key": os.getenv("SUPABASE_KEY"),
        }
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: str):
        """Set a configuration value"""
        self.config[key] = value
    
    @staticmethod
    def generate_key(password: str, salt: bytes) -> bytes:
        """Generate an encryption key from a password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def encrypt_value(self, value: str, password: str) -> str:
        """Encrypt a configuration value"""
        salt = os.urandom(16)
        key = self.generate_key(password, salt)
        f = Fernet(key)
        encrypted = f.encrypt(value.encode())
        return base64.urlsafe_b64encode(salt + encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str, password: str) -> str:
        """Decrypt a configuration value"""
        try:
            data = base64.urlsafe_b64decode(encrypted_value.encode())
            salt = data[:16]
            encrypted = data[16:]
            key = self.generate_key(password, salt)
            f = Fernet(key)
            return f.decrypt(encrypted).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {str(e)}")
    
    def save_encrypted_config(self, password: str, output_file: str = "config.enc"):
        """Save encrypted configuration to a file"""
        encrypted_config = {}
        for key, value in self.config.items():
            if value:
                encrypted_config[key] = self.encrypt_value(value, password)
        
        with open(output_file, "w") as f:
            for key, value in encrypted_config.items():
                f.write(f"{key}={value}\n")
    
    def load_encrypted_config(self, password: str, input_file: str = "config.enc"):
        """Load encrypted configuration from a file"""
        if not os.path.exists(input_file):
            return
        
        with open(input_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    try:
                        decrypted_value = self.decrypt_value(value, password)
                        self.config[key] = decrypted_value
                    except ValueError as e:
                        print(f"Warning: Could not decrypt {key}: {str(e)}")
    
    def validate_config(self) -> bool:
        """Validate that all required configuration values are present"""
        required_keys = ["openai_api_key", "supabase_url", "supabase_key"]
        missing_keys = [key for key in required_keys if not self.get(key)]
        
        if missing_keys:
            print(f"Missing required configuration: {', '.join(missing_keys)}")
            return False
        return True 