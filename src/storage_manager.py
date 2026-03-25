import os
import shutil
import hashlib
import requests

class StorageManager:
    def __init__(self, node_list, replication_factor=3):
        self.node_list = node_list
        self.replication_factor = replication_factor

    def store_file(self, file_path):
        file_hash = self.calculate_file_hash(file_path)
        file_data = self.read_file(file_path)

        # Replicate the file across multiple nodes
        for i in range(self.replication_factor):
            node_index = i % len(self.node_list)
            node_url = self.node_list[node_index]
            self.upload_to_node(node_url, file_hash, file_data)

        return file_hash

    def retrieve_file(self, file_hash):
        # Retrieve the file from multiple nodes and compare the hashes
        for node_url in self.node_list:
            file_data = self.download_from_node(node_url, file_hash)
            if self.validate_file_hash(file_data, file_hash):
                return file_data

        raise Exception(f'Unable to retrieve file with hash: {file_hash}')

    def calculate_file_hash(self, file_path):
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()

    def read_file(self, file_path):
        with open(file_path, 'rb') as f:
            return f.read()

    def upload_to_node(self, node_url, file_hash, file_data):
        response = requests.post(f'{node_url}/store', json={'hash': file_hash, 'data': file_data.decode()})
        response.raise_for_status()

    def download_from_node(self, node_url, file_hash):
        response = requests.get(f'{node_url}/retrieve/{file_hash}')
        response.raise_for_status()
        return response.content.encode()

    def validate_file_hash(self, file_data, expected_hash):
        actual_hash = hashlib.sha256(file_data).hexdigest()
        return actual_hash == expected_hash
