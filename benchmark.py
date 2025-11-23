import json, subprocess, time, os
sizes = [256, 512, 1024]
p = 0.01; f = 0.0001; d0 = 0.6; nsteps = 200
results = {'tamanhos': sizes, 'sequencial': [], 'paralelo': {}, 'distribuido': {}}
# seq
for N in sizes:
    cmd = ['python', 'sequencial/forest_fire_sequencial.py', str(N), str(N), str(nsteps), str(p), str(f), str(d0)]
    t0 = time.perf_counter(); subprocess.run(cmd); t1 = time.perf_counter()
    results['sequencial'].append(t1-t0)
# paralelo: 2 and 4 threads
for threads in [2,4]:
    arr = []
    for N in sizes:
        cmd = ['python', 'paralelo/forest_fire_paralelo.py', str(N), str(N), str(nsteps), str(threads), str(p), str(f), str(d0)]
        t0 = time.perf_counter(); subprocess.run(cmd); t1 = time.perf_counter()
        arr.append(t1-t0)
    results['paralelo'][str(threads)] = arr
# distribuido local: 2 and 4 workers (uses run_distributed_local)
for workers in [2,4]:
    arr = []
    for N in sizes:
        cmd = ['python', 'distribuido/run_distributed_local.py', str(workers), '9000', str(N), str(N), str(nsteps), str(p), str(f), str(d0)]
        t0 = time.perf_counter(); subprocess.run(cmd); t1 = time.perf_counter()
        arr.append(t1-t0)
    results['distribuido'][str(workers)] = arr
with open('resultados.json', 'w') as f: json.dump(results, f, indent=2)
print('Benchmark complete. Results in resultados.json')