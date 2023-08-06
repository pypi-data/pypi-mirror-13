"""
MCBH method of approximation of problem matrix by H2-matrix.
"""

from __future__ import print_function, absolute_import, division

from time import time
import numpy as np
from .h2matrix import H2matrix
from maxvolpy.maxvol import maxvol_svd, maxvol_qr

def mcbh(problem, tau, iters=1, onfly=False, verbose=False):
    """
    Computes H2-approximation by MCBH method.

    Uses Multicharge Barnes-Hut method (MCBH) of approximation of
    discretized non-local operators by H2-matrices [MCBH]_.

    Parameters
    ----------
    problem : h2tools.problem.Problem
        Discretized problem with block cluster tree.
    tau : float
        Parameter of desired relative error (spectral tolerance for
        SVDs).
    iter : integer
        Number of iterations (depends on problem).
    onfly : bool
        Wheather or not to use "low" memory allocation type (useful
        if matrix elements are fast enough to compute, saves a lot
        of memory).
    verbose : boolean
        Whether or not to print additional information.

    Returns
    -------
    h2tools.h2matrix.H2matrix
        H2-approximation.
    """
    time0 = time()
    # far field approximation timings [ function time,
    #     block function calls, elements computed, maxvol time]
    far_timings = [0., 0, 0, 0.]
    # close field timings [ function time, block function calls,
    #     elements computed]
    close_timings = [0., 0, 0]
    row_size = problem.row_tree.level[-1]
    row_prebasis = [np.ndarray(0, dtype=np.uint64) for i in range(row_size)]
    col_size = problem.col_tree.level[-1]
    col_prebasis = [np.ndarray(0, dtype=np.uint64) for i in range(col_size)]
    row_basis, row_transfer, col_basis, col_transfer = _factorup(problem,
            tau, row_prebasis, col_prebasis, far_timings, verbose)
    for i in range(iters):
        row_prebasis, col_prebasis = _factordown(problem, row_basis,
                row_transfer, col_basis, col_transfer, far_timings, verbose)
        row_basis, row_transfer, col_basis, col_transfer = _factorup(problem,
                tau, row_prebasis, col_prebasis, far_timings, verbose)
    if not onfly:
        row_interaction, col_interaction = _matrix(problem, row_basis,
                col_basis, far_timings)
        row_close, col_close = _close_matrix(problem, close_timings)
    else:
        row_interaction = None
        col_interaction = None
        row_close = None
        col_close = None
    ans = H2matrix(problem, row_transfer, col_transfer, row_interaction,
            col_interaction, row_close, col_close, row_basis, col_basis)
    totaltime = time()-time0
    if verbose:
        print('Far-field interactions(MCBH method):')
        print('    Function calls: {}'.format(far_timings[1]))
        print('    Function values computed: {}'.format(far_timings[2]))
        print('    Function time: {:.2f} seconds'.format(far_timings[0]))
        if far_timings[2] > 0:
            print('    Average time per function value: {:.2e} seconds'.
                    format(far_timings[0]/far_timings[2]))
        print('    Maxvol time: {:.2f} seconds'.format(far_timings[3]))
        print('Near-field interactions:')
        print('    Function calls: {}'.format(close_timings[1]))
        print('    Function values computed: {}'.format(close_timings[2]))
        print('    Function time: {:.2f} seconds'.format(close_timings[0]))
        if close_timings[2] > 0:
            print('    Average time per function value: {:.2e} seconds'.
                    format(close_timings[0]/close_timings[2]))
        print('Total time: {:.2f} seconds'.format(totaltime))
        print('Memory:')
        print('    Basises: {:.2f} MB'.format(
            ans.nbytes(0, 0, 0, 1, 0)/1024/1024))
        print('    Transfer matrices: {:.2f} MB'.format(
            ans.nbytes(1, 0, 0, 0, 0)/1024/1024))
        print('    Far-field interactions: {:.2f} MB'.format(
            ans.nbytes(0, 1, 0, 0, 0)/1024/1024))
        print('    Near-field interactions: {:.2f} MB'.format(
            ans.nbytes(0, 0, 1, 0, 0)/1024/1024))
        print('    Python control structures: {:.2f} MB'.format(
            ans.nbytes(0, 0, 0, 0, 1)/1024/1024))
        print('Total memory: {:.2f} MB'.format(ans.nbytes()/1024/1024))
    return ans

