#!/usr/bin/python3

import subprocess

password_b64 = "U2VjdS5USUMK"

p1 = subprocess.Popen(["echo", password_b64], stdout=subprocess.PIPE)
p2 = subprocess.Popen("openssl base64 -d".split(), stdin=p1.stdout, stdout=subprocess.PIPE)

password = p2.stdout.read().decode()
print(password)


p3 = subprocess.Popen