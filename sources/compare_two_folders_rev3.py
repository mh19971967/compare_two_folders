import hashlib
import os
# import sys
import datetime


def get_file_hash(def_file_path):
    with open(def_file_path, "rb") as f:
        file_data = f.read()
        return hashlib.sha512(file_data).hexdigest()


def sha512_hash(def_filename):
    """Calculate the SHA512 hash of a file."""
    sha512 = hashlib.sha512()
    with open(def_filename, "rb") as f:
        while True:
            if data := f.read(4096):
                sha512.update(data)
            else:
                break
    return sha512.hexdigest()


def compare_files(def_file1, def_file2):
    # Get file status
    file1_stat = os.stat(def_file1)
    file2_stat = os.stat(def_file2)

    # Check file size
    if file1_stat.st_size != file2_stat.st_size:
        return "file_size", str(file1_stat.st_size), str(file2_stat.st_size)

    # Check modification time
    if file1_stat.st_mtime != file2_stat.st_mtime:
        return "file_modification_time", \
            str(datetime.datetime.fromtimestamp(file1_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')), \
            str(datetime.datetime.fromtimestamp(file2_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'))

    # Check file hash
    file1_hash = sha512_hash(def_file1)
    file2_hash = sha512_hash(def_file2)
    if file1_hash != file2_hash:
        return "file_hash", str(file1_hash), str(file2_hash)

    # Check bitwise comparison
    with open(def_file1, "rb") as f1, open(def_file2, "rb") as f2:
        while True:
            b1 = f1.read(4096)
            b2 = f2.read(4096)
            if b1 != b2:
                return "file_bit", str(b1), str(b2)
            if not b1:
                break
    return None, None, None


def compare_folders(def_folder1, def_folder2, def_exclude_files=None, def_exclude_extensions=None):
    # Store the files in each folder
    files1 = {}
    files2 = {}
    for root, dirs, files in os.walk(def_folder1):
        for file in files:
            # Skip excluded files
            if def_exclude_files and file in def_exclude_files:
                continue
            # Skip excluded file extensions
            if def_exclude_extensions and os.path.splitext(file)[1].lower() in def_exclude_extensions:
                continue
            file_path = os.path.join(root, file)
            files1[file_path[len(def_folder1) + 1:]] = file_path
    for root, dirs, files in os.walk(def_folder2):
        for file in files:
            # Skip excluded files
            if def_exclude_files and file in def_exclude_files:
                continue
            # Skip excluded file extensions
            if def_exclude_extensions and os.path.splitext(file)[1].lower() in def_exclude_extensions:
                continue
            file_path = os.path.join(root, file)
            files2[file_path[len(def_folder2) + 1:]] = file_path
    # Check for missing files
    missing_files1 = set(files1.keys()).difference(set(files2.keys()))
    missing_files2 = set(files2.keys()).difference(set(files1.keys()))
    for file in missing_files1:
        print(f"File missing: {def_folder2}/{file}.")
    for file in missing_files2:
        print(f"File missing: {def_folder1}/{file}.")
    # Compare files
    for file in set(files1.keys()).intersection(set(files2.keys())):
        file1 = files1[file]
        file2 = files2[file]
        diff_type, file1_data, file2_data = compare_files(file1, file2)
        if diff_type is not None:
            print(f"File differs: {file}. Cause: {diff_type} (file1: {file1_data} <=> File2: {file2_data}).")


if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     print("Usage: python compare_folders.py folder1 folder2")
    #     sys.exit(1)
    # folder1 = sys.argv[1]
    # folder2 = sys.argv[2]

    folder1 = "/Users/mh/temp/test1"
    folder2 = "/Users/mh/temp/test2"
    #folder1 = "/Users/mh/temp/01 - Januar"
    #folder2 = "/Users/mh/temp/02 - Januar"

    # Optional: specify a list of files to exclude
    exclude_files = [".DS_Store"]

    # Optional: specify a list of file extensions to exclude
    exclude_extensions = [".log"]

    compare_folders(folder1, folder2, exclude_files, exclude_extensions)
