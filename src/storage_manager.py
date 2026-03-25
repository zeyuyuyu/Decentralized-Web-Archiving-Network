import os
import shutil
import hashlib
import requests

from typing import List

class StorageManager:
    def __init__(self, data_dir: str, node_urls: List[str]):
        self.data_dir = data_dir
        self.node_urls = node_urls

    def store_content(self, content: bytes) -> str:
        """
        Stores the given content in the local data directory and replicates it across the decentralized network.
        Returns the content hash.
        """
        content_hash = self._calculate_hash(content)
        file_path = os.path.join(self.data_dir, content_hash)

        # Store content locally
        with open(file_path, 'wb') as f:
            f.write(content)

        # Replicate content across the decentralized network
        self._replicate_content(content, content_hash)

        return content_hash

    def retrieve_content(self, content_hash: str) -> bytes:
        """
        Retrieves the content with the given hash from the local data directory or the decentralized network.
        """
        file_path = os.path.join(self.data_dir, content_hash)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()

        # Fetch content from the decentralized network
        for node_url in self.node_urls:
            try:
                response = requests.get(f'{node_url}/content/{content_hash}')
                response.raise_for_status()
                content = response.content
                self._store_locally(content, content_hash)
                return content
            except requests.exceptions.RequestException:
                continue

        raise FileNotFoundError(f'Content with hash {content_hash} not found')

    def _calculate_hash(self, content: bytes) -> str:
        """
        Calculates the SHA-256 hash of the given content.
        """
        return hashlib.sha256(content).hexdigest()

    def _replicate_content(self, content: bytes, content_hash: str):
        """
        Replicates the given content across the decentralized network.
        """
        for node_url in self.node_urls:
            try:
                requests.post(f'{node_url}/content', data=content, headers={'X-Content-Hash': content_hash})
            except requests.exceptions.RequestException:
                continue

    def _store_locally(self, content: bytes, content_hash: str):
        """
        Stores the given content locally with the specified hash.
        """
        file_path = os.path.join(self.data_dir, content_hash)
        with open(file_path, 'wb') as f:
            f.write(content)
