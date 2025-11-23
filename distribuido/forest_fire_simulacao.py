# helper functions for workers: perform local updates on a block with ghost rows provided
import numpy as np
EMPTY, TREE, BURN = 0,1,2

def update_block(block, top_ghost, bottom_ghost, p, f):
    # block: array shape (rows, Ny)
    # top_ghost/bottom_ghost: arrays shape (Ny,) or None
    rows, Ny = block.shape
    # build padded
    if top_ghost is None:
        pad_top = np.full((1,Ny), EMPTY, dtype=np.int8)
    else:
        pad_top = top_ghost.reshape(1,Ny)
    if bottom_ghost is None:
        pad_bottom = np.full((1,Ny), EMPTY, dtype=np.int8)
    else:
        pad_bottom = bottom_ghost.reshape(1,Ny)
    padded = np.vstack([pad_top, block, pad_bottom])
    new = block.copy()
    for i in range(rows):
        for j in range(Ny):
            s = padded[i+1,j]
            if s == BURN:
                new[i,j] = EMPTY
            elif s == TREE:
                burning = False
                for di in (-1,0,1):
                    for dj in (-1,0,1):
                        if di==0 and dj==0: continue
                        ni = i+1+di; nj = j+dj
                        if nj < 0 or nj >= Ny: continue
                        if padded[ni,nj] == BURN:
                            burning = True; break
                    if burning: break
                if burning:
                    new[i,j] = BURN
                elif np.random.random() < f:
                    new[i,j] = BURN
                else:
                    new[i,j] = TREE
            else:
                if np.random.random() < p:
                    new[i,j] = TREE
                else:
                    new[i,j] = EMPTY
    return new
