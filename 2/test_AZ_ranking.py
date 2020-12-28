


import pandas as pd
import numpy as np
from numba import jit
from matplotlib import pyplot as plt


N = 30
N_score = np.array(score*N)
assign_score = np.random.choice(N_score, N*4, replace=False)
ind_score = np.zeros(N)
for j in range(N):
    ind_score[j] = assign_score[j*4:j*4+4].mean()

ind_score_ranked = ind_score[ind_score.argsort()]


@jit
def simulation(N, N_simu, rank):
    score = [1,2,3,4]
    N_score = np.array(score*N)
    result = np.zeros(N_simu)
    for i in range(N_simu):
        assign_score = np.random.choice(N_score, N*4, replace=False)
        ind_score = np.zeros(N)
        for j in range(N):
            ind_score[j] = assign_score[j*4:j*4+4].mean()
        ind_score_ranked = ind_score[ind_score.argsort()]
        result[i] = ind_score_ranked[-rank]

    return (result)


def plot_rank(rank = 1):


    aa1 = simulation(3, 100000, rank)
    aa2 = simulation(4, 100000, rank)
    aa3 = simulation(6, 100000, rank)
    aa4 = simulation(7, 100000, rank)
    aa5 = simulation(30, 100000, rank)
    
    
    ax = plt.subplot(511)
    ax.set_autoscaley_on(False)
    
    plt.hist(aa1, histtype='stepfilled', bins=30, alpha=0.85,
             label=f"""Team_3 std={aa1.std()},
             mean={aa1.mean()} """, color="#A60628", normed=True)
    plt.legend(loc="upper left")
    plt.title(f"some interesting analysis")
    plt.xlim([1, 4])
    plt.xlabel(f"mean score of rank {rank}")
    
    ax = plt.subplot(512)
    ax.set_autoscaley_on(False)
    plt.hist(aa2, histtype='stepfilled', bins=30, alpha=0.85,
             label=f"""Team_4 std={aa2.std()},
             mean={aa2.mean()} """, color="#7A68A6", normed=True)
    plt.legend(loc="upper left")
    plt.xlim([1, 4])
    plt.xlabel(f"mean score of rank {rank}")
    
    
    ax = plt.subplot(513)
    ax.set_autoscaley_on(False)
    plt.hist(aa3, histtype='stepfilled', bins=30, alpha=0.85,
             label=f"""Team_6 std={aa3.std()},
             mean={aa3.mean()} """, color="#1A68A6", normed=True)
    plt.legend(loc="upper left")
    plt.xlim([1, 4])
    plt.xlabel(f"mean score of rank {rank}")
    
    ax = plt.subplot(514)
    ax.set_autoscaley_on(False)
    plt.hist(aa4, histtype='stepfilled', bins=30, alpha=0.85,
             label=f"""Team_7 std={aa4.std()},
             mean={aa4.mean()} """, color="#1A68A6", normed=True)
    plt.legend(loc="upper left")
    plt.xlim([1, 4])
    plt.xlabel(f"mean score of rank {rank}")
    
    
    ax = plt.subplot(515)
    ax.set_autoscaley_on(False)
    plt.hist(aa5, histtype='stepfilled', bins=30, alpha=0.85,
             label=f"""Team_30 std={aa5.std()},
             mean={aa5.mean()} """, color="#1A68A6", normed=True)
    plt.legend(loc="upper left")
    plt.xlim([1, 4])
    plt.xlabel(f"mean score of rank {rank}")
