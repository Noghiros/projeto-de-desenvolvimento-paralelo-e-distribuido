import sys, subprocess, time

if len(sys.argv) < 9:
    print('Usage: python run_distributed_local.py <num_procs> <base_port> Nx Ny nsteps p f d0')
    sys.exit(1)

num_procs = int(sys.argv[1])
base_port = int(sys.argv[2])
Nx = int(sys.argv[3])
Ny = int(sys.argv[4])
nsteps = int(sys.argv[5])
p = float(sys.argv[6])
f = float(sys.argv[7])
d0 = float(sys.argv[8])

procs = []

for rank in range(num_procs):
    cmd = [
        'python', 'worker.py',
        str(rank), str(num_procs), str(base_port),
        str(Nx), str(Ny), str(nsteps),
        str(p), str(f), str(d0)
    ]
    print('Starting:', ' '.join(cmd))

    proc = subprocess.Popen(cmd, cwd='distribuido')  # <-- ALTERADO AQUI
    procs.append(proc)
    time.sleep(0.05)

for proc in procs:
    proc.wait()

print('All workers finished.')