def _factorup(problem, tau, row_prebasis, col_prebasis, timings, verbose):
    """
    Computes basises/transfer matrices with given representing sets.
    """
    def _buildmatrix(ind, RC, tree0, far0, tree1, basis0, basis1, prebasis,
            func, timings):
        """
        Returns basis and interaction matrix of node 'ind' of 'tree0'.
        """
        child = tree0.child[ind]
        if not child:
            list0 = [tree0.index[ind]]
            index0 = list0[0]
        else:
            list0 = []
            for k in child:
                list0.append(basis0[k])
            index0 = np.concatenate(list0)
        list1 = [prebasis]
        child = tree1.child
        for k in far0[ind]:
            if basis1[k].size > 0:
                list1.append(basis1[k])
            elif not child[k]:
                list1.append(tree1.index[k])
            else:
                for l in child[k]:
                    list1.append(basis1[l])
        if len(list1) > 1:
            index1 = np.concatenate(list1)
            if RC == 'row':
                time0 = time()
                matrix = func(index0, index1)
                timings[0] += time()-time0
            else:
                time0 = time()
                matrix = func(index1, index0)
                timings[0] += time()-time0
            timings[1] += 1
            timings[2] += matrix.size
            return index0, matrix
        else:
            return index0, None
    
    tol = 1.05
    dtype = problem.dtype
    func = problem.func
    queue = problem.queue
    row_tree = problem.row_tree
    row_far = problem.row_far
    row_notransition = problem.row_notransition
    col_tree = problem.col_tree
    col_far = problem.col_far
    col_notransition = problem.col_notransition
    row_size = row_tree.level[-1]
    col_size = col_tree.level[-1]
    row_basis = [np.ndarray(0, dtype=np.uint64) for i in range(row_size)]
    row_transfer = [np.ndarray((0, 0)) for i in range(row_size)]
    if problem.symmetric:
        col_basis = row_basis
        col_transfer = row_transfer
    else:
        col_basis = [np.ndarray(0, dtype=np.uint64) for i in range(col_size)]
        col_transfer = [np.ndarray((0, 0)) for i in range(col_size)]
    # Loop is query-dependant
    for i in queue:
        for j in i:
            ind = j[1]
            if j[0] == 'row':
                row, matrix = _buildmatrix(ind, j[0], row_tree, row_far,
                        col_tree, row_basis, col_basis,
                        row_prebasis[row_tree.parent[ind]], func, timings)
                if matrix is None:
                    row_basis[ind] = row.copy()
                    row_transfer[ind] = np.ndarray((0, row.size), dtype=dtype)
                else:
                    time0 = time()
                    basis, row_transfer[ind] = maxvol_svd(matrix, tau, tol,
                            job='R')
                    timings[3] += time()-time0
                    row_basis[ind] = row[basis].copy()
                del row, matrix
            else:
                col, matrix = _buildmatrix(ind, j[0], col_tree, col_far,
                        row_tree, col_basis, row_basis,
                        col_prebasis[col_tree.parent[ind]], func, timings)
                if matrix is None:
                    col_basis[ind] = col.copy()
                    col_transfer[ind] = np.ndarray((0, col.size), dtype=dtype)
                else:
                    time0 = time()
                    basis, col_transfer[ind] = maxvol_svd(matrix, tau, tol,
                            job='C')
                    timings[3] += time()-time0
                    col_basis[ind] = col[basis].copy()
                del col, matrix
    return row_basis, row_transfer, col_basis, col_transfer

