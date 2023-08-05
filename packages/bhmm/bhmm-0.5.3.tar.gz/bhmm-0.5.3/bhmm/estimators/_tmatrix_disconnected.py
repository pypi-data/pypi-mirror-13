__author__ = 'noe'

import numpy as np

def estimate_P(C, reversible = True, fixed_statdist=None):
    # import emma
    import msmtools.estimation as msmest
    # output matrix. Initially eye
    n = np.shape(C)[0]
    P = np.eye((n), dtype=np.float64)
    # treat each connected set separately
    S = msmest.connected_sets(C)
    for s in S:
        if len(s) > 1: # if there's only one state, there's nothing to estimate and we leave it with diagonal 1
            # compute transition sub-matrix on s
            Cs = C[s,:][:,s]
            Ps = msmest.transition_matrix(Cs, reversible = reversible, mu=fixed_statdist)
            # write back to matrix
            for i,I in enumerate(s):
                for j,J in enumerate(s):
                    P[I,J] = Ps[i,j]
            P[s,:][:,s] = Ps
    # done
    return P

def stationary_distribution(C, P):
    # import emma
    import msmtools.estimation as msmest
    import msmtools.analysis as msmana
    # disconnected sets
    n = np.shape(C)[0]
    ctot = np.sum(C)
    pi = np.zeros((n))
    # treat each connected set separately
    S = msmest.connected_sets(C)
    for s in S:
        # compute weight
        w = np.sum(C[s,:]) / ctot
        pi[s] = w * msmana.statdist(P[s,:][:,s])
    # reinforce normalization
    pi /= np.sum(pi)
    return pi
