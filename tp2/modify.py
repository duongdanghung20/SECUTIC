#!/usr/bin/python3

import subprocess
import sys
from bitstring import BitArray
import random

def modify(file_name):

    b = BitArray(bytes=open(file_name, 'rb').read())
    modify_pos = random.randrange(0, len(b.bin))
    b.set(int(1 - int(b.bin[modify_pos])), modify_pos)
    base_name, *extension = file_name.split(".")
    modify_1bit_fname = base_name + "_modify_1bit." + ".".join(extension)
    with open(modify_1bit_fname, "wb") as wf:
        wf.write(b.bytes)

    cmd_dgst = subprocess.Popen(["openssl", "dgst", "-sha256"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    cmd_dgst.stdin.write(bytes(file_name, 'utf-8'))
    cmd_dgst.stdin.close()

    out = cmd_dgst.stdout.read()
    print("Original file SHA256 hash: {}".format(out.decode()))

    cmd_dgst = subprocess.Popen(["openssl", "dgst", "-sha256"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    cmd_dgst.stdin.write(bytes(modify_1bit_fname, 'utf-8'))
    cmd_dgst.stdin.close()

    out = cmd_dgst.stdout.read()
    print("Modified 1-bit file SHA256 hash: {}".format(out.decode()))

if __name__ == "__main__":
    fname = sys.argv[1]
    modify(fname)