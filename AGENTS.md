# AGENTS.md — CYBERBLITZ '26

Workstation guidelines and execution rules for agents operating on this machine.

NOTE: this is for a school CTF so help me find the flag.

all flags are in the format `CYBLTZ2026{}`

prefer to use uv for py scripts. if you're using a script for solution, write it in the same folder as the challenge directory

---

## 1. Workstation Profile & Architecture

- **Host OS**: macOS (Darwin `arm64`) on Apple Silicon M3, 24 GB unified memory.
- **Runtimes**:
  - Python: `/Users/adoreblvnk/.local/bin/python3` (Python 3.14)
  - Homebrew: `/opt/homebrew/bin/brew`
  - Container Engine: `/usr/local/bin/docker` (Docker 29 with Rosetta 2 x86_64 emulation)
- **External Linux Environment**: Debian VM (SSH / shared mount) or local Docker container.

---

## 2. Execution Policy: Host vs. Linux Boundary

Darwin cannot execute Linux ELF binaries or run Linux dynamic tracing tools (`strace`, `ltrace`, Linux `gdb`). Enforce the following execution boundaries:

### Run on macOS Host (Native ARM64 Speed)
Execute CPU-intensive scripts, static tooling, and remote networking natively on the host:
- **Cryptography & Math**: SageMath, Z3 solver, sympy, custom arithmetic.
- **AI / Machine Learning**: PyTorch scripts, adversarial sample generation, model inspection (`safetensors`, `fickling`). Utilize Apple Silicon unified memory / MPS where applicable.
- **Web Exploitation**: Fuzzers (`ffuf`), scanners (`sqlmap`), headless browser automation, HTTP/S proxy tools, and remote payload delivery.
- **Static Reverse Engineering**: Headless Ghidra decompilation, JADX (APK/DEX decompilation), disassemblers, and string/symbol extraction.
- **Forensics & Triage**: Wireshark/`tshark`, ExifTool, Volatility 3, PCAP dissection, and disk image carving (`binwalk`).
- **Remote Pwn Drivers**: Run Python exploit scripts (`from pwn import *; io = remote(host, port)`) directly on the host.

### Delegate to Linux (Docker or Debian VM)
Never attempt to execute Linux ELF binaries directly on Darwin. Route dynamic Linux analysis to Docker or the Debian VM:
- **Local Pwn & Dynamic Analysis**: ELF binary execution, GDB (`pwndbg`), heap inspection, stack canary/ASLR verification.
- **Binary Patching**: `patchelf` (glibc interpreter/rpath swapping) and `pwninit`.
- **System Call Tracing**: `strace`, `ltrace`, and seccomp filter inspection.
- **Kernel / eBPF / Low-level OS**: Custom Linux kernel modules, rootkits, eBPF programs, and QEMU system emulators.

#### Preferred Container Invocation (Docker with Rosetta)
When dynamic Linux execution is required, prefer a fast throwaway container mounted to the workspace over launching the full Debian GUI:
```bash
# x86_64 Linux container (uses Apple Rosetta 2 translation)
docker run --rm -it --platform linux/amd64 -v "$PWD":/pwd -w /pwd ubuntu:24.04 bash

# ARM64 Linux container
docker run --rm -it --platform linux/arm64 -v "$PWD":/pwd -w /pwd debian:bookworm bash
```

---

## 3. CTF Context & Knowledge Base

- **Competition Guide**: Consult `cyberblitz_2026_guide.md` for target author signatures, challenge predictions, and exploit templates (glibc 2.34+ FSOP, Pyjail escapes, .NET Native AOT, HTTP/3 forensics, and LLL lattice attacks).
- **Domain Skills**: Leverage skills in `.agents/skills/`:
  - `skill://solve-challenge`: Triage and category dispatch.
  - `skill://ctf-pwn`: Modern glibc heap, FSOP, ROP, seccomp bypass.
  - `skill://ctf-reverse`: Obfuscation, custom VMs, stripped Go, and .NET reversing.
  - `skill://ghidra-headless`: Headless Ghidra decompilation scripts.
  - `skill://android-reverse-engineering`: APK/AAR decompilation with JADX/Fernflower.
  - `skill://ctf-web`: Modern framework vulnerabilities, prototype pollution, CSS/XS-Leaks.
  - `skill://ctf-crypto`: LLL, lattice reduction, discrete log, and elliptic curve attacks.
  - `skill://ctf-ai-ml`: Prompt injection, model extraction, and pickle/safetensors payloads.
  - `skill://ctf-forensics`: QUIC/HTTP3 PCAPs, memory dumps, NTFS forensics.
  - `skill://ctf-misc`: Pyjails, bash jails, encodings, and esoteric languages.
  - `skill://ctf-writeup`: Submission-ready writeup generation.

---

## 4. Engineering Principles for Subagents

- **Surgical Changes**: Make minimal, verified edits. Do not touch unrelated challenge files.
- **Tool Grounding**: Use dedicated tools (`read`, `grep`, `glob`, `edit`) instead of invoking shell utilities (`cat`, `find`, `sed`).
- **No Hallucinated Execution**: If dynamic testing requires Linux syscalls or ELF binary execution, verify inside Docker or state the exact VM command rather than guessing execution outcomes on macOS.
