# VSD Internship — VLSI System Design

> A hands-on internship journey through VLSI design, RISC-V toolchains, and digital systems.

---

## Table of Contents

| # | Task | Description |
|---|------|-------------|
| 1 | [Task 1](#task-1-risc-v-toolchain-setup--c-compilation) | Compile C code using GCC and the RISC-V GNU Toolchain |
| 2 | [Task 2](#task-2-spike-simulation-of-the-compiled-c-code) | Spike simulation of RISC-V assembly code and observation |
| 3 | [Task 3](#task-3-risc-v-reference-design-bring-up) | Use the VSD Codespace to run a pre-built RISC-V + FPGA environment and replicate the toolchain locally |

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

## Task 2: Spike Simulation of the compiled C code

> This task is split into two parts. **Part A** uses the `sum1ton` program from Task 1. **Part B** introduces a new Fibonacci series program and repeats the same compilation and simulation workflow.

**Objective:** Simulate the C code compiled using RISC-V GNU Toolchain using Spike, a RISC-V simulator, and observe the output. Along with that, also use debug tools in spike. 

---

### Step 1 — Install dependencies and Spike

First, install all dependencies : 
```bash
sudo dnf install -y gcc-c++ make dtc libmpc-devel mpfr-devel gmp-devel
```
Next, clone the github repository of Spike: 
```bash
git clone https://github.com/riscv-software-src/riscv-isa-sim.git
cd riscv-isa-sim
```
Now, build and install Spike: 
```bash
mkdir build
cd build
../configure --host=riscv64-unknown-linux-gnu --prefix=/usr/local
make -j$(nproc)
sudo make install
```
Verify installation of Spike:

```bash
spike --help
```

A help menu should open if you have installed it correctly.

---

### Step 2 — Install RISC-V proxy kernel

```bash
cd ~
git clone https://github.com/riscv-software-src/riscv-pk.git
cd riscv-pk
mkdir build
cd build
../configure --host=riscv64-unknown-linux-gnu --prefix=/usr/local
make -j$(nproc)
sudo make install
```
Set a symlink to pk so we do not have to type an absolute path every single time.
```bash
sudo ln -s /usr/local/riscv64-unknown-linux-gnu/bin/pk /usr/local/bin/pk
```

---

### Step 3 — Compiling the program using gcc and RISC-V toolchain

**Using GCC:**

```bash
gcc sum1ton.c
./a.out
```

**Expected output:**
```
Sum of numbers from 1 to 100 is 5050
```
**Using RISC-V GNU Toolchain:**

```bash
riscv64-unknown-linux-gnu-gcc -march=rv64g -mabi=lp64d -static -o sum1ton.o sum1ton.c
spike $(which pk) sum1ton.o
```
Observe that the outputs will be same for both GCC and RISC-V toolchain.
![Compilation using GCC and RISC-V toolchain](images/task2/a.png)

---

### Step 4 — Using the debugger in Spike

To debug a program using spike, first we need to look at the object dump of the program.
```bash
riscv64-unknown-linux-gnu-objdump -d sum1ton.o | less
```
![Object dump](images/task2/b.png)
Now, use spike debugger to debug the program.
```bash
spike -d $(which pk) sum1ton.o
```
If we look at the object dump of the program, main function starts at address 10340. So when we start debug, we run the program counter until that address and then we look at individual registers to find out a bug if there is any.
```
0000000000010340 <main>:
   10340:       0004f537                lui     a0,0x4f
   10344:       00001637                lui     a2,0x1
   10348:       ff010113                addi    sp,sp,-16
   1034c:       3ba60613                addi    a2,a2,954 # 13ba <__libc_dlerror_result+0x1372>
   10350:       68850513                addi    a0,a0,1672 # 4f688 <__rseq_flags+0x4>
   10354:       06400593                li      a1,100
   10358:       00113423                sd      ra,8(sp)
   1035c:       181000ef                jal     10cdc <_IO_printf>
   10360:       00813083                ld      ra,8(sp)
   10364:       00000513                li      a0,0
   10368:       01010113                addi    sp,sp,16
   1036c:       00008067                ret
```
In the image, we can see that I ran the Program counter from 0 to 10340. Then checked a0. The reg value has not been updated yet. To move forward you press enter and on each step after the PC ticks, we can check and see how the register values are changing. 
![Spike debugger](images/task2/c.png)


---

## Task 2 — Part B: Fibonacci Series

**Objective:** Repeat the Spike simulation workflow with a new C program that generates the Fibonacci series. Observe that both GCC (host) and the RISC-V toolchain produce identical output, and use the Spike debugger to step through the compiled binary.

---

### Step 1 — Write the C Program

Create a file `fibonacci.c`:

```c
#include <stdio.h>

int main() {

    int n = 10, first = 0, second = 1, next;

    printf("Fibonacci Series: ");

    for (int i = 0; i < n; i++)
    {
        if (i <= 1)
            next = i;
        else
        {
            next = first + second;
            first = second;
            second = next;
        }

        printf("%d ", next);
    }
    printf("\n");
}
```

---

### Step 2 — Compile and Run (GCC & RISC-V Toolchain)

**Using GCC:**

```bash
gcc fibonacci.c
./a.out
```

**Expected output:**
```
Fibonacci Series: 0 1 1 2 3 5 8 13 21 34
```

**Using RISC-V GNU Toolchain:**

```bash
riscv64-unknown-linux-gnu-gcc -march=rv64g -mabi=lp64d -static -o fibonacci.o fibonacci.c
spike $(which pk) fibonacci.o
```

Observe that the outputs are identical for both GCC and the RISC-V toolchain.

![Compilation using GCC and RISC-V toolchain](images/task2/d.png)

---

### Step 3 — Inspect the Object Dump

Generate the disassembly of the compiled RISC-V binary:

```bash
riscv64-unknown-linux-gnu-objdump -d fibonacci.o | less
```

![Object dump of fibonacci.o](images/task2/e.png)

---

### Step 4 — Debug with Spike

Use the Spike debugger to step through the Fibonacci binary:

```bash
spike -d $(which pk) fibonacci.o
```

Locate the `main` function address from the object dump, then run the program counter up to that address and step through the registers to observe how the Fibonacci computation evolves.

![Spike debugger session for fibonacci.o](images/task2/f.png)

---

---

## Task 3: RISC-V Reference Design Bring-Up

**Objective:** Use the VSD-provided GitHub Codespace (a pre-configured cloud environment) to explore and run a complete RISC-V + FPGA reference design. Verify the pre-installed toolchain, compile and simulate a sample C program, build the RISC-V logo firmware, and then replicate the same toolchain setup on a local Fedora machine.

---

### Step 1 — Launch the VSD Codespace & Verify Tools

The VSD internship provides a GitHub Codespace with the RISC-V toolchain (SiFive GCC 8.3.0), Spike simulator, and Icarus Verilog pre-installed. After launching the codespace, verify all tools are present:

```bash
riscv64-unknown-elf-gcc --version
spike --help
iverilog -V
```

**Expected output:**
```
riscv64-unknown-elf-gcc (SiFive GCC 8.3.0-2019.08.0) 8.3.0
Spike RISC-V ISA Simulator 1.1.1-dev
```

![Tool verification in VSD Codespace](images/task3/Screenshot%20from%202026-06-15%2017-33-39.png)

---

### Step 2 — Compile and Run the Sample Program

The codespace ships with a `samples/` directory containing example programs. Navigate to it, compile `sum1ton.c` using the RISC-V cross-compiler, and simulate it with Spike:

```bash
ls
cd samples
ls
riscv64-unknown-elf-gcc -o sum1ton.o sum1ton.c
spike pk sum1ton.o
```

**Expected output:**
```
bbl loader
Sum from 1 to 9 is 45
```

![Compiling and running sum1ton in the Codespace](images/task3/Screenshot%20from%202026-06-15%2017-35-06.png)

---

### Step 3 — Install the Full FPGA + RISC-V Toolchain (Codespace)

The codespace also contains a `vsdfpga_labs/` directory with a setup script that installs the complete toolchain — general build tools, the FPGA synthesis stack (Yosys, nextpnr-ice40, IceStorm, Icarus Verilog), and the SiFive RISC-V GCC 8.3.0 cross-compiler:

```bash
# General dependencies
sudo apt-get install git vim autoconf automake autotools-dev curl libmpc-dev \
  libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool \
  patchutils bc zlib1g-dev libexpat1-dev gtkwave picocom -y

# FPGA toolchain (Yosys/NextPNR/IceStorm)
sudo apt-get install yosys nextpnr-ice40 icestorm iverilog -y

# RISC-V Toolchain (GCC 8.3.0)
cd ~
mkdir -p riscv_toolchain && cd riscv_toolchain
wget "https://static.dev.sifive.com/dev-tools/riscv64-unknown-elf-gcc-8.3.0-2019.08.0-x86_64-linux-ubuntu14.tar.gz"
tar -xvzf riscv64-unknown-elf-gcc-*.tar.gz
echo 'export PATH=$HOME/riscv_toolchain/riscv64-unknown-elf-gcc-8.3.0-2019.08.0-x86_64-linux-ubuntu14/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

![Running the setup script in the Codespace](images/task3/Screenshot%20from%202026-06-15%2017-38-37.png)

![Toolchain extraction and bram hex build](images/task3/Screenshot%20from%202026-06-15%2017-39-55.png)

---

### Step 4 — Build the RISC-V Logo Firmware

Navigate to the `basicRISCV/Firmware` directory inside `vsdfpga_labs` and build the reference firmware:

```bash
cd ~/vsdfpga_labs/basicRISCV/Firmware
# Review and close (Ctrl+X)
make riscv_logo.bram.hex
```

**Expected output:**
```
make: 'riscv_logo.bram.hex' is up to date.
```

![Building riscv_logo.bram.hex firmware](images/task3/Screenshot%20from%202026-06-15%2023-03-31.png)

---

### Step 5 — Run the RISC-V Logo Program with Spike

Compile the `riscv_logo.c` program and simulate it with Spike to confirm the firmware and toolchain are working end-to-end:

```bash
riscv64-unknown-elf-gcc -O0 -mabi=lp64 -march=rv64i -o riscv_logo.o riscv_logo.c
spike pk riscv_logo.o
```

A successful run prints the VSD ASCII art banner:

```
bbl loader
************************************************************
*  LEARN TO THINK LIKE A CHIP  *
*     VSDSQUADRON FPGA MINI     *
*BRINGS RISC-V TO VSD CLASSROOM*
************************************************************
```

![Spike simulation output showing VSD ASCII art logo](images/task3/Screenshot%20from%202026-06-15%2023-05-12.png)

---

### Step 6 — Replicate the Toolchain on a Local Fedora Machine

To run the same environment locally (outside the Codespace), install the equivalent packages on Fedora and download the SiFive toolchain tarball:

```bash
# Update package manager
sudo dnf update

# Install general build tools
sudo dnf install -y git vim autoconf automake autotools-dev curl \
  libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex \
  texinfo gperf libtool patchutils bc zlib1g-dev libexpat1-dev

# Install FPGA-specific tools
sudo dnf install -y yosys nextpnr-ice40 fpga-icestorm iverilog

# Install simulation and debugging tools
sudo dnf install -y gtkwave picocom
```

![Installing dependencies on local Fedora machine](images/task3/Screenshot%20from%202026-06-15%2023-06-49.png)

Then download and extract the SiFive RISC-V GCC 8.3.0 toolchain, and verify the installation:

```bash
mkdir -p ~/riscv_toolchain && cd ~/riscv_toolchain
wget "https://static.dev.sifive.com/dev-tools/riscv64-unknown-elf-gcc-8.3.0-2019.08.0-x86_64-linux-ubuntu14.tar.gz"
tar -xvzf riscv64-unknown-elf-gcc-*.tar.gz
export PATH=$HOME/riscv_toolchain/riscv64-unknown-elf-gcc-8.3.0-2019.08.0-x86_64-linux-ubuntu14/bin:$PATH
riscv64-unknown-elf-gcc --version
```

**Expected output:**
```
riscv64-unknown-elf-gcc (SiFive GCC 8.3.0-2019.08.0) 8.3.0
Copyright (C) 2018 Free Software Foundation, Inc.
```

![Local Fedora toolchain extraction and version verification](images/task3/Screenshot%20from%202026-06-15%2023-17-47.png)

> **Key Observation:** The VSD Codespace provides a ready-made reference environment. Replicating it locally confirms that the same SiFive GCC 8.3.0 toolchain and Spike workflow work identically on a local Fedora machine.

---

## Repository Structure

```
VSD-internship/
├── images/
│   ├── task1/          # Screenshots for Task 1
│   │   ├── a.png       # Toolchain binaries
│   │   ├── b.png       # GCC host compilation output
│   │   ├── c.png       # RISC-V -O1 disassembly
│   │   ├── d.png       # RISC-V -Ofast disassembly (part 1)
│   │   └── e.png       # RISC-V -Ofast disassembly (part 2)
│   ├── task2/          # Screenshots for Task 2
│   │   ├── a.png       # GCC and RISC-V toolchain compilation output (Part A)
│   │   ├── b.png       # Object dump of sum1ton.o (Part A)
│   │   ├── c.png       # Spike debugger session (Part A)
│   │   ├── d.png       # GCC and RISC-V toolchain compilation output (Part B)
│   │   ├── e.png       # Object dump of fibonacci.o (Part B)
│   │   └── f.png       # Spike debugger session for fibonacci.o (Part B)
│   └── task3/          # Screenshots for Task 3
│       ├── a.png       # Tool verification in VSD Codespace
│       ├── b.png       # Compiling and running sum1ton in the Codespace
│       ├── c.png       # Running the FPGA+RISC-V setup script
│       ├── d.png       # Toolchain extraction and bram hex build
│       ├── e.png       # Building riscv_logo.bram.hex
│       ├── f.png       # Spike simulation VSD ASCII art output
│       ├── g.png       # Installing dependencies on local Fedora
│       └── h.png       # Local Fedora toolchain verification
└── README.md
```

---

## Acknowledgements

- [VLSI System Design (VSD)](https://www.vlsisystemdesign.com/) — for the internship program and curriculum
- [RISC-V GNU Toolchain](https://github.com/riscv-collab/riscv-gnu-toolchain) — the open-source cross-compilation toolchain used throughout
- [SiFive](https://www.sifive.com/) — for the pre-built RISC-V GCC 8.3.0 toolchain distribution
