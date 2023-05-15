#!/usr/bin/python3

import subprocess
import sys
import os
from hash_file import hash_file

algos = ["sha256", "md5"]

def archive_hash_file(file_name, algorithm):
    hash_file(file_name, algorithm)
    base_name = file_name.rsplit(".", 1)[0]
    hash_file_name = "{}.{}".format(base_name, algorithm)
    archive_name = "archive_hash_{}.zip".format(base_name)
    subprocess.run("zip {} {} {}".format(archive_name, file_name, hash_file_name).split(' '))
    os.remove(file_name)
    os.remove(hash_file_name)

if __name__ == "__main__":
    f_name = sys.argv[1]
    algorithm = sys.argv[2]
    archive_hash_file(f_name, algorithm)
    base_name = f_name.rsplit(".", 1)[0]
    archive_name = "archive_hash_{}.zip".format(base_name)
    print("Hash file saved in: {}".format(archive_name))
    print("Done!")