import os
import hashlib
import json
import argparse

HASH_FILE = 'file_hashes.json'

def compute_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def store_hashes(hashes):
    with open(HASH_FILE, 'w') as f:
        json.dump(hashes, f)

def load_hashes():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, 'r') as f:
            return json.load(f)
    return {}

def check_integrity(file_paths, reinitialize=False):
    stored_hashes = load_hashes()
    current_hashes = {}

    for file_path in file_paths:
        if os.path.isfile(file_path):
            current_hashes[file_path] = compute_hash(file_path)
        else:
            print(f"Skipping non-file: {file_path}")

    if reinitialize:
        store_hashes(current_hashes)
        print("Hashes re-initialized.")
        return

    discrepancies = []
    for file_path, current_hash in current_hashes.items():
        stored_hash = stored_hashes.get(file_path)
        if stored_hash and stored_hash != current_hash:
            discrepancies.append(file_path)

    if discrepancies:
        print("Discrepancies found in the following files:")
        for file_path in discrepancies:
            print(file_path)
    else:
        print("No discrepancies found.")

def main():
    parser = argparse.ArgumentParser(description="Check file integrity using SHA-256 hashes.")
    parser.add_argument('path', help="Directory or single log file to check.")
    parser.add_argument('--reinitialize', action='store_true', help="Reinitialize the stored hashes, overwriting any existing hash records.")
    args = parser.parse_args()

    if os.path.isdir(args.path):
        file_paths = [os.path.join(args.path, f) for f in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, f))]
    else:
        file_paths = [args.path]

    check_integrity(file_paths, args.reinitialize)