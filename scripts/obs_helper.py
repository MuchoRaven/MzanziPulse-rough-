"""
OBS Helper Module for FunctionGraph
Downloads/uploads SQLite database from Huawei Object Storage

WHY WE NEED THIS:
- FunctionGraph has no permanent storage
- We need to download DB, work with it, then upload it back
- This module handles that process cleanly
"""

import os
import tempfile
from obs import ObsClient  # Huawei OBS SDK

class OBSDatabaseManager:
    """
    Manages SQLite database stored in OBS
    
    CONCEPT: Think of this as a "librarian"
    - Downloads book (database) from shelf (OBS)
    - Lets you read/write in it
    - Returns book to shelf when done
    """
    
    def __init__(self, 
                 access_key_id: str,      # Your Huawei Cloud AK
                 secret_access_key: str,  # Your Huawei Cloud SK  
                 bucket_name: str,        # "mzansipulse-data"
                 region: str = 'af-south-1'):
        """
        Initialize connection to OBS
        
        WHY THESE PARAMETERS:
        - access_key_id: Proves you're authorized to access OBS
        - secret_access_key: Like a password for your account
        - bucket_name: Which storage container to use
        - region: Where the data is physically stored
        """
        self.bucket_name = bucket_name
        self.obs_client = ObsClient(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            server=f'https://obs.{region}.myhuaweicloud.com'
        )
    
    def download_database(self, object_key: str = 'mzansipulse.db') -> str:
        """
        Download database from OBS to temporary location
        
        WHAT HAPPENS:
        1. Creates temporary file on FunctionGraph's mini-computer
        2. Downloads database from OBS into that file
        3. Returns the file path
        
        Args:
            object_key: Name of database file in OBS
            
        Returns:
            str: Path to downloaded database file
            Example: '/tmp/mzansipulse_abc123.db'
        
        WHY TEMPORARY FILE:
        - FunctionGraph only has /tmp folder for temporary storage
        - File is deleted automatically when function finishes
        """
        # Create temporary file
        # tempfile.NamedTemporaryFile creates a unique filename
        # This prevents conflicts if multiple functions run at once
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,        # Don't delete immediately
            suffix='.db',        # SQLite file extension
            prefix='mzansipulse_'  # Prefix for easy identification
        )
        temp_path = temp_file.name
        temp_file.close()
        
        # Download from OBS
        print(f"📥 Downloading {object_key} from OBS bucket {self.bucket_name}...")
        
        resp = self.obs_client.getObject(
            bucketName=self.bucket_name,
            objectKey=object_key,
            downloadPath=temp_path  # Save directly to temp file
        )
        
        if resp.status < 300:  # HTTP 2xx = success
            print(f"✅ Database downloaded to: {temp_path}")
            return temp_path
        else:
            raise Exception(f"Failed to download database: {resp.errorMessage}")
    
    def upload_database(self, local_path: str, object_key: str = 'mzansipulse.db'):
        """
        Upload modified database back to OBS
        
        WHAT HAPPENS:
        1. Reads the local database file
        2. Uploads it to OBS (overwrites old version)
        3. Confirms success
        
        WHY WE NEED THIS:
        - After adding transactions, balances change
        - We need to save those changes back to cloud
        - Next function call will get updated data
        
        Args:
            local_path: Path to database on FunctionGraph
            object_key: Name to save as in OBS
        """
        print(f"📤 Uploading {local_path} to OBS bucket {self.bucket_name}...")
        
        resp = self.obs_client.putFile(
            bucketName=self.bucket_name,
            objectKey=object_key,
            file_path=local_path
        )
        
        if resp.status < 300:
            print(f"✅ Database uploaded successfully")
        else:
            raise Exception(f"Failed to upload database: {resp.errorMessage}")
    
    def cleanup(self, local_path: str):
        """
        Delete temporary database file
        
        WHY:
        - FunctionGraph has limited /tmp storage (512MB)
        - Clean up after ourselves to prevent filling it up
        
        Args:
            local_path: Path to temporary database file
        """
        if os.path.exists(local_path):
            os.remove(local_path)
            print(f"🗑️  Cleaned up temporary file: {local_path}")