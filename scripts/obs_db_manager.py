"""
OBS Database Manager
Downloads SQLite database from Huawei OBS for production deployment
"""

import os
import time
from obs import ObsClient

class OBSDatabaseManager:
    """
    Manages SQLite database stored in OBS
    - Downloads DB from OBS on first run
    - Uses cached local copy for fast access
    - Syncs periodically to keep data fresh
    """
    
    def __init__(self, 
                 access_key_id: str,
                 secret_access_key: str,
                 bucket_name: str,
                 db_object_key: str = 'mzansipulse.db',
                 region: str = 'af-south-1'):
        """
        Initialize OBS connection
        
        Args:
            access_key_id: Your Huawei Cloud AK
            secret_access_key: Your Huawei Cloud SK
            bucket_name: OBS bucket name (e.g., 'mzansi-pulsedata')
            db_object_key: Database filename in OBS
            region: OBS region
        """
        self.bucket_name = bucket_name
        self.db_object_key = db_object_key
        self.local_db_path = os.path.join('..', 'database', 'mzansipulse_live.db')
        self.last_download = 0
        self.sync_interval = 300  # Sync every 5 minutes
        
        # Initialize OBS client
        self.obs_client = ObsClient(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            server=f'https://obs.{region}.myhuaweicloud.com'
        )
        
        print(f"🔗 Connected to OBS: {bucket_name}/{db_object_key}")
    
    def get_database_path(self) -> str:
        """
        Get path to database file
        Downloads from OBS if not cached or outdated
        
        Returns:
            str: Path to local database file
        """
        current_time = time.time()
        
        # Check if we need to download/refresh
        should_download = (
            not os.path.exists(self.local_db_path) or  # No local copy
            current_time - self.last_download > self.sync_interval  # Outdated
        )
        
        if should_download:
            self.download_from_obs()
        
        return self.local_db_path
    
    def download_from_obs(self):
        """Download database from OBS to local file"""
        try:
            print(f"📥 Downloading database from OBS...")
            
            # Download database
            resp = self.obs_client.getObject(
                bucketName=self.bucket_name,
                objectKey=self.db_object_key,
                downloadPath=self.local_db_path
            )
            
            if resp.status < 300:
                self.last_download = time.time()
                print(f"✅ Database downloaded successfully")
                print(f"   📍 Local path: {self.local_db_path}")
            else:
                print(f"❌ Download failed: {resp.errorMessage}")
                
                # Fallback to original database if download fails
                fallback_path = os.path.join('..', 'database', 'mzansipulse.db')
                if os.path.exists(fallback_path):
                    print(f"⚠️  Using fallback database: {fallback_path}")
                    self.local_db_path = fallback_path
                else:
                    raise Exception(f"Database download failed and no fallback available")
                
        except Exception as e:
            print(f"❌ Error downloading from OBS: {str(e)}")
            
            # Try to use existing local file
            if os.path.exists(self.local_db_path):
                print(f"⚠️  Using cached database (may be outdated)")
            else:
                # Last resort: use original database
                fallback_path = os.path.join('..', 'database', 'mzansipulse.db')
                if os.path.exists(fallback_path):
                    print(f"⚠️  Using original database: {fallback_path}")
                    self.local_db_path = fallback_path
                else:
                    raise Exception(f"No database available: {str(e)}")
    
    def upload_to_obs(self):
        """Upload local database back to OBS (for write operations)"""
        try:
            print(f"📤 Uploading database to OBS...")
            
            resp = self.obs_client.putFile(
                bucketName=self.bucket_name,
                objectKey=self.db_object_key,
                file_path=self.local_db_path
            )
            
            if resp.status < 300:
                print(f"✅ Database uploaded successfully")
            else:
                print(f"❌ Upload failed: {resp.errorMessage}")
                
        except Exception as e:
            print(f"❌ Error uploading to OBS: {str(e)}")
    
    def close(self):
        """Close OBS connection"""
        self.obs_client.close()


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    """
    Test OBS database connection
    """
    import sys
    
    print("=" * 80)
    print("🧪 Testing OBS Database Manager")
    print("=" * 80)
    
    # Check if credentials are provided
    if len(sys.argv) < 4:
        print("\n❌ Usage: python obs_db_manager.py <AK> <SK> <BUCKET_NAME>")
        print("\nExample:")
        print("  python obs_db_manager.py YOUR_AK YOUR_SK mzansi-pulsedata")
        sys.exit(1)
    
    ak = sys.argv[1]
    sk = sys.argv[2]
    bucket = sys.argv[3]
    
    # Create manager
    manager = OBSDatabaseManager(
        access_key_id=ak,
        secret_access_key=sk,
        bucket_name=bucket
    )
    
    # Test download
    db_path = manager.get_database_path()
    
    print(f"\n✅ Database ready at: {db_path}")
    
    # Test database
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM businesses")
    business_count = cursor.fetchone()[0]
    
    print(f"\n📊 Database Stats:")
    print(f"   • Users: {user_count}")
    print(f"   • Businesses: {business_count}")
    
    conn.close()
    manager.close()
    
    print("\n" + "=" * 80)
    print("✅ OBS Database Manager Test Complete!")
    print("=" * 80)