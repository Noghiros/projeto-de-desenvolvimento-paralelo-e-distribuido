import matplotlib.pyplot as plt, json
def plotar_graficos(fname='resultados.json'):
    with open(fname,'r') as f: dados = json.load(f)
    tamanhos = dados['tamanhos']
    tempos_seq = dados['sequencial']
    tempos_par = dados['paralelo']
    tempos_dist = dados['distribuido']
    plt.figure(); plt.plot(tamanhos, tempos_seq, marker='o'); plt.xlabel('Tamanho da matriz (N)'); plt.ylabel('Tempo (s)'); plt.title('Tempo - Sequencial'); plt.grid(); plt.savefig('tempo_sequencial.png')
    plt.figure()
    for k,v in tempos_par.items():
        plt.plot(tamanhos, v, marker='o', label=f'{k} threads')
    plt.xlabel('Tamanho da matriz (N)'); plt.ylabel('Tempo (s)'); plt.title('Tempo - Paralelo'); plt.legend(); plt.grid(); plt.savefig('tempo_paralelo.png')
    plt.figure()
    for k,v in tempos_dist.items():
        plt.plot(tamanhos, v, marker='o', label=f'{k} workers')
    plt.xlabel('Tamanho da matriz (N)'); plt.ylabel('Tempo (s)'); plt.title('Tempo - Distribuido'); plt.legend(); plt.grid(); plt.savefig('tempo_distribuido.png')
    print('Plots saved.')
if __name__=='__main__': plotar_graficos()