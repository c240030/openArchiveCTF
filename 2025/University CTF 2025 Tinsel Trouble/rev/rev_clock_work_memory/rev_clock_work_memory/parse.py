def main():
    key = b"TOCK"

    encrypted_bytes = [
        0x1C,
        0x1B,
        0x01,
        0x30,
        0x23,
        0x7B,
        0x30,
        0x26,
        0x0B,
        0x3D,
        0x70,
        0x3D,
        0x0B,
        0x7E,
        0x30,
        0x14,
        0x37,
        0x7F,
        0x73,
        0x27,
        0x75,
        0x6E,
        0x3E,
    ]

    flag = ""
    for i, byte in enumerate(encrypted_bytes):
        flag += chr(byte ^ key[i % len(key)])

    print(flag)


if __name__ == "__main__":
    main()