def _factordown(problem, row_basis, row_transfer, col_basis, col_transfer,
        timings, verbose):
    """
    Computes representing sets with given basises.
    """
    func = problem.func
    queue = problem.queue
    row_tree = problem.row_tree
    row_far = problem.row_far
    row_notransition = problem.row_notransition
    col_tree = problem.col_tree
    col_far = problem.col_far
    col_notransition = problem.col_notransition
    row_size = row_tree.level[-1]
    col_size = col_tree.level[-1]
    row_prebasis = [np.ndarray(0, dtype=np.uint64) for i in range(row_size)]
    col_prebasis = [np.ndarray(0, dtype=np.uint64) for i in range(col_size)]
    tol = 1.05
    # Loop is query-dependant
    for i in reversed(queue):
        for j in i:
            ind = j[1]
            if j[0] == 'row':
                row = row_basis[ind]
                col_list = [row_prebasis[row_tree.parent[ind]]]
                for k in row_far[ind]:
                    col_list.append(col_basis[k])
                col = np.concatenate(col_list)
                if row.size >= col.size:
                    row_prebasis[ind] = col.copy()
                else:
                    time0 = time()
                    tmpmatrix = func(row, col).T
                    timings[0] += time()-time0
                    timings[1] += 1
                    timings[2] += tmpmatrix.size
                    time0 = time()
                    tmpmatrix = maxvol_qr(tmpmatrix, tol)[0]
                    timings[3] += time()-time0
                    row_prebasis[ind] = col[tmpmatrix].copy()
                    del tmpmatrix
                del row, col, col_list
            else:
                col = col_basis[ind]
                row_list = [col_prebasis[col_tree.parent[ind]]]
                for k in col_far[ind]:
                    row_list.append(row_basis[k])
                row = np.concatenate(row_list)
                if col.size >= row.size:
                    col_prebasis[ind] = row.copy()
                else:
                    time0 = time()
                    tmpmatrix = func(row, col)
                    timings[0] += time()-time0
                    timings[1] += 1
                    timings[2] += tmpmatrix.size
                    time0 = time()
                    tmpmatrix = maxvol_qr(tmpmatrix, tol)[0]
                    timings[3] += time()-time0
                    col_prebasis[ind] = row[tmpmatrix].copy()
                    del tmpmatrix
                del row, row_list, col
    return row_prebasis, col_prebasis
        
def _matrix(problem, row_basis, col_basis, timings):
    """
    Computes interaction matrices.
    """
    func = problem.func
    row = problem.row_tree
    row_far = problem.row_far
    col = problem.col_tree
    col_far = problem.col_far
    row_size = row.level[-1]
    col_size = col.level[-1]
    row_interaction = [[] for i in range(row_size)]
    # Loop is query-independant
    for i in range(row_size):
        for j in row_far[i]:
            time0 = time()
            tmpmatrix = func(row_basis[i], col_basis[j])
            timings[0] += time()-time0
            timings[1] += 1
            timings[2] += tmpmatrix.size
            row_interaction[i].append(tmpmatrix)
            del tmpmatrix
    if problem.symmetric:
        col_interaction = row_interaction
    else:
        col_interaction = [[] for i in range(col_size)]
        for i in range(col_size):
            for j in col_far[i]:
                k = row_far[j].index(i)
                col_interaction[i].append(row_interaction[j][k].T)
    return row_interaction, col_interaction

def _close_matrix(problem, timings):
    func = problem.func
    row = problem.row_tree
    row_close = problem.row_close
    col = problem.col_tree
    col_close = problem.col_close
    row_size = row.level[-1]
    col_size = col.level[-1]
    row_close_interaction = [[] for i in range(row_size)]
    # Loop is query-independant
    for i in range(row_size):
        for j in row_close[i]:
            time0 = time()
            tmpmatrix = func(row.index[i], col.index[j])
            timings[0] += time()-time0
            timings[1] += 1
            timings[2] += tmpmatrix.size
            row_close_interaction[i].append(tmpmatrix)
            del tmpmatrix
    if problem.symmetric:
        col_close_interaction = row_close_interaction
    else:
        col_close_interaction = [[] for i in range(col_size)]
        for i in range(col_size):
            for j in col_close[i]:
                k = row_close[j].index(i)
                col_close_interaction[i].append(row_close_interaction[j][k].T)
    return row_close_interaction, col_close_interaction
