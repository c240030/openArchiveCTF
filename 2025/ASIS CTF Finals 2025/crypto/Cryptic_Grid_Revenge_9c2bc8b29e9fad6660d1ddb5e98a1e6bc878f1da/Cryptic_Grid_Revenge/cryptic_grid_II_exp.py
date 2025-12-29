#!/usr/bin/env python3


## Cryptic Grid II Crypto task writeup - ASIS CTF Final 2025
# factoreal@asis.sh
## The main idea is about "The 100 Prisoners Problem", for this please see: 
# https://www.youtube.com/watch?v=iSNsgj1OCLA

import re
import socket
import time

host = "127.0.0.1"
port = 12401
zzz = 0.1

MAXINSIGHT = 0b101010
SECRET_LEN = 0x40
while True:
	print("=" * 100)
	print("Another try ...")
	hope = True
	try:
		secret = [None] * SECRET_LEN
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.connect((host, port))
			time.sleep(zzz * 10)
			data = sock.recv(1 << 24).decode()
			print(data)
			matches = re.search(r"Focus pulse: (\d+)\n", data)
			shadow_byte = int(matches.group(1))
			print(f"{shadow_byte=}")

			for _ in range(SECRET_LEN):
				sock.sendall("r\n".encode())
				time.sleep(zzz)
				data = sock.recv(1 << 12).decode()
				# print(data)
				sock.sendall(f"{shadow_byte}\n".encode())
				time.sleep(zzz)
				data = sock.recv(1 << 12).decode()
				# print(data)
				matches = re.search(r"Reflection: (.+)\n", data)
				shadow_byte_enc = matches.group(1)
				print(shadow_byte_enc, end=" -> ")

				pointer = shadow_byte_enc
				for _ in range(MAXINSIGHT):
					sock.sendall("q\n".encode())
					time.sleep(zzz)
					data = sock.recv(1 << 12).decode()
					# print(data)
					sock.sendall(f"{pointer}\n".encode())
					time.sleep(zzz)
					data = sock.recv(1 << 12).decode()
					# print(data)
					sock.sendall(f"{-0x20}\n".encode())
					time.sleep(zzz)
					data = sock.recv(1 << 12).decode()
					# print(data)
					if "Attempts depleted" in data:
						hope = False
						break
					elif "ALIGNMENT FOUND" in data:
						matches = re.search(r"ALIGNMENT FOUND at (\d+)\n", data)
						secret[int(matches.group(1))] = shadow_byte
						matches = re.search(r"Focus pulse: (\d+)\n", data)
						shadow_byte = int(matches.group(1))
						print(f"{shadow_byte=}")
						break
					matches = re.search(r"Trace: (.+)\n", data)
					pointer = matches.group(1)
					print(pointer, end=" -> ")
				if not hope:
					break
				print(f"\n{secret=}")
			if None in secret:
				continue
			secret = bytes(secret).hex()
			print(f"{secret=}")
			sock.sendall("c\n".encode())
			time.sleep(zzz)
			data = sock.recv(1 << 12).decode()
			print(data)
			sock.sendall(f"{secret}\n".encode())
			time.sleep(zzz)
			data = sock.recv(1 << 12).decode()
			print(data)
			exit()
	except Exception as e:
		print(e)
import time


host = "127.0.0.1"
port = 12401
zzz = 0.1

MAXINSIGHT = 0b101010
SECRET_LEN = 0x40
while True:
	print("=" * 100)
	print("Another try ...")
	hope = True
	try:
		secret = [None] * SECRET_LEN
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.connect((host, port))
			time.sleep(zzz * 10)
			data = sock.recv(1 << 24).decode()
			print(data)
			matches = re.search(r"Focus pulse: (\d+)\n", data)
			shadow_byte = int(matches.group(1))
			print(f"{shadow_byte=}")

			for _ in range(SECRET_LEN):
				sock.sendall("r\n".encode())
				time.sleep(zzz)
				data = sock.recv(1 << 12).decode()
				sock.sendall(f"{shadow_byte}\n".encode())
				time.sleep(zzz)
				data = sock.recv(1 << 12).decode()
				matches = re.search(r"Reflection: (.+)\n", data)
				shadow_byte_enc = matches.group(1)
				print(shadow_byte_enc, end=" -> ")

				pointer = shadow_byte_enc
				for _ in range(MAXINSIGHT):
					sock.sendall("q\n".encode())
					time.sleep(zzz)
					data = sock.recv(1 << 12).decode()
					sock.sendall(f"{pointer}\n".encode())
					time.sleep(zzz)
					data = sock.recv(1 << 12).decode()
					sock.sendall(f"{-0x20}\n".encode())
					time.sleep(zzz)
					data = sock.recv(1 << 12).decode()
					if "Attempts depleted" in data:
						hope = False
						break
					elif "ALIGNMENT FOUND" in data:
						matches = re.search(r"ALIGNMENT FOUND at (\d+)\n", data)
						secret[int(matches.group(1))] = shadow_byte
						matches = re.search(r"Focus pulse: (\d+)\n", data)
						shadow_byte = int(matches.group(1))
						print(f"{shadow_byte=}")
						break
					matches = re.search(r"Trace: (.+)\n", data)
					pointer = matches.group(1)
					print(pointer, end=" -> ")
				if not hope:
					break
				print(f"\n{secret=}")
			if None in secret:
				continue
			secret = bytes(secret).hex()
			print(f"{secret=}")
			sock.sendall("c\n".encode())
			time.sleep(zzz)
			data = sock.recv(1 << 12).decode()
			print(data)
			sock.sendall(f"{secret}\n".encode())
			time.sleep(zzz)
			data = sock.recv(1 << 12).decode()
			print(data)
			exit()
	except Exception as e:
		print(e)