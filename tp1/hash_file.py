#!/usr/bin/python3

import hashlib
import sys

def hash_file(file_name, algorithm):
    with open(file_name, 'rb') as f:
        data = f.read()
        if algorithm == "sha256":
            hash_data = hashlib.sha256(data).hexdigest()
        elif algorithm == "md5":
            hash_data = hashlib.md5(data).hexdigest()
        else:
            print("This algorithm is not implemented")
            sys.exit(1)
        base_name = file_name.rsplit(".", 1)[0]
        hash_file_name = "{}.{}".format(base_name, algorithm)
        with open(hash_file_name, "w") as hf:
            hf.write(hash_data)

if __name__ == "__main__":
    f_name = sys.argv[1]
    algorithm = sys.argv[2]
    hash_file(f_name, algorithm)
    base_name = f_name.rsplit(".", 1)[0]
    hash_file_name = "{}.{}".format(base_name, algorithm)
    print("Hash file saved in: {}".format(hash_file_name))
    print("Done!")