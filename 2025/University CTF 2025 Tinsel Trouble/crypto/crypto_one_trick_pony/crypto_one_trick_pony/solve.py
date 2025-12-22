import hashlib
import json
import os
import subprocess
import sys

from pwn import *
from sympy.ntheory import discrete_log

# ================= CONFIGURATION =================
HOST = "154.57.164.80"
PORT = 31863

# Prime P (FROST_PRIME)
P = 0x1A66804D885939D7ACF3A4B413C9A24547B876E706913ADEC9684CC4A63AB0DFD2E0FD79F683DE06AD17774815DFC8375370EB3D0FB5DCE0019BD0632E7663A41

# ================= C++ CRACKER (LEGENDRE ALGO) =================
cpp_source = """
#include <iostream>
#include <vector>
#include <string>
#include <cstdlib>
#include <thread>
#include <atomic>
#include <mutex>
#include <algorithm>

std::atomic<bool> found(false);
std::mutex print_mutex;

int legendre(long long a, long long p) {
    int res = 1;
    a %= p;
    while (a != 0) {
        while (a % 2 == 0) {
            a /= 2;
            if (p % 8 == 3 || p % 8 == 5) res = -res;
        }
        std::swap(a, p);
        if (a % 4 == 3 && p % 4 == 3) res = -res;
        a %= p;
    }
    if (p == 1) return res;
    return 0;
}

void worker(long long start, long long end, long long original_p, const std::vector<int>& target, int thread_id) {
    int len = target.size();
    long long p = original_p;

    for (long long s = start; s < end; s++) {
        if (found.load()) return;

        long long current_seed = s;
        bool match = true;
        for (int i = 0; i < len; i++) {
            int leg = legendre(current_seed, p);
            int bit = (leg == 1) ? 1 : 0;

            if (bit != target[i]) { match = false; break; }

            // Mimic server logic: skip 0
            current_seed = (current_seed + 1) % p;
            if (current_seed == 0) current_seed += 1;
        }

        if (match) {
            found.store(true);
            std::lock_guard<std::mutex> lock(print_mutex);
            std::cout << s << std::endl;
            std::exit(0);
        }
    }
}

int main(int argc, char* argv[]) {
    if (argc < 3) return 1;
    long long p = std::atoll(argv[1]);
    std::string bits = argv[2];
    int len = bits.length();

    std::vector<int> target(len);
    for(int i=0; i<len; i++) target[i] = bits[i] - '0';

    unsigned int total_cores = std::thread::hardware_concurrency();
    if (total_cores == 0) total_cores = 4;
    // Leave some cores for the OS/Python
    unsigned int workers_count = (total_cores >= 4) ? total_cores - 2 : ((total_cores > 1) ? total_cores - 1 : 1);

    std::vector<std::thread> threads;
    long long range = p / workers_count;
    for (unsigned int i = 0; i < workers_count; i++) {
        long long start = 1 + i * range;
        long long end = (i == workers_count - 1) ? p : start + range;
        threads.emplace_back(worker, start, end, p, std::ref(target), i);
    }
    for (auto& t : threads) { if (t.joinable()) t.join(); }
    return 0;
}
"""


# ================= PYTHON LOGIC (FIXED STATE SYNC) =================
class TinselRNG_Solver:
    def __init__(self, prime, seed):
        self.holly_prime = prime
        self.sleigh_seed = seed

    def sparkle_bit(self):
        if self.sleigh_seed == 0:
            self.sleigh_seed += 1
        while True:
            shimmer = pow(
                self.sleigh_seed, (self.holly_prime - 1) // 2, self.holly_prime
            )
            yield int(shimmer == 1)
            self.sleigh_seed = (self.sleigh_seed + 1) % self.holly_prime
            if self.sleigh_seed == 0:
                self.sleigh_seed += 1

    def gather_sparkles(self, l):
        bits = ""
        # FIX: ACCURATE SERVER SIMULATION
        # The server uses enumerate() and breaks when index i == l.
        # This consumes one extra state from the generator (l+1 states consumed, l bits used).
        for i, b in enumerate(self.sparkle_bit()):
            if i == l:
                break
            bits += str(b)
        return bits


def compile_cpp():
    if not os.path.exists("cracker.exe") and not os.path.exists("cracker"):
        log.info("Compiling C++ cracker...")
        with open("cracker.cpp", "w", encoding="utf-8") as f:
            f.write(cpp_source)
        cmd = "g++ -O3 cracker.cpp -o cracker" + (".exe" if os.name == "nt" else "")
        os.system(cmd)


def get_seed_from_cpp(holly_prime, bits):
    exec_name = "cracker.exe" if os.name == "nt" else "./cracker"
    try:
        res = subprocess.check_output([exec_name, str(holly_prime), bits], text=True)
        lines = res.strip().splitlines()
        for line in reversed(lines):
            if line.isdigit():
                return int(line)
        return None
    except:
        return None


def attempt_exploit(target_length):
    io = None
    try:
        log.info(f"Trying length: {target_length}")
        io = remote(HOST, PORT, level="error")

        io.recvuntil(b"frostrng.holly_prime = ")
        holly_prime = int(io.recvline().strip())

        # 1. Get Signature
        io.recvuntil(b"> ")
        io.sendline(b"1")
        io.recvuntil(b"Whisper your message: ")
        msg = "TEST"
        io.sendline(msg.encode())
        resp = json.loads(io.recvline().strip())
        etch = int(resp["signature"])

        # 2. Solve DLP (Pohlig-Hellman)
        blizzard = hashlib.sha512(msg.encode()).digest()
        snowmark = int.from_bytes(blizzard, "big") % P
        lantern_key = discrete_log(P, etch, snowmark)

        # 3. Crack Seed
        recovered_bits = f"{lantern_key:0500b}"
        seed = get_seed_from_cpp(holly_prime, recovered_bits)

        if seed is None:
            return False, "Crack failed"

        # 4. Generate OTP (State Sync fixed in TinselRNG_Solver)
        rng = TinselRNG_Solver(holly_prime, seed)
        rng.gather_sparkles(500)  # Skip key bits (consumes 501 states internally)

        flag_bits = rng.gather_sparkles(target_length * 8)

        io.recvuntil(b"> ")
        io.sendline(b"2")
        io.recvuntil(b"(in bits): ")
        io.sendline(flag_bits.encode())

        response = io.recvline().strip().decode()
        io.close()

        if "fake_flag" in response:
            return False, response
        return True, response

    except Exception as e:
        if io:
            io.close()
        return False, str(e)


def main():
    compile_cpp()

    # Priority: 85 (Flag + \n), 84 (Exact), 83, 86
    priority = [85, 84, 83, 86]
    scan_list = priority + [i for i in range(75, 95) if i not in priority]

    log.info(f"Starting scan with lengths: {scan_list[:6]}...")

    for length in scan_list:
        success, result = attempt_exploit(length)
        if success:
            print("\n" + "=" * 50)
            log.success(f"FOUND CORRECT FLAG! (Length: {length})")
            log.success(f"CONTENT: {result}")
            print("=" * 50 + "\n")
            break
        else:
            log.failure(f"Length {length} failed.")

    # Cleanup
    try:
        if os.name == "nt":
            os.remove("cracker.exe")
        else:
            os.remove("cracker")
        os.remove("cracker.cpp")
    except:
        pass


if __name__ == "__main__":
    main()
