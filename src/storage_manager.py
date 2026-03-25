import ipfshttpclient
from pathlib import Path
from typing import Optional, Dict
import hashlib
import json

class StorageManager:
    def __init__(self, ipfs_host: str = '/ip4/127.0.0.1/tcp/5001'):
        """Initialize storage manager with IPFS connection"""
        self.ipfs = ipfshttpclient.connect(ipfs_host)
        self.content_index: Dict[str, str] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load content index from disk if exists"""
        index_path = Path('content_index.json')
        if index_path.exists():
            with open(index_path, 'r') as f:
                self.content_index = json.load(f)

    def _save_index(self) -> None:
        """Save content index to disk"""
        with open('content_index.json', 'w') as f:
            json.dump(self.content_index, f)

    def store_content(self, content: str) -> str:
        """Store content in IPFS and return CID"""
        # Calculate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        # Check if already stored
        if content_hash in self.content_index:
            return self.content_index[content_hash]

        # Add to IPFS
        result = self.ipfs.add_str(content)
        cid = result['Hash']

        # Update index
        self.content_index[content_hash] = cid
        self._save_index()

        return cid

    def retrieve_content(self, cid: str) -> Optional[str]:
        """Retrieve content from IPFS by CID"""
        try:
            content = self.ipfs.cat(cid).decode('utf-8')
            return content
        except Exception as e:
            print(f'Error retrieving content: {e}')
            return None

    def pin_content(self, cid: str) -> bool:
        """Pin content to ensure persistence"""
        try:
            self.ipfs.pin.add(cid)
            return True
        except Exception as e:
            print(f'Error pinning content: {e}')
            return False

    def get_content_size(self, cid: str) -> Optional[int]:
        """Get size of stored content in bytes"""
        try:
            stats = self.ipfs.files.stat(f'/ipfs/{cid}')
            return stats['Size']
        except Exception as e:
            print(f'Error getting content size: {e}')
            return None

    def close(self) -> None:
        """Close IPFS connection"""
        self.ipfs.close()
