```
─$ file chall 
chall: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=f8df5c43882ea2b977d56a3bc87d7443a05f21d5, for GNU/Linux 3.2.0, with debug_info, not stripped
```

```
└─$ strings chall              
/lib64/ld-linux-x86-64.so.2
mgUa
fgets
stdin
puts
__stack_chk_fail
strlen
strcspn
__libc_start_main
__cxa_finalize
memcmp
printf
strncmp
libc.so.6
GLIBC_2.4
GLIBC_2.2.5
GLIBC_2.34
_ITM_deregisterTMCloneTable
__gmon_start__
_ITM_registerTMCloneTable
nb 3
nb 3
PTE1
u+UH
CcaY
Enter flag: 
wrong :(
SECCON{
correct flag!
;*3$"
expand 32-byte kGCC: (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0
	buf
}	len
}	ok
;!	9
__off_t
_IO_read_ptr
_chain
flag_enc
__builtin_memcmp
size_t
_shortbuf
__uint8_t
_IO_buf_base
user_tag
key_bytes
_fileno
_IO_read_end
long int
_flags
_IO_buf_end
_cur_column
_IO_codecvt
_old_offset
__uint32_t
_IO_marker
stdin
__builtin_strlen
_freeres_buf
long unsigned int
_IO_write_ptr
short unsigned int
_IO_save_base
_lock
sigma_words
_flags2
_mode
fgets
__builtin_puts
__builtin_strcspn
_IO_write_end
message
_IO_lock_t
_IO_FILE
sigma_encrypt
_markers
unsigned char
short int
_IO_wide_data
_vtable_offset
GNU C17 13.3.0 -mtune=generic -march=x86-64 -g -O0 -fPIE -fno-plt -fasynchronous-unwind-tables -fstack-protector-strong -fstack-clash-protection -fcf-protection
__stack_chk_fail
__builtin_printf
__builtin_strncmp
__off64_t
_IO_read_base
_IO_save_end
__pad5
_unused2
_IO_backup_base
_freeres_list
main
_IO_write_base
/work/rev-2/recreate
main.c
/usr/include/x86_64-linux-gnu/bits
/usr/lib/gcc/x86_64-linux-gnu/13/include
/usr/include/x86_64-linux-gnu/bits/types
/usr/include
types.h
stdint-uintn.h
stddef.h
struct_FILE.h
stdio.h
string.h
config.h
<built-in>
Scrt1.o
__abi_tag
reloc.o
R_X86_64_SIZE32
crtstuff.c
deregister_tm_clones
__do_global_dtors_aux
completed.0
__do_global_dtors_aux_fini_array_entry
frame_dummy
__frame_dummy_init_array_entry
main.c
flag_enc
sigma_encrypt
__FRAME_END__
_DYNAMIC
__GNU_EH_FRAME_HDR
_GLOBAL_OFFSET_TABLE_
__libc_start_main@GLIBC_2.34
strncmp@GLIBC_2.2.5
_ITM_deregisterTMCloneTable
sigma_words
puts@GLIBC_2.2.5
stdin@GLIBC_2.2.5
_edata
_fini
strlen@GLIBC_2.2.5
__stack_chk_fail@GLIBC_2.4
printf@GLIBC_2.2.5
strcspn@GLIBC_2.2.5
memcmp@GLIBC_2.2.5
fgets@GLIBC_2.2.5
__data_start
__gmon_start__
__dso_handle
_IO_stdin_used
_end
__bss_start
main
__TMC_END__
_ITM_registerTMCloneTable
__cxa_finalize@GLIBC_2.2.5
_init
.symtab
.strtab
.shstrtab
.interp
.note.gnu.property
.note.gnu.build-id
.note.ABI-tag
.gnu.hash
.dynsym
.dynstr
.gnu.version
.gnu.version_r
.rela.dyn
.init
.plt
.plt.got
.text
.fini
.rodata
.eh_frame_hdr
.eh_frame
.init_array
.fini_array
.dynamic
.data
.bss
.comment
.debug_aranges
.debug_info
.debug_abbrev
.debug_line
.debug_str
.debug_line_str
```



