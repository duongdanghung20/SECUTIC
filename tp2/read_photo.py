#!/usr/bin/python3

import base64

with open("photo.base64", "r") as f:
    with open("photo.jpeg", "wb") as wf:
        z = base64.decode(f, wf)