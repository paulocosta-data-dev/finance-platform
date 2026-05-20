import hashlib
from pathlib import Path


def generate_file_hash(
    file_path: Path,
) -> str:

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while chunk := file.read(8192):

            sha256.update(chunk)

    return sha256.hexdigest()