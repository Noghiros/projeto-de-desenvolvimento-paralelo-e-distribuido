# worker process for distributed forest-fire (simple TCP)
import sys, socket, time, numpy as np, csv
from forest_fire_simulacao import update_block

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError('Socket closed')
        data += chunk
    return data

def send_row(sock, row):
    b = row.tobytes()
    sock.sendall(b)

def recv_row(sock, Ny):
    data = recv_exact(sock, Ny)
    return np.frombuffer(data, dtype=np.int8).copy()

def worker_main(rank, num_procs, base_port, Nx, Ny, nsteps, p, f, d0):
    rows_per = Nx // num_procs
    i0 = rank * rows_per
    i1 = Nx if rank == num_procs-1 else (rank+1)*rows_per
    my_rows = i1 - i0
    grid = np.where(np.random.random((my_rows, Ny)) < d0, 1, 0).astype(np.int8)
    new_grid = grid.copy()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_port = base_port + rank
    server.bind(('127.0.0.1', my_port))
    server.listen(2)
    up_sock = None; down_sock = None
    accept_conn = {}
    def accept_once(name):
        conn, addr = server.accept()
        accept_conn[name] = conn
    if rank < num_procs - 1:
        import threading
        thr = threading.Thread(target=accept_once, args=('down',), daemon=True)
        thr.start()
    if rank > 0:
        up_port = base_port + (rank - 1)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                s.connect(('127.0.0.1', up_port))
                up_sock = s
                break
            except Exception:
                time.sleep(0.05)
    if rank < num_procs - 1:
        while 'down' not in accept_conn:
            time.sleep(0.01)
        down_sock = accept_conn['down']

    total_comm = 0.0; total_comp = 0.0
    for step in range(nsteps):
        top_row = grid[0,:]; bottom_row = grid[-1,:]
        s_comm = time.perf_counter()
        if up_sock:
            send_row(up_sock, top_row); topGhost = recv_row(up_sock, Ny)
        else:
            topGhost = None
        if down_sock:
            send_row(down_sock, bottom_row); bottomGhost = recv_row(down_sock, Ny)
        else:
            bottomGhost = None
        e_comm = time.perf_counter(); total_comm += (e_comm - s_comm)
        s_comp = time.perf_counter()
        new_grid = update_block(grid, topGhost, bottomGhost, p, f)
        e_comp = time.perf_counter(); total_comp += (e_comp - s_comp)
        grid[:,:] = new_grid
    if up_sock: up_sock.close()
    if down_sock: down_sock.close()
    server.close()
    print(f'[WORKER {rank}] comp={total_comp:.6f}s comm={total_comm:.6f}s total={total_comp+total_comm:.6f}s')
    with open(f'result_worker_{rank}.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['rank','rows','Nx_total','Ny','nsteps','p','f','comp_time','comm_time','total'])
        w.writerow([rank, f'{i0}-{i1-1}', Nx, Ny, nsteps, p, f, f'{total_comp:.6f}', f'{total_comm:.6f}', f'{total_comp+total_comm:.6f}'])

if __name__ == '__main__':
    if len(sys.argv) < 10:
        print('Usage: python worker.py <rank> <num_procs> <base_port> Nx Ny nsteps p f d0'); sys.exit(1)
    rank = int(sys.argv[1]); num_procs = int(sys.argv[2]); base_port = int(sys.argv[3])
    Nx = int(sys.argv[4]); Ny = int(sys.argv[5]); nsteps = int(sys.argv[6])
    p = float(sys.argv[7]); f = float(sys.argv[8]); d0 = float(sys.argv[9])
    worker_main(rank, num_procs, base_port, Nx, Ny, nsteps, p, f, d0)
