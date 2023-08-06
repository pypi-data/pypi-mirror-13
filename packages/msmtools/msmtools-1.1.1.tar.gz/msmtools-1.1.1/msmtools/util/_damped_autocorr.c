
/*
    # integrate damped autocorrelation
    corrsum = 0.0
    for lag in range(N):
        acf = 0.0
        n = 0.0
        for x in X0:
            Nx = len(x)  # length of this trajectory
            if (Nx > lag):  # only use trajectories that are long enough
                acf += np.sum(x[0:Nx-lag] * x[lag:Nx])
                n += float(Nx-lag)
        acf /= n
        if acf <= 0 and truncate_acf:  # zero autocorrelation. Exit
            break
        elif lag > 0:  # start integrating at lag 1 (effect of lag 0 is contained in the 0.5 below
            corrsum += acf * (1.0 - (float(lag)/float(N)))

            */

double damped_corr(long N, PyObject*)
