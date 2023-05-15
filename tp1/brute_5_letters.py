#!/usr/bin/python3

import sys

letters = [chr(asc) for asc in range(ord('a'), ord('a') + 26)]

password = sys.argv[1]

def brute():
    for c1 in letters:
        for c2 in letters:
            for c3 in letters:
                for c4 in letters:
                    for c5 in letters:
                        guess = c1 + c2 + c3 + c4 + c5
                        print(guess)
                        if guess == password:
                            print("The password is: {}!!".format(guess))
                            return
if __name__ == "__main__":
    brute()
