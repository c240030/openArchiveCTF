import torch
import torch.nn.functional as F

from architecture import load_hf_gpt2_model, fill_mask

# ----------------------
# Utilities
# ----------------------

def top_k(wrapper, prompt_text: str, k: int = 10):
    logits = fill_mask(wrapper, prompt_text)
    probs = F.softmax(logits, dim=-1)
    top_k_probs, top_k_indices = torch.topk(probs, k)
    results = []
    for i in range(k):
        idx = top_k_indices[i].item()
        results.append((wrapper.itos[idx], top_k_probs[i].item(), idx))
    return results


def next_char_argmax(wrapper, prompt_text: str):
    logits = fill_mask(wrapper, prompt_text)
    idx = int(torch.argmax(logits).item())
    return wrapper.itos[idx]


def next_char_constrained(wrapper, prompt_text: str, allowed: set[str], k: int = 15):
    """Pick the highest-probability token within an allowed set."""
    logits = fill_mask(wrapper, prompt_text)
    probs = F.softmax(logits, dim=-1)
    top_k_probs, top_k_indices = torch.topk(probs, k)
    for i in range(k):
        idx = int(top_k_indices[i].item())
        tok = wrapper.itos[idx]
        if tok in allowed:
            return tok, float(top_k_probs[i].item())
    # fallback to absolute argmax if no allowed char found in top-k
    idx = int(torch.argmax(probs).item())
    return wrapper.itos[idx], float(probs[idx].item())


def ensure_in_window(s: str, max_len: int = 120) -> str:
    return s[-max_len:]


# ----------------------
# Guided Flag Recovery
# ----------------------

def recover_flag(debug: bool = True) -> str:
    wrapper = load_hf_gpt2_model()

    # 1) Inspect the first branching point
    seed = "password: "
    first_prompt = seed + "[MASK]"
    first_top = top_k(wrapper, first_prompt, k=10)

    if debug:
        print("Top-10 for 'password: [MASK]':")
        for i, (tok, p, _) in enumerate(first_top, 1):
            print(f"  {i:>2}. '{tok}'  prob={p:.4f}")
        print()

    # 2) Force the correct branch: choose 'A' if present in top-10
    pick_A = any(tok == 'A' for tok, _, _ in first_top)
    if not pick_A:
        # If 'A' isn't in top-10 (unexpected), still force it (we're following the intended path)
        if debug:
            print("'A' not in top-10; forcing 'A' due to challenge hint.")
    known = seed + "A"

    # 3) Steer toward the known prefix 'AI2025{'
    target_prefix = "I2025{"
    for ch in target_prefix:
        ctx = ensure_in_window(known)
        prompt = ctx + "[MASK]"
        # Choose exactly the next target char, but sanity-check it's not a vanishingly unlikely pick
        logits = fill_mask(wrapper, prompt)
        probs = F.softmax(logits, dim=-1)
        idxs = [i for i, s in wrapper.itos.items() if s == ch]
        if len(idxs) == 0:
            raise RuntimeError(f"Character '{ch}' not in vocab; cannot proceed.")
        p_ch = float(probs[idxs[0]].item())
        if debug:
            print(f"Steering to '{ch}'  (p={p_ch:.5f})")
        known += ch

    if debug:
        print("\nReached prefix:", known)

    # 4) Inside braces: beam search over constrained alphabet
    allowed_inside = set(list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"))
    allowed_all = allowed_inside | {'}'}  # include closing brace

    # Beam items: tuple(score_log, text)
    import math
    beam = [(0.0, known)]
    beam_width = 5
    max_steps = 128

    for step in range(max_steps):
        new_beam = []
        completed = []
        for score, cand in beam:
            if '}' in cand:
                completed.append((score, cand))
                continue
            ctx = ensure_in_window(cand)
            prompt = ctx + "[MASK]"
            logits = fill_mask(wrapper, prompt)
            probs = F.softmax(logits, dim=-1)

            # Collect top candidates among allowed tokens
            top_probs, top_idxs = torch.topk(probs, 50)
            for i in range(top_probs.numel()):
                idx = int(top_idxs[i].item())
                tok = wrapper.itos[idx]
                if tok not in allowed_all:
                    continue
                p = float(top_probs[i].item())
                if p <= 0:
                    continue
                bonus = 0.0
                if tok == '}':
                    # Encourage early closure
                    bonus = 2.0
                new_beam.append((score + math.log(p) + bonus, cand + tok))

        # If nothing expanded, stop
        if not new_beam and not completed:
            break

        # Keep best candidates
        new_beam.sort(key=lambda x: x[0], reverse=True)
        beam = new_beam[:beam_width]

        if debug:
            best_preview = [s for s,_ in zip([b[1] for b in beam], range(min(3, len(beam))))]
            print(f"Step {step+1}: best partials ->")
            for pv in best_preview:
                tail = pv[-60:]
                print("  ..." + tail)

        # If any completed in this round, prefer the best-closed
        if completed:
            completed.sort(key=lambda x: x[0], reverse=True)
            known = completed[0][1]
            break

    # Extract the flag if present
    start = known.find("AI2025{")
    end = known.find('}', start + 1) if start != -1 else -1
    if start != -1 and end != -1:
        flag = known[start:end+1]
        if debug:
            print("\nRecovered:", flag)
        return flag

    if debug:
        print("\nDid not find a complete flag; last known:")
        print(known)
    return ""


if __name__ == "__main__":
    try:
        flag = recover_flag(debug=True)
        if flag:
            print("\nFLAG:", flag)
        else:
            print("\nFlag not recovered. Try increasing k or relaxing constraints.")
    except Exception as e:
        print("Error:", e)
