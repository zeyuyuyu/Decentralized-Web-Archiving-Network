import hashlib
import os

class StorageManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def store_data(self, data, filename):
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(data)
        return self.calculate_checksum(file_path)

    def retrieve_data(self, filename):
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'rb') as f:
            data = f.read()
        return data

    def calculate_checksum(self, file_path):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

    def verify_data_integrity(self):
        for filename in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, filename)
            expected_checksum = self.calculate_checksum(file_path)
            stored_checksum = self.retrieve_checksum(filename)
            if expected_checksum != stored_checksum:
                print(f'Data integrity violation detected for file: {filename}')
                return False
        return True

    def retrieve_checksum(self, filename):
        # Implement logic to retrieve the stored checksum for the given file
        pass
