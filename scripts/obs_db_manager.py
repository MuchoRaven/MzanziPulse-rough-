"""
OBS Database Manager
Smart sync: only downloads from OBS when local database is missing.
Preserves local transactions across restarts.
"""

import os
from obs import ObsClient


class OBSDatabaseManager:
    """
    Manages SQLite database stored in OBS with smart sync behavior:

    STARTUP:  Download from OBS only if local DB is missing.
              If local DB exists, use it as-is (preserves local transactions).

    RUNTIME:  All writes go to local DB. Call upload_to_obs() after changes.

    SHUTDOWN: upload_to_obs() backs up to OBS.
    """

    def __init__(self,
                 access_key_id: str,
                 secret_access_key: str,
                 bucket_name: str,
                 db_object_key: str = 'mzansipulse.db',
                 region: str = 'af-south-1'):
        """
        Initialize OBS connection.

        Args:
            access_key_id:   Huawei Cloud AK
            secret_access_key: Huawei Cloud SK
            bucket_name:     OBS bucket (e.g. 'mzansipulse-data')
            db_object_key:   Object key in OBS bucket
            region:          OBS region
        """
        self.bucket_name = bucket_name
        self.db_object_key = db_object_key
        # Canonical path — matches LOCAL_DB_PATH in auth_api.py
        self.local_db_path = os.path.join('..', 'database', 'mzansipulse.db')

        self.obs_client = ObsClient(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            server=f'https://obs.{region}.myhuaweicloud.com'
        )

        print(f"🔗 OBS connected: {bucket_name}/{db_object_key}")

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def get_database_path(self) -> str:
        """
        Return path to the local database file.

        Smart sync rules:
        - Local DB exists  → use it immediately, no OBS download
        - Local DB missing → download from OBS first
        """
        if os.path.exists(self.local_db_path):
            print(f"✅ Local database found — using existing data")
            print(f"   📍 {os.path.abspath(self.local_db_path)}")
        else:
            print(f"⚠️  Local database missing — downloading from OBS...")
            self.download_from_obs()

        return self.local_db_path

    def download_from_obs(self):
        """Download database from OBS to local path."""
        try:
            # Ensure the database directory exists
            os.makedirs(os.path.dirname(self.local_db_path), exist_ok=True)

            resp = self.obs_client.getObject(
                bucketName=self.bucket_name,
                objectKey=self.db_object_key,
                downloadPath=self.local_db_path
            )

            if resp.status < 300:
                print(f"✅ Database downloaded from OBS successfully")
                print(f"   📍 {os.path.abspath(self.local_db_path)}")
            else:
                raise Exception(f"OBS returned status {resp.status}: {resp.errorMessage}")

        except Exception as e:
            print(f"❌ Download from OBS failed: {e}")
            if os.path.exists(self.local_db_path):
                print(f"⚠️  Falling back to existing local database")
            else:
                raise Exception(
                    f"No local database available and OBS download failed: {e}"
                )

    def upload_to_obs(self) -> bool:
        """
        Upload local database to OBS.
        Called after write operations and on shutdown.

        Returns:
            True on success, False on failure.
        """
        try:
            if not os.path.exists(self.local_db_path):
                print(f"❌ Cannot upload — local database not found")
                return False

            resp = self.obs_client.putFile(
                bucketName=self.bucket_name,
                objectKey=self.db_object_key,
                file_path=self.local_db_path
            )

            if resp.status < 300:
                print(f"✅ Database backed up to OBS successfully")
                return True
            else:
                print(f"❌ OBS upload failed: {resp.errorMessage}")
                return False

        except Exception as e:
            print(f"❌ Error uploading to OBS: {e}")
            return False

    def close(self):
        """Close OBS connection."""
        self.obs_client.close()


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("🧪 Testing OBS Database Manager (Smart Sync)")
    print("=" * 70)

    if len(sys.argv) < 4:
        print("\n❌ Usage: python obs_db_manager.py <AK> <SK> <BUCKET>")
        sys.exit(1)

    ak, sk, bucket = sys.argv[1], sys.argv[2], sys.argv[3]

    manager = OBSDatabaseManager(
        access_key_id=ak,
        secret_access_key=sk,
        bucket_name=bucket
    )

    db_path = manager.get_database_path()
    print(f"\n✅ Database ready at: {db_path}")

    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    print(f"📊 Users in DB: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM cash_transactions")
    print(f"📊 Transactions in DB: {cursor.fetchone()[0]}")
    conn.close()

    manager.close()
    print("\n✅ Test complete!")
