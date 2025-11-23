import sys, time, csv
import numpy as np

EMPTY, TREE, BURN = 0, 1, 2

def step(grid, p, f):
    Nx, Ny = grid.shape
    new = grid.copy()
    # burning -> empty
    new[grid == BURN] = EMPTY
    # neighbors burning mask (Moore neighborhood)
    g = (grid == BURN)
    mask = np.zeros_like(g, dtype=bool)
    mask[:-1,:] |= g[1:,:]
    mask[1:,:]  |= g[:-1,:]
    mask[:,:-1] |= g[:,1:]
    mask[:,1:]  |= g[:,:-1]
    mask[:-1,:-1] |= g[1:,1:]
    mask[:-1,1:]  |= g[1:,:-1]
    mask[1:,:-1]  |= g[:-1,1:]
    mask[1:,1:]   |= g[:-1,:-1]

    tree_mask = (grid == TREE)
    catch = tree_mask & mask
    ignite = (np.random.random(size=grid.shape) < f) & tree_mask
    grow = (np.random.random(size=grid.shape) < p) & (grid == EMPTY)

    new[catch] = BURN
    new[ignite] = BURN
    new[grow] = TREE
    return new

def run(Nx=512, Ny=512, nsteps=500, p=0.01, f=0.0001, d0=0.6, out_csv='result_seq.csv'):
    grid = np.where(np.random.random((Nx,Ny)) < d0, TREE, EMPTY).astype(np.int8)
    burn_counts = []
    t0 = time.perf_counter()
    for s in range(nsteps):
        grid = step(grid, p, f)
        burn_counts.append(int((grid == BURN).sum()))
    t1 = time.perf_counter()
    total = t1 - t0
    print(f'[SEQ] Nx={Nx} Ny={Ny} steps={nsteps} total_time={total:.6f}s')
    with open(out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['mode','Nx','Ny','nsteps','p','f','total_time','avg_burn'])
        w.writerow(['seq', Nx, Ny, nsteps, p, f, f'{total:.6f}', sum(burn_counts)/len(burn_counts) if burn_counts else 0.0])

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 6:
        Nx = int(args[0]); Ny = int(args[1]); nsteps = int(args[2])
        p = float(args[3]); f = float(args[4]); d0 = float(args[5])
    else:
        Nx, Ny, nsteps, p, f, d0 = 512, 512, 500, 0.01, 0.0001, 0.6
    run(Nx,Ny,nsteps,p,f,d0)
