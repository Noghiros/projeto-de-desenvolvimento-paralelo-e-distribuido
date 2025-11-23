import sys, time, csv, threading
import numpy as np

EMPTY, TREE, BURN = 0,1,2

class Worker(threading.Thread):
    def __init__(self, tid, grid, new_grid, i0, i1, nsteps, p, f, barrier):
        super().__init__()
        self.tid = tid
        self.grid = grid
        self.new_grid = new_grid
        self.i0 = i0; self.i1 = i1
        self.nsteps = nsteps
        self.p = p; self.f = f
        self.barrier = barrier

    def run(self):
        Nx, Ny = self.grid.shape
        for step in range(self.nsteps):
            # compute for assigned rows
            for i in range(self.i0, self.i1):
                for j in range(Ny):
                    s = int(self.grid[i,j])
                    if s == BURN:
                        self.new_grid[i,j] = EMPTY
                    elif s == TREE:
                        burning = False
                        for di in (-1,0,1):
                            ni = i+di
                            if ni < 0 or ni >= Nx: continue
                            for dj in (-1,0,1):
                                nj = j+dj
                                if di==0 and dj==0: continue
                                if nj < 0 or nj >= Ny: continue
                                if self.grid[ni,nj] == BURN:
                                    burning = True; break
                            if burning: break
                        if burning:
                            self.new_grid[i,j] = BURN
                        elif np.random.random() < self.f:
                            self.new_grid[i,j] = BURN
                        else:
                            self.new_grid[i,j] = TREE
                    else:
                        if np.random.random() < self.p:
                            self.new_grid[i,j] = TREE
                        else:
                            self.new_grid[i,j] = EMPTY
            # sync
            self.barrier.wait()
            # wait for main thread to swap buffers
            self.barrier.wait()

def run(Nx=512, Ny=512, nsteps=300, nthreads=4, p=0.01, f=0.0001, d0=0.6, out_csv='result_threads.csv'):
    grid = np.where(np.random.random((Nx,Ny)) < d0, TREE, EMPTY).astype(np.int8)
    new_grid = grid.copy()
    barrier = threading.Barrier(nthreads+1)
    rows_per = Nx // nthreads
    threads = []
    for t in range(nthreads):
        i0 = t*rows_per
        i1 = Nx if t==nthreads-1 else (t+1)*rows_per
        th = Worker(t, grid, new_grid, i0, i1, nsteps, p, f, barrier)
        threads.append(th)
        th.start()
    t0 = time.perf_counter()
    for step in range(nsteps):
        barrier.wait()  # wait workers compute done
        # swap by copying contents to grid
        grid[:,:] = new_grid
        barrier.wait()  # let workers continue
    for th in threads:
        th.join()
    t1 = time.perf_counter()
    total = t1 - t0
    print(f'[THREADS] Nx={Nx} Ny={Ny} steps={nsteps} threads={nthreads} total_time={total:.6f}s')
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['mode','Nx','Ny','nsteps','threads','p','f','total_time'])
        w.writerow(['threads', Nx, Ny, nsteps, nthreads, p, f, f'{total:.6f}'])

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 7:
        Nx = int(args[0]); Ny = int(args[1]); nsteps = int(args[2]); nthreads = int(args[3])
        p = float(args[4]); f = float(args[5]); d0 = float(args[6])
    else:
        Nx, Ny, nsteps, nthreads, p, f, d0 = 512, 512, 300, 4, 0.01, 0.0001, 0.6
    run(Nx,Ny,nsteps,nthreads,p,f,d0)
