# 3AM Socket Solver

This solver connects to the TCP challenge, recovers the ECDSA private key from masked nonces using Z3, reconstructs the dataset parameters via HKDF(MK), extracts exact `t` values, solves for `(Kx, r)` using division polynomials over the finite field, and decrypts the flag.

## Run (Windows PowerShell)

```powershell
# From this folder
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python solve.py
```

If raw TCP fails on port 443, the solver auto-falls back to TLS.

## Notes
- Uses Z3 to model the masked nonce leak: `a_i*d - 2^36*α_i - 2^140*β_i - N*e_i = c_i'` with `0 ≤ α_i,β_i < 2^24`.
- Reproduces server’s HKDF selection rule: pick first `(λ,μ,ν)` such that `(ν·μ − λ) ≠ 0 (mod p)`.
- Inverts Möbius via `t = (μ − y0) / (y0·ν − λ)` with `y0 = (y − beta) mod p`.
- Recovers `Kx` by solving `x(2P) − x(3P) = T2 − T3 (mod p)` using division polynomials and SymPy over GF(p), then recovers `r = T2 − x(2P)` and verifies with `5P`.