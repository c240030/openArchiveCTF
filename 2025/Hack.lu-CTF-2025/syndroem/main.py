#!/usr/bin/env bash
import os
import sys
import hashlib
from typing import List
sys.path.insert(0, 'mceliece')

from sage.all_cmdline import *   # import sage library
from parameters import parameters
from keygen import keygen_abstract
from fixedweight import fixedweight
from encode import encode

# target weight of the error weight
OMEGA = 4
# filename of the public key file
PK_FILENAME = "pk.txt"
# filename of the solution vector
SYNDROME_FILENAME = "syndrome.txt"
# length of the error vector
ERROR_LENGTH = 3488
# Base field
F2 = GF(2)


def randombits(r: int) -> List[int]:
    """
    :param r: number of bits to sample
    :return: list of ints mod 2
    """
    return [randrange(2) for _ in range(r)]



def read_matrix(P, 
                name: str,
                transposed: bool = True,
                challenge_format: bool = False):
    """
    :param P: params
    :param pk: filename
    """
    T = [[0 for _ in range(P.k)] for _ in range(P.n-P.k)]
    with open(name, 'r') as f:
        lines = [line.rstrip() for line in f]
        if challenge_format:
            if "#" in lines[-2]:
                lines = lines[:-2]
            lines = lines[7:]
        for i, line in enumerate(lines): 
            for j, c in enumerate(line):
                if transposed:
                    T[j][i] = int(c)
                else:
                    T[i][j] = int(c)


    T = matrix(F2, T)
    return T 



P = parameters("mceliece348864")
flag = os.getenv("FLAG", "")
seed_int = int(hashlib.sha256(flag.encode('utf-8')).hexdigest(), 16)
set_random_seed(seed_int)

T = read_matrix(P, PK_FILENAME)

t_org = P.t
P.t = OMEGA
e = fixedweight(randombits, P)
P.t = t_org

syndrome = encode(e, T, P)


def ask_solution():
    print("Enter the error:")
    try:
        data = str(input())
    except EOFError:
        return


    # check length 
    if len(data) != ERROR_LENGTH:
        print("wrong len")
        return
    
    data = [int(d) for d in data]

    # check if binary
    if not all([0 <= int(d) <= 1 for d in data]):
        print("not binary")
        return

    # check weight:
    weight = sum(data)
    if weight != OMEGA:
        print("wrong weight %d" % weight)
        return

    # compute syndrome
    check_syndrome = None
    try:
        data = vector(GF(2), data)
        check_syndrome = encode(e, T, P)
    except e as Exception:
        print(e)
        return
    
    # check syndrome
    for i in range(P.n-P.k):
        if syndrome[i] != check_syndrome[i]:
            print("wrong syndrome")
            return
    print(flag)
    exit(0)
    

def main():
    print("Welcome to Roberts Construction Service!")
    print("Your syndrome:")
    print(syndrome)
    while True:
        ask_solution()


if __name__ == '__main__':
   try:
        main()
   except EOFError:
       pass
   except KeyboardInterrupt:
       pass
