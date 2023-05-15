#!/usr/bin/python3

import subprocess
import sys
import hashlib
import os
import shutil

algos = ["sha256", "md5"]

def verify_archive(file_name, algorithm):
    base_name = file_name[13:-4]
    extract_dir = file_name[:-4]
    subprocess.run("mkdir {}".format(extract_dir).split(' '))
    subprocess.run("unzip {} -d {}".format(file_name, extract_dir).split(' '))
    os.chdir("./{}".format(extract_dir))    
    hash_file_name = "{}.{}".format(base_name, algorithm)
    with open("{}.txt".format(base_name), 'rb') as f:
        data = f.read()
        if algorithm == "sha256":
            hash_data = hashlib.sha256(data).hexdigest()
        elif algorithm == "md5":
            hash_data = hashlib.md5(data).hexdigest()
        else:
            print("This algorithm is not implemented")
            sys.exit(1)
        with open(hash_file_name, "r") as hf:
            if hf.read() != hash_data:
                print("Hash verification failed! The file has been modified and will not be extracted!")
                os.chdir("..")
                shutil.rmtree(extract_dir)
            else:
                print("Hash verification succeeded! The file is safe and will be extracted!")
                shutil.move(r"{}.txt".format(base_name), r"..")
                os.chdir("..")
                shutil.rmtree(extract_dir)

if __name__ == "__main__":
    f_name = sys.argv[1]
    algorithm = sys.argv[2]
    verify_archive(f_name, algorithm)