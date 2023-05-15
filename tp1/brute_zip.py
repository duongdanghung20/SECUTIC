#!/usr/bin/python3

import subprocess

with open("corpus_francais.txt", "r") as f:
    corpus = f.readlines()
    corpus = [w.rstrip('\n') for w in corpus]

for w in corpus:
    command = "unzip -P %s -o archive.zip 2> /dev/stdout" %w
    command = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    (result, ignore) = command.communicate()
    print(w)
    result = result.decode()
    print("=========================")
    if ('incorrect' not in result) and ('error' not in result):
        print("Password is", w)
        print(result)
        break
