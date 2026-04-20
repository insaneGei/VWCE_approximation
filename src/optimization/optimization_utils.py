import numpy as np
from scipy.optimize import minimize


def compute_optimal_weights(etf_allocations, target):
    """
    Find ETF weights that minimize the squared distance to a target geographic allocation.

    Solves: min_{w} || A w - g ||^2  s.t.  sum(w) = 1
    where A is the matrix of ETF country allocations and g is the target.

    Parameters
    ----------
    etf_allocations : pd.DataFrame
        Country weights per ETF. Index = country names, columns = ETF names.
    target : pd.Series
        Target country weights. Index = country names.

    Returns
    -------
    np.ndarray
        Optimal weight for each ETF (same order as etf_allocations.columns), summing to 1.
    """
    n = etf_allocations.shape[1]
    all_countries = etf_allocations.index.union(target.index)
    A = etf_allocations.reindex(all_countries, fill_value=0).values
    g = target.reindex(all_countries, fill_value=0).values
    history = []

    def objective(w):
        return np.linalg.norm(A @ w - g) ** 2

    def callback(xk):
        score = objective(xk)
        history.append(score)
        print(f"Iteration {len(history)}: {score}")

    x0 = np.ones(n) / n
    constraints = {'type': 'eq', 'fun': lambda w: w.sum() - 1}

    res = minimize(objective, x0, method='SLSQP', callback=callback,
                   constraints=constraints, options={'maxiter': 5000, 'disp': True})
    return res.x
