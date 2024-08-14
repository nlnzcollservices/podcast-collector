import hashlib
import os

def get_md5(filename):
    """
    Calculates the MD5 checksum of a file.
    :param filename: Path to the file.
    :return: MD5 hash as a hexadecimal string.
    """
    m = hashlib.md5()
    with open(filename, 'rb') as file_to_check:
        while chunk := file_to_check.read(8192):
            m.update(chunk)
    return m.hexdigest()

def get_file_size(filename):
    """
    Retrieves the size of a file in bytes.
    :param filename: Path to the file.
    :return: Size of the file in bytes.
    """
    try:
        return os.path.getsize(filename)
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    filename = r"Y:\ndha\pre-deposit_prod\LD_working\podcasts\files\76 small rooms\20230901_Ep046_Award_Reward_FINAL.mp3"  # Replace with the actual file path
    md5_checksum = get_md5(filename)
    file_size = get_file_size(filename)

    if md5_checksum:
        print(f"MD5 Checksum: {md5_checksum}")
    else:
        print("Error calculating MD5 checksum.")

    if file_size is not None:
        print(f"File Size (bytes): {file_size}")
    else:
        print("File not found or unable to retrieve size.")
