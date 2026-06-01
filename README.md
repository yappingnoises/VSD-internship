# VSD Internship — VLSI System Design

> A hands-on internship journey through VLSI design, RISC-V toolchains, and digital systems.

---

## Table of Contents

| # | Task | Description |
|---|------|-------------|
| 1 | [Task 1](#task-1-risc-v-toolchain-setup--c-compilation) | Compile C code using GCC and the RISC-V GNU Toolchain |

---

## Task 1: RISC-V Toolchain Setup & C Compilation

**Objective:** Install the RISC-V GNU cross-compiler toolchain and compile a C program for both the native host (x86-64) and the RISC-V target architecture. Observe the differences in assembly output between optimization levels.

---

### Step 1 — Install Dependencies

Install the required packages for building the cross-compiler on a Fedora/RHEL-based system:

```bash
sudo dnf install autoconf automake python3 libmpc-devel mpfr-devel gmp-devel \
  gawk bison flex texinfo patchutils gcc gcc-c++ zlib-devel expat-devel \
  libslirp-devel ncurses-devel
```

---

### Step 2 — Build the Linux Cross-Compiler

Choose an install prefix (a writable directory). Here, `~/riscv` is used:

```bash
./configure --prefix=~/riscv
make linux
echo 'export PATH=$PATH:~/riscv/bin' >> ~/.bashrc
source ~/.bashrc
```

> Note: This step takes a while — grab a coffee while it compiles!

---

### Step 3 — Verify the Installation

List the installed binaries:

```bash
cd ~/riscv/bin
ls
```

You should see a set of `riscv64-unknown-linux-gnu-*` tools:

![Installed RISC-V toolchain binaries](images/task1/a.png)

Confirm the cross-compiler version:

```bash
riscv64-unknown-linux-gnu-gcc --version
```

**Expected output:**
```
riscv64-unknown-linux-gnu-gcc (GCC) 14.1.0
Copyright (C) 2024 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

Also confirm the native GCC is available:

```bash
gcc -v
```

---

### Step 4 — Write the C Program

Create a file `sum1ton.c` — a simple program that computes the sum from 1 to *n*:

```c
#include <stdio.h>

int main()
{
    int i, sum = 0, n = 100;

    for (i = 1; i <= n; ++i)
    {
        sum += i;
    }

    printf("Sum of numbers from 1 to %d is %d\n", n, sum);
    return 0;
}
```

---

### Step 5 — Compile and Run on the Host (GCC)

Compile for the native host architecture and run:

```bash
gcc sum1ton.c -o sum1ton
./sum1ton
```

**Output:**
```
Sum of numbers from 1 to 100 is 5050
```

![GCC compilation and output](images/task1/b.png)

---

### Step 6 — Cross-Compile for RISC-V & Inspect Assembly

#### With `-O1` optimization:

```bash
riscv64-unknown-linux-gnu-gcc -O1 -mabi=lp64d -march=rv64g -o sum1ton.o sum1ton.c
riscv64-unknown-linux-gnu-objdump -d sum1ton.o | less
```

![Disassembly with -O1](images/task1/c.png)

#### With `-Ofast` optimization:

```bash
riscv64-unknown-linux-gnu-gcc -Ofast -mabi=lp64d -march=rv64g -o sum1ton.o sum1ton.c
riscv64-unknown-linux-gnu-objdump -d sum1ton.o | less
```

![Disassembly with -Ofast (1)](images/task1/d.png)
![Disassembly with -Ofast (2)](images/task1/e.png)

> **Key Observation:** With `-Ofast`, the compiler aggressively optimizes the loop — notice the significantly fewer instructions compared to `-O1`. The compiler may even evaluate the sum at compile time or use vectorization.

---

## Repository Structure

```
VSD-internship/
├── images/
│   └── task1/          # Screenshots for Task 1
│       ├── a.png       # Toolchain binaries
│       ├── b.png       # GCC host compilation output
│       ├── c.png       # RISC-V -O1 disassembly
│       ├── d.png       # RISC-V -Ofast disassembly (part 1)
│       └── e.png       # RISC-V -Ofast disassembly (part 2)
└── README.md
```

---

## Acknowledgements

- [VLSI System Design (VSD)](https://www.vlsisystemdesign.com/) — for the internship program and curriculum
- [RISC-V GNU Toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain) — the open-source cross-compilation toolchain used throughout
