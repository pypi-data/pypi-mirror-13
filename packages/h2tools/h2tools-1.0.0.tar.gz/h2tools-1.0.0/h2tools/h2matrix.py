"""
Class H2matrix represents H2-matrices in special low-parametric format.
"""

from __future__ import print_function, absolute_import, division

__all__ = ['H2matrix']

from time import time
import numpy as np
from maxvolpy.maxvol import maxvol_svd, maxvol_qr
from .problem import Problem
import copy
try:
    from pypropack import svdp
except:
    pass
import scipy.sparse.linalg as la
from sys import getsizeof

class H2matrix(object):
    """
    Low-parametric structure of H2-matrices.

    Every H2-matrix is based on row and column cluster trees with
    corresponding transfer and interaction matrices. However, there is
    special case of H2-format, when interaction matrices are simply
    submatrices of a given matrix. In such case each interaction matrix
    can be computed on demand as a submatrix, based on corresponding
    rows and columns.

    There are 2 types of structure and 2 types of memory allocation
    for H2matrix instance:

    Types of structure:
        1. "h2": no conditions on far-field interaction matrices.
        2. "mcbh": far-field interaction matrices are submatrices of
           given matrix, based on lists of basis rows and columns.
     
    Types of memory allocation:
        1. "full": all interaction matrices are stored in memory.
        2. "low": close-field interaction matrices are computed on
           demand, far field interaction matrices are also computed on
           demand for "mcbh"-type structure.

    Usually, most memory consuming part of H2matrix is a list of
    far-field interaction matrices. Since main feature of "mcbh"-type
    structure of H2matrix is representation of far-field interaction
    matrices as submatrices of initial matrix, based on lists of basis
    rows and columns, using "low" memory allocation model saves a lot
    of memory in case of "mcbh"-type structure of H2matrix. For some
    problems, it decreases total memory consumption of H2matrix by an
    order of magnitude.

    Parameters
    ----------
    problem: Problem
        Contains all information on problem (linear operator and block
        cluster tree).
    row_transfer : list of numpy.ndarray(ndim=2)
        Transfer matrix for each node of row cluster tree.
    col_transfer : list of numpy.ndarray(ndim=2)
        Transfer matrix for each node of column cluster tree.
    row_interaction : list of list of numpy.ndarray(ndim=2)
        Far-field interaction matrices for each node of row cluster
        tree. At least one of `row_interaction` and `col_interaction`
        must be set.
    col_interaction : list of list of numpy.ndarray(ndim=2)
        Far-field interaction matrices for each node of column cluster
        tree. At least one of `row_interaction` and `col_interaction`
        must be set.
    row_close : list of list of numpy.ndarray(ndim=2)
        Near-field interaction matrices for each node of row cluster
        tree. At least one of `row_close` and `col_close` must be set.
    col_close : list of list of numpy.ndarray(ndim=2)
        Near-field interaction matrices for each node of column cluster
        tree. At least one of `row_close` and `col_close` must be set.
    row_basis : list of numpy.ndarray(ndim=1, dtype=numpy.uint64)
        Basis rows for each node of row cluster tree.
    col_basis : list of numpy.ndarray(ndim=1, dtype=numpy.uint64)
        Basis columns for each node of column cluster tree.

    Attributes
    ----------
    problem : instance of class h2tools.Problem
        Contains information about source and destination datas,
        cluster trees and lists of admissibly far and admissibly close
        nodes.
    h2_type : string
        Type of structure. Possible values are following:
        - "h2": no conditions on interaction matrices, no basis rows or
          columns, standard H2matrix format.
        - "mcbh": interaction matrices are submatrices of initial
            matrix (defined by `problem`), requires basis rows and
            columns.
    mem_type : string
        Memory allocation model. Possible values are following:
        - "full": all interaction matrices are stored in memory.
        - "low": close-field interaction matrices are computed on
          demand, far field interaction matrices are also computed on
          demand (not stored in memory) if `h2_type` is "mcbh".
    row_basis : list of numpy.ndarray(ndim=1, dtype=numpy.uint64)
        Contains indexes of basis rows for each node of row cluster
        tree.
    col_basis : list of numpy.ndarray(ndim=1, dtype=numpy.uint64)
        Contains indexes of basis columns for each node of column
        cluster tree.
    row_transfer : list of numpy.ndarray(ndim=2)
        Transfer matrices from children to node for each node of row
        cluster tree.
    col_transfer : list of numpy.ndarray(ndim=2)
        Transfer matrices from children to node for each node of column
        cluster tree.
    row_interaction : list of list of numpy.ndarray(ndim=2)
        List of interaction matrices with corresponding admissibly far
        nodes for each node of row cluster tree.
    col_interaction : list of list of numpy.ndarray(ndim=2)
        List of interaction matrices with corresponding admissibly far
        nodes for each node of column cluster tree.
    row_close : list of list of numpy.ndarray(ndim=2)
        List of interaction matrices with corresponding admissibly
        close nodes for each node of row cluster tree.
    col_close : list of list of numpy.ndarray(ndim=2)
        List of interaction matrices with corresponding admissibly
        close nodes for each node of column cluster tree.
    """

    def __init__(self, problem, row_transfer, col_transfer, row_interaction,
            col_interaction, row_close, col_close, row_basis=None,
            col_basis=None):
        if type(problem) is not Problem:
            raise TypeError('problem parameter must be instance of'
                    ' h2py.Problem')
        if not isinstance(row_transfer, list):
            raise TypeError('row_transfer parameter should be list of'
                    ' transfer matrices for row (destination) cluster tree')
        if not isinstance(col_transfer, list):
            raise TypeError('col_transfer parameter should be list of'
                    ' transfer matrices for column (source) cluster tree')
        if not (((row_basis is None) and (col_basis is None)) or
                (isinstance(row_basis, list) and isinstance(col_basis, list))):
            raise TypeError('row_basis and col_basis parameters should be'
                    ' both None or both lists of corresponding basises.')
        if row_interaction is None and col_interaction is not None:
            try:
                size = problem.row_tree.level[-1]
                row_interaction = [[] for i in range(size)]
                for i in range(size):
                    for j in problem.row_far[i]:
                        k = problem.col_far[j].index(i)
                        row_interaction[i].append(col_interaction[j][k].T)
            except:
                raise ValueError('col_interaction must be None or a list of'
                        ' lists of far-field interaction matrices of'
                        ' appropriate size.')
        if col_interaction is None and row_interaction is not None:
            try:
                size = problem.col_tree.level[-1]
                col_interaction = [[] for i in range(size)]
                for i in range(size):
                    for j in problem.col_far[i]:
                        k = problem.row_far[j].index(i)
                        col_interaction[i].append(row_interaction[j][k].T)
            except:
                raise ValueError('row_interaction must be None or a list of'
                        ' lists of far-field interaction matrices of'
                        ' appropriate size.')
        if row_close is None and col_close is not None:
            try:
                size = problem.row_tree.level[-1]
                row_close = [[] for i in range(size)]
                for i in range(size):
                    for j in problem.row_close[i]:
                        k = problem.col_close[j].index(i)
                        row_close[i].append(col_close[j][k].T)
            except:
                raise ValueError('col_close must be None or a list of lists'
                        ' of near-field interaction matrices of appropriate'
                        ' size.')
        if col_close is None and row_close is not None:
            try:
                size = problem.col_tree.level[-1]
                col_close = [[] for i in range(size)]
                for i in range(size):
                    for j in problem.col_close[i]:
                        k = problem.row_close[j].index(i)
                        col_close[i].append(row_close[j][k].T)
            except:
                raise ValueError('row_close must be None or a list of lists'
                        ' of near-field interaction matrices of appropriate'
                        ' size.')
        if row_basis is None:
            self.h2_type = 'h2'
        else:
            self.h2_type = 'mcbh'
        if self.h2_type == 'mcbh' and ((row_close is None) is
                (row_interaction is not None)):
            print('Since only one of far-field and close-field interactions'
                    ' were assigned as None, assuming "low" memory allocation'
                    ' type (both set as None).')
            row_interaction = None
            col_interaction = None
            row_close = None
            col_close = None
        if row_close is None:
            self.mem_type = 'low'
        else:
            self.mem_type = 'full'
        self.problem = problem
        self.shape = problem.shape
        self.dtype = problem.dtype
        self.row_basis = row_basis
        self.col_basis = col_basis
        self.row_transfer = row_transfer
        self.col_transfer = col_transfer
        self.row_interaction = row_interaction
        self.col_interaction = col_interaction
        self.row_close = row_close
        self.col_close = col_close

    def func(self, row, col):
        """
        Returns submatrix on intersection of given rows and columns.

        Parameters
        ----------
        row : numpy.ndarray(ndim=1, dtype=numpy.uint64)
            rows, where to compute submatrix
        col : numpy.ndarray(ndim=1, dtype=numpy.uint64)
            columns, where to compute submatrix

        Returns
        -------
        numpy.ndarray
            Submatrix on intersection of given rows and columns.
        """
        return self.problem.func(row, col)

    def _matrix(self):
        """Technical procedure, computes far-field interaction matrices"""
        row = self.problem.row_tree
        row_far = self.problem.row_far
        row_data = self.problem.row_data
        col = self.problem.col_tree
        col_far = self.problem.col_far
        col_data = self.problem.col_data
        row_basis = self.row_basis
        col_basis = self.col_basis
        row_size = row.level[-1]
        col_size = col.level[-1]
        self.row_interaction = [[] for i in range(row_size)]
        # Loop is query-independant
        for i in range(row_size):
            for j in row_far[i]:
                time0 = time()
                tmpmatrix = self.func(row_basis[i], col_basis[j])
                self.row_interaction[i].append(tmpmatrix)
                del tmpmatrix
        if self.problem.symmetric:
            self.col_interaction = self.row_interaction
        else:
            self.col_interaction = [[] for i in range(col_size)]
            for i in range(col_size):
                for j in col_far[i]:
                    k = row_far[j].index(i)
                    self.col_interaction[i].append(
                            self.row_interaction[j][k].T)

    @staticmethod
    def __dot_up(tree, notransition, transfer, x):
        """
        Computes "charges" of basis elements.
        
        Does it in bottom-to-top manner.
        """
        size = tree.level[-1]
        level_count = len(tree.level)-1
        node_weight = [np.zeros((0, x.shape[1]), dtype=x.dtype) for
                i in range(size)]
        # Loop is query-dependant
        for i in range(level_count-1):
            for j in range(tree.level[level_count-i-2],
                    tree.level[level_count-i-1]):
                if notransition[j]:
                    continue
                if not tree.child[j]:
                    tmp = x[tree.index[j]]
                else:
                    tmp = []
                    for k in tree.child[j]:
                        tmp.append(node_weight[k])
                    tmp = np.vstack(tmp)
                if transfer[j].shape[0] == 0:
                    node_weight[j] = tmp
                else:
                    node_weight[j] = transfer[j].T.dot(tmp)
        return node_weight

    @staticmethod
    def __dot_interact(tree, far, notransition, matrix, node_weight):
        """
        Computes "potentials" of basis elements.

        Uses precomputed interaction matrices and "charges" of adjunct
        cluster tree.
        """
        size = tree.level[-1]
        tmp = node_weight[-1]
        node_answer = [np.ndarray((0, tmp.shape[1]), dtype=tmp.dtype) if
            not far[i] else
            np.zeros((matrix[i][0].shape[0], tmp.shape[1]), dtype=tmp.dtype)
            for i in range(size)]
        for i in range(size):
            if notransition[i]:
                continue
            tmp = node_answer[i]
            for j in range(len(far[i])):
                tmp += matrix[i][j].dot(node_weight[far[i][j]])
        return node_answer

    @staticmethod
    def __dot_interact_onfly(tree, far, notransition, func, basis0, basis1,
            node_weight, T=False):
        """
        Computes "potentials" of basis elements.

        Computes interaction matrices on fly and uses precomputed
        "charges" of adjunct cluster tree.
        """
        size = tree.level[-1]
        tmp = node_weight[-1]
        node_answer = [np.ndarray((0, tmp.shape[1]), dtype=tmp.dtype) if
                not far[i] else
                np.zeros((basis0[i].shape[0], tmp.shape[1]), dtype=tmp.dtype)
                for i in range(size)]
        for i in range(size):
            if notransition[i]:
                continue
            tmp = node_answer[i]
            if T:
                for j in range(len(far[i])):
                    tmp += func(basis1[far[i][j]], basis0[i]).T.dot(
                            node_weight[far[i][j]])
            else:
                for j in range(len(far[i])):
                    tmp += func(basis0[i], basis1[far[i][j]]).dot(
                            node_weight[far[i][j]])
        return node_answer
    
    @staticmethod
    def __dot_down(tree, notransition, transfer, node_answer):
        """
        Computes "potentials" of all elements.

        Uses precomputed "potentials" of cluster tree.
        """
        size = tree.level[-1]
        level_count = len(tree.level)-1
        tmp = node_answer[-1]
        dtype = tmp.dtype
        nrhs = tmp.shape[1]
        answer = np.zeros((tree.data.count, nrhs), dtype=dtype)
        for i in range(level_count-1):
            for j in range(tree.level[i], tree.level[i+1]):
                if notransition[j]:
                    continue
                if node_answer[j].shape[0] == 0:
                    node_answer[j] = np.zeros((transfer[j].shape[1], nrhs),
                            dtype=dtype)
        for i in range(level_count-1):
            for j in range(tree.level[i], tree.level[i+1]):
                if notransition[j]:
                    continue
                if transfer[j].shape[0] == 0:
                    tmp = node_answer[j]
                else:
                    tmp = transfer[j].dot(node_answer[j])
                if not tree.child[j]:
                    answer[tree.index[j]] = tmp
                else:
                    i1 = 0
                    for k in tree.child[j]:
                        i2 = i1 + node_answer[k].shape[0]
                        node_answer[k] += tmp[i1:i2]
                        i1 = i2
        return answer

    def far_dot(self, x):
        """
        Applies far-field part of H2matrix to vector from left side.

        Parameters
        ----------
        x : numpy.ndarray
            Vector or block-vector to multiply.

        Returns
        -------
        numpy.ndarray
            Result of farfield `A * x`. 
        """
        if x.shape[0] != self.shape[1]:
            raise ValueError('operands could not be broadcast together with'
                    ' shapes ({0:d}) ({1:d})').format(
                            self.shape[1], x.shape[0])
        if x.ndim == 1:
            x1 = x.reshape(-1, 1)
        else:
            x1 = x
        node_weight = self.__dot_up(self.problem.col_tree,
                self.problem.col_notransition, self.col_transfer, x1)
        if self.h2_type == 'mcbh' and self.mem_type == 'low':
            node_answer = self.__dot_interact_onfly(self.problem.row_tree,
                    self.problem.row_far, self.problem.row_notransition,
                    self.problem.func, self.row_basis, self.col_basis,
                    node_weight)
        else:
            node_answer = self.__dot_interact(self.problem.row_tree,
                    self.problem.row_far, self.problem.row_notransition,
                    self.row_interaction, node_weight)
        answer = self.__dot_down(self.problem.row_tree,
                self.problem.row_notransition, self.row_transfer, node_answer)
        if x.ndim == 1:
            answer = answer.reshape(-1)
        return answer

    def far_rdot(self, x):
        """
        Applies far-field part of H2matrix to vector from right side.

        Parameters
        ----------
        x : numpy.ndarray
            Vector or block-vector to multiply.

        Returns
        -------
        numpy.ndarray
            Result of farfield `x * A`. 
        """
        if x.shape[0] != self.shape[0]:
            raise ValueError('operands could not be broadcast together with'
                    ' shapes ({0:d}) ({1:d})').format(
                            self.shape[0], x.shape[0])
        if x.ndim == 1:
            x1 = x.reshape(-1, 1)
        else:
            x1 = x
        node_weight = self.__dot_up(self.problem.row_tree,
                self.problem.row_notransition, self.row_transfer, x1)
        if self.h2_type == 'mcbh' and self.mem_type == 'low':
            node_answer = self.__dot_interact_onfly(self.problem.col_tree,
                    self.problem.col_far, self.problem.col_notransition,
                    self.problem.func, self.col_basis, self.row_basis,
                    node_weight, True)
        else:
            node_answer = self.__dot_interact(self.problem.col_tree,
                    self.problem.col_far, self.problem.col_notransition,
                    self.col_interaction, node_weight)
        answer = self.__dot_down(self.problem.col_tree,
                self.problem.col_notransition, self.col_transfer, node_answer)
        if x.ndim == 1:
            answer = answer.reshape(-1)
        return answer

    def close_dot(self, x):
        """
        Applies near-field part of H2matrix to vector from left side.

        Parameters
        ----------
        x : numpy.ndarray
            Vector or block-vector to multiply.

        Returns
        -------
        numpy.ndarray
            Result of near-field `A * x`. 
        """
        if x.shape[0] != self.shape[1]:
            raise ValueError('operands could not be broadcast together with'
                    ' shapes ({0:d}) ({1:d})').format(
                            self.shape[1], x.shape[0])
        if x.ndim == 1:
            x1 = x.reshape(-1, 1)
        else:
            x1 = x
        nrhs = x1.shape[1]
        row = self.problem.row_tree
        col = self.problem.col_tree
        row_size = row.level[-1]
        row_close = self.problem.row_close
        matrix = self.row_close
        answer = np.zeros((self.shape[0], nrhs), dtype=self.dtype)
        func = self.problem.func
        if self.mem_type == 'low':
            for i in range(row_size):
                for j in range(len(row_close[i])):
                    tmp_index = col.index[row_close[i][j]]
                    answer[row.index[i]] += func(row.index[i], tmp_index).dot(
                            x1[tmp_index])
        else:
            for i in range(row_size):
                for j in range(len(row_close[i])):
                    answer[row.index[i]] += matrix[i][j].dot(x1[col.index[
                        row_close[i][j]]])
        if x.ndim == 1:
            answer = answer.reshape(-1)
        return answer

    def close_rdot(self, x):
        """
        Applies near-field part of H2matrix to vector from right side.

        Parameters
        ----------
        x : numpy.ndarray
            Vector or block-vector to multiply.

        Returns
        -------
        numpy.ndarray
            Result of near-field `x * A`.
        """
        if x.shape[0] != self.shape[0]:
            raise ValueError('operands could not be broadcast together with'
                    ' shapes ({0:d}) ({1:d})').format(
                            self.shape[0], x.shape[0])
        if x.ndim == 1:
            x1 = x.reshape(-1, 1)
        else:
            x1 = x
        nrhs = x1.shape[1]
        row = self.problem.row_tree
        col = self.problem.col_tree
        col_size = row.level[-1]
        col_close = self.problem.row_close
        matrix = self.col_close
        answer = np.zeros((self.shape[1], nrhs), dtype=self.dtype)
        func = self.problem.func
        if self.mem_type == 'low':
            for i in range(col_size):
                for j in range(len(col_close[i])):
                    tmp_index = row.index[col_close[i][j]]
                    answer[col.index[i]] += func(col.index[i], tmp_index).dot(
                            x1[tmp_index])
        else:
            for i in range(col_size):
                for j in range(len(col_close[i])):
                    answer[col.index[i]] += matrix[i][j].dot(x1[row.index[
                        col_close[i][j]]])
        if x.ndim == 1:
            answer = answer.reshape(-1)
        return answer

    def dot(self, x):
        """
        Applies multplication by H2matrix to vector from left side.

        Parameters
        ----------
        x : numpy.ndarray
            Vector or block-vector to multiply.

        Returns
        -------
        numpy.ndarray
            Result of `A * x`.
        """
        if x.shape[0] != self.shape[1]:
            raise ValueError('operands could not be broadcast together with'
                    ' shapes ({0:d}) ({1:d})').format(
                            self.shape[1], x.shape[0])
        if x.ndim == 1:
            x1 = x.reshape(-1, 1)
        else:
            x1 = x
        answer = self.far_dot(x1)+self.close_dot(x1)
        if x.ndim == 1:
            answer = answer.reshape(-1)
        return answer

    def rdot(self, x):
        """
        Applies multplication by H2matrix to vector from right side.

        Parameters
        ----------
        x : numpy.ndarray
            Vector or block-vector to multiply.

        Returns
        -------
        numpy.ndarray
            Result of `x * A`.
        """
        if x.shape[0] != self.shape[0]:
            raise ValueError('operands could not be broadcast together with'
                    ' shapes ({0:d}) ({1:d})').format(
                            self.shape[0], x.shape[0])
        if x.ndim == 1:
            x1 = x.reshape(-1, 1)
        else:
            x1 = x
        answer = self.far_rdot(x1)+self.close_rdot(x1)
        if x.ndim == 1:
            answer = answer.reshape(-1)
        return answer

    def nbytes(self, transfer=True, interaction=True, close=True, basis=True,
            python=True):
        """
        Returns memory, used by requested parts of H2matrix, in bytes.

        Parameters
        ----------
        transfer : boolean
            If true, adds to result size of memory buffers, used by
            transfer matrices.
        interaction : boolean
            If true, adds to result size of memory buffers, used by
            far-field interaction matrices.
        close : boolean
            If true, adds to result size of memory buffers, used by
            near-field interaction matrices.
        basis : boolean
            If true, adds to result size of memory buffers, used by
            storage of indexes of basis rows and columns.
        python : boolean
            If true, adds to result size of memory buffers, used by
            Python to wrap all buffers.

        Returns
        -------
        integer
            Number of bytes, consumed by given parts of H2matrix.
        """
        nbytes = 0
        if transfer:
            for i in self.row_transfer:
                for j in i:
                    nbytes += j.nbytes
            if not self.problem.symmetric:
                for i in self.col_transfer:
                    for j in i:
                        nbytes += j.nbytes
        if interaction and not (self.mem_type == 'low' and
                self.h2_type == 'mcbh'):
            for i in self.row_interaction:
                for j in i:
                    nbytes += j.nbytes
        if close and not self.mem_type == 'low':
            for i in self.row_close:
                for j in i:
                    nbytes += j.nbytes
        if basis and self.h2_type == 'mcbh':
            for i in self.row_basis:
                nbytes += i.nbytes
            if not self.problem.symmetric:
                for i in self.col_basis:
                    nbytes += i.nbytes
        if python:
            nbytes += getsizeof(self)
            if self.h2_type == 'mcbh':
                nbytes += getsizeof(self.row_basis)
                for i in self.row_basis:
                    nbytes += getsizeof(i)
            nbytes += getsizeof(self.row_transfer)
            for i in self.row_transfer:
                nbytes += getsizeof(i)
                for j in i:
                    nbytes += getsizeof(j)
            if not self.problem.symmetric:
                if self.h2_type == 'mcbh':
                    nbytes += getsizeof(self.col_basis)
                    for i in self.col_basis:
                        nbytes += getsizeof(i)
                nbytes += getsizeof(self.col_transfer)
                for i in self.col_transfer:
                    nbytes += getsizeof(i)
                    for j in i:
                        nbytes += getsizeof(j)
            if not (self.h2_type == 'mcbh' and self.mem_type == 'low'):
                nbytes += getsizeof(self.row_interaction)
                for i in self.row_interaction:
                    nbytes += getsizeof(i)
                    for j in i:
                        nbytes += getsizeof(j)
                if not self.problem.symmetric:
                    nbytes += getsizeof(self.col_interaction)
                    for i in self.col_interaction:
                        nbytes += getsizeof(i)
                        for j in i:
                            nbytes += getsizeof(j)
            if not self.mem_type == 'low':
                nbytes += getsizeof(self.row_close)
                for i in self.row_close:
                    nbytes += getsizeof(i)
                    for j in i:
                        nbytes += getsizeof(j)
                if not self.problem.symmetric:
                    nbytes += getsizeof(self.col_close)
                    for i in self.col_close:
                        nbytes += getsizeof(i)
                        for j in i:
                            nbytes += getsizeof(j)
        return nbytes
    
    def svdcompress(self, tau, verbose=False):
        """
        Decompression of H2matrix by SVD for block rows and columns.

        Performs SVD decompression of each block row and block column
        inplace. Orthogonolizes transfer matrices of row cluster tree,
        then decompresses block columns of column cluster tree, then
        orthogonolizes transfer matrices of column cluster tree and
        then decompresses block rows of row cluster tree. Finally,
        transfer matrices of row cluster tree are orthogonolized one
        additional time to make all transfer matrices orthogonal.

        Parameters
        ----------
        tau : float
            Spectral error tolerance for SVD decompressions of each block
            row and block column.
        verbose : boolean
            If true, shows memory before and after decompression and
            additional information in some cases.
        """
        time0 = time()
        if self.h2_type == 'mcbh' and self.mem_type == 'low':
            if verbose:
                print('Computing far-field interaction matrices, since they'
                        ' are required for svd decompression')
            self._matrix()
        if verbose:
            print('memory BEFORE SVD-compression: {0:.3f}MB'.format(
                self.nbytes()/1024./1024))
        transfer = self.row_transfer
        for i in range(len(transfer)):
            if self.problem.row_notransition[i]:
                continue
            if transfer[i].size == 0:
                transfer[i] = np.eye(transfer[i].shape[1],
                        dtype=transfer[i].dtype)
        if self.problem.symmetric:
            # if symmetry flag is True, then each item of self.queue
            # contains only 'row' tag
            self._orthogonolize('row')
            self._compress('row', tau)
            self._orthogonolize('row')
        else:
            transfer = self.col_transfer
            for i in range(len(transfer)):
                if self.problem.col_notransition[i]:
                    continue
                if transfer[i].size == 0:
                    transfer[i] = np.eye(transfer[i].shape[1],
                            dtype=transfer[i].dtype)
            self._orthogonolize('row')
            self._compress('col', tau)
            self._orthogonolize('col')
            self._compress('row', tau)
            self._orthogonolize('row')
        self._compresstime = time()-time0
        self.row_basis = None
        self.col_basis = None
        self.h2_type = 'h2'
        if verbose:
            print('memory AFTER SVD-compression: {0:.3f}MB'.format(
                self.nbytes()/1024./1024))
            print('recompression time:', self._compresstime)

    def _orthogonolize(self, RC):
        """
        Orthogonolizes transfer matrices for given cluster tree.
        
        Parameters
        ----------
        RC : string
            Shows what cluster tree's transfer matrices need to be
            orthogonolized. Possible values are "row" and "col".
        """
        if RC == 'row':
            tree = self.problem.row_tree
            far = self.problem.row_far
            transfer = self.row_transfer
            interaction = self.row_interaction
            interaction2 = self.col_interaction
            node_count = tree.level[-1]
        else:
            tree = self.problem.col_tree
            far = self.problem.col_far
            transfer = self.col_transfer
            interaction = self.col_interaction
            interaction2 = self.row_interaction
            node_count = tree.level[-1]
        diff = [0 for i in range(node_count)]
        for i in self.problem.queue:
            for j in i:
                if RC == j[0]:
                    k = j[1]
                    # Update transfer matrix from children nodes
                    if tree.child[k]:
                        s = 0
                        for l in tree.child[k]:
                            e = s+diff[l].shape[1]
                            transfer[k][s:e] = diff[l].dot(transfer[k][s:e])
                            s = e
                    # Update transfer matrix with Q factor of QR factorization
                    transfer[k], r = np.linalg.qr(transfer[k])
                    # Apply R factor of QR factorization to
                    # interaction matrices
                    for l in range(len(interaction[k])):
                        interaction[k][l] = r.dot(interaction[k][l])
                    diff[k] = r
        if self.problem.symmetric:
            for i in self.problem.queue:
                for j in i:
                    if RC == j[0]:
                        k = j[1]
                        # Apply R factors to interaction matrices from the
                        # other side for symmetry
                        for l in range(len(interaction[k])):
                            interaction[k][l] = interaction[k][l].dot(
                                    diff[far[k][l]].T)
        for i in self.problem.queue:
            for j in i:
                if RC == j[0]:
                    k = j[1]
                    # Update interaction matrices for another tree
                    for l in range(len(interaction[k])):
                        m = far[far[k][l]].index(k)
                        interaction2[far[k][l]][m] = interaction[k][l].T

    def _compress(self, RC, tau):
        """
        Performs SVD decompression of block rows and columns.
        
        Parameters `RC` shows which cluster tree needs to be
        decompressed. Requires all transfer matrices of adjunct cluster
        tree to be orthogonal.
        """
        if RC == 'row':
            tree = self.problem.row_tree
            far = self.problem.row_far
            transfer = self.row_transfer
            interaction = self.row_interaction
            interaction2 = self.col_interaction
            node_count = tree.level[-1]
            notransition = self.problem.row_notransition
        else:
            tree = self.problem.col_tree
            far = self.problem.col_far
            transfer = self.col_transfer
            interaction = self.col_interaction
            interaction2 = self.row_interaction
            node_count = tree.level[-1]
            notransition = self.problem.col_notransition
        diffS = [0 for i in range(node_count)]
        diffU = [0 for i in range(node_count)]
        for i in reversed(self.problem.queue):
            for j in i:
                if RC == j[0]:
                    k = j[1]
                    p = tree.parent[k]
                    # Put part of parent transfer matrix, according to
                    # node itself, into 'tmp_matrix'
                    if notransition[p]:
                        tmp_matrix = []
                    else:
                        l = 0
                        tmp_list = tree.child[p]
                        ind0 = 0
                        ind1 = transfer[tmp_list[l]].shape[1]
                        while tmp_list[l] != k:
                            l += 1
                            ind0 = ind1
                            ind1 = ind0+transfer[tmp_list[l]].shape[1]
                        tmp_matrix = [transfer[p][ind0:ind1]]
                    # Put all the interaction matrices into 'tmp_matrix'
                    tmp_matrix.extend(interaction[k])
                    tmp_matrix = np.hstack(tmp_matrix)
                    # Compute SVD of tmp_matrix
                    U, S, V = np.linalg.svd(tmp_matrix, full_matrices=0)
                    # Define new rank with relative tolerance 'tau'
                    new_rank = S.size
                    tmp_eps = tau*S[0]
                    for l in range(S.size):
                        if S[l] < tmp_eps:
                            new_rank = l
                            break
                    S = S[:new_rank].copy()
                    U = U[:, :new_rank].copy()
                    #V = V[:new_rank]
                    diffS[k] = S
                    diffU[k] = np.diag(1/S).dot(U.T.conj())
                    # Update transfer matrix according to SVD
                    transfer[k] = transfer[k].dot(U.dot(np.diag(S)))
        for i in self.problem.queue:
            for j in i:
                if RC == j[0]:
                    k = j[1]
                    #Update transfer matrix
                    if (not notransition[k]) and tree.child[k]:
                        s = 0
                        tmp_matrix = []
                        last_row = 0
                        for l in range(len(tree.child[k])):
                            tmp_diff = diffU[tree.child[k][l]]
                            e = s+tmp_diff.shape[1]
                            tmp_matrix.append(tmp_diff.dot(transfer[k][s:e]))
                            s = e
                            last_row += tmp_diff.shape[0]
                        if s != transfer[k].shape[0]:
                            raise ValueError('Internal error of '
                                    'svdcompress(_compress function)')
                        transfer[k] = np.vstack(tmp_matrix)
                    # Update interaction matrices according to SVD
                    for l in range(len(interaction[k])):
                        interaction[k][l] = diffU[k].dot(
                                interaction[k][l])
        if self.problem.symmetric:
            for i in self.problem.queue:
                for j in i:
                    if RC == j[0]:
                        k = j[1]
                        # Update interaction matrices from the other side
                        # for symmetry
                        for l in range(len(interaction[k])):
                            interaction[k][l] = interaction[k][l].dot(
                                    diffU[far[k][l]].T)
        for i in self.problem.queue:
            for j in i:
                if RC == j[0]:
                    k = j[1]
                    # Update interaction matrices for another tree
                    for l in range(len(interaction[k])):
                        m = far[far[k][l]].index(k)
                        interaction2[far[k][l]][m] = interaction[k][l].T

    def mcbh(self, onfly=False, verbose=False):
        """
        Converts current H2matrix representation to "mcbh" H2-type.

        Parameters
        ----------
        onfly : boolean
            If true, converts `mem_type` to "low", otherwise converts
            it to "full".
        verbose : boolean
            If true, outputs some additional information.
        """
        t0 = time()
        if self.h2_type == 'mcbh' and self.mem_type == 'low' and onfly:
            if verbose:
                print('Already on required representation')
            return
        if self.h2_type == 'mcbh' and self.mem_type == 'full' and not onfly:
            if verbose:
                print('Already on required representation')
            return
        if self.h2_type == 'mcbh' and self.mem_type == 'low':
            self._matrix()
            self.mem_type = 'full'
            if verbose:
                print('Computed interaction matrices in {} seconds'.format(
                    time()-t0))
            return
        if self.h2_type == 'mcbh' and self.mem_type == 'full':
            self.row_interaction = None
            self.col_interaction = None
            self.mem_type = 'low'
            if verbose:
                print('Removed interaction matrices')
            return
        tol = 1.05
        symmetric = self.problem.symmetric
        queue = self.problem.queue
        row = self.problem.row_tree
        col = self.problem.col_tree
        level_count = len(row.level)-1
        row_size = row.level[-1]
        col_size = col.level[-1]
        row_far = self.problem.row_far
        col_far = self.problem.col_far
        row_basis = self.row_basis
        col_basis = self.col_basis
        row_transfer = self.row_transfer
        col_transfer = self.col_transfer
        row_notransition = self.problem.row_notransition
        col_notransition = self.problem.col_notransition
        row_basis = [np.ndarray(0, dtype = np.uint64) for
                i in range(row_size)]
        if not symmetric:
            col_basis = [np.ndarray(0, dtype = np.uint64) for
                    i in range(col_size)]
        else:
            col_basis = row_basis
        self.row_basis = row_basis
        self.col_basis = col_basis
        if onfly:
            self.row_interaction = None
            self.col_interaction = None
            self.h2_type = 'mcbh'
            self.mem_type = 'low'
        else:
            self.h2_type = 'mcbh'
            self.mem_type = 'full'
        row_r = [0 for i in range(row_size)]
        col_r = [0 for i in range(col_size)]
        for i in range(level_count-1, -1, -1):
            for j in range(col.level[i], col.level[i+1]):
                if col_notransition[j]:
                    continue
                if col.child[j] == []:
                    if col_transfer[j].shape[0] == 0:
                        col_transfer[j] = np.eye(col_transfer[j].shape[1])
                    tmp = maxvol_qr(col_transfer[j], tol)
                    col_r[j] = col_transfer[j][tmp[0]]
                    col_transfer[j] = tmp[1]
                    col_basis[j] = col.index[j][tmp[0]]
                else:
                    s = []
                    s2 = []
                    ind = 0
                    if col_transfer[j].shape[0] == 0:
                        col_transfer[j] = np.eye(col_transfer[j].shape[1])
                    for k in col.child[j]:
                        p = col_r[k].shape[0]
                        s.append(col_r[k].dot(col_transfer[j][ind:ind+p]))
                        s2.append(col_basis[k])
                        ind += p
                    tmp = maxvol_qr(np.vstack(s), tol)
                    col_r[j] = np.vstack(s)[tmp[0]]
                    col_transfer[j] = tmp[1]
                    col_basis[j] = np.concatenate(s2)[tmp[0]]
            if i < level_count-1:
                for j in range(col.level[i+1], col.level[i+2]):
                    col_r[j] = 0
        for i in range(col.level[-3], col.level[-1]):
            col_r[i] = 0
        if not symmetric:
            for i in range(level_count-1, -1, -1):
                for j in range(row.level[i], row.level[i+1]):
                    if row_notransition[j]:
                        continue
                    if row.child[j] == []:
                        if row_transfer[j].shape[0] == 0:
                            row_transfer[j] = np.eye(row_transfer[j].shape[1])
                        tmp = maxvol_qr(row_transfer[j], tol)
                        row_r[j] = row_transfer[j][tmp[0]]
                        row_transfer[j] = tmp[1]
                        row_basis[j] = row.index[j][tmp[0]]
                    else:
                        s = []
                        s2 = []
                        ind = 0
                        if row_transfer[j].shape[0] == 0:
                            row_transfer[j] = np.eye(row_transfer[j].shape[1])
                        for k in row.child[j]:
                            p = row_r[k].shape[0]
                            s.append(row_r[k].dot(row_transfer[j][ind:ind+p]))
                            s2.append(row_basis[k])
                            ind += p
                        tmp = maxvol_qr(np.vstack(s), tol)
                        row_r[j] = np.vstack(s)[tmp[0]]
                        row_transfer[j] = tmp[1]
                        row_basis[j] = np.concatenate(s2)[tmp[0]]
                if i < level_count-1:
                    for j in range(row.level[i+1], row.level[i+2]):
                        row_r[j] = 0
            for i in range(row.level[-3], row.level[-1]):
                row_r[i] = 0
        if not onfly:
            self._matrix()
        if verbose:
            print('Converted in {} seconds'.format(time()-t0))

    def copy(self, verbose=False):
        """
        Copies all buffers into new instance of H2matrix.

        Uses `deepcopy` function of module `copy`.

        Parameters
        ----------
        verbose : boolean
            If true, shows copy time.
        """
        t0 = time()
        row_basis = copy.deepcopy(self.row_basis)
        row_transfer = copy.deepcopy(self.row_transfer)
        row_interaction = copy.deepcopy(self.row_interaction)
        row_close = copy.deepcopy(self.row_close)
        if not self.problem.symmetric:
            col_basis = copy.deepcopy(self.col_basis)
            col_transfer = copy.deepcopy(self.col_transfer)
            col_interaction = copy.deepcopy(self.col_interaction)
            col_close = copy.deepcopy(self.col_close)
        else:
            col_basis = row_basis
            col_transfer = row_transfer
            col_interaction = row_interaction
            col_close = row_close
        ans = H2matrix(self.problem, row_transfer, col_transfer,
                row_interaction, col_interaction, row_close, col_close,
                row_basis, col_basis)
        if verbose:
            print('Copied in {} seconds'.format(time()-t0))
        return ans

    def diffnorm(self, factor2=None, far_only=True):
        """
        Computes relative spectral distance from H2matrix.
        
        If `factor2` is not given, distance is measured to initial
        linear operator, represented by `problem` attribute. Otherwise,
        distance is measured to `factor2` operator with help of
        following methods, defined in `factor2` object: `dot`, `rdot`,
        `far_dot` and `far_rdot`. Meaning of this methods is the same,
        as meaning of methods of this object.

        If parameter `far_only` is True, measures relative error of
        approximation of far-field part only.

        Parameters
        ----------
        factor2 : Python object
            If not defined, this function returns relative spectral
            error of approximation by H2matrix. If defined, this
            method returns relative spectral distance from H2matrix
            to `factor2`
        far_only : boolean
            If true, measures distance only by far-field part.

        Returns
        -------
        float
            Relative spectral distance to initial operator or `factor2`
            object.
        """
        try:
            svdp
        except NameError:
            raise ImportError("No pypropack installed, cannot measure error.")
        if factor2 is None:
            factor2 = self.problem
        if far_only:
            linop_diff = la.LinearOperator(self.shape, matvec=lambda x:
                    factor2.far_dot(x)-self.far_dot(x), rmatvec=lambda x:
                    factor2.far_rdot(x)-self.far_rdot(x), dtype=self.dtype)
            s_diff = svdp(linop_diff, 1, compute_u=0, compute_v=0, kmax=100)
            linop_factor = la.LinearOperator(self.shape, matvec=self.far_dot,
                    rmatvec=self.far_rdot, dtype=self.dtype)
            s_factor = svdp(linop_factor, 1, compute_u=0, compute_v=0,
                    kmax=100)
        else:
            linop_diff = la.LinearOperator(self.shape, matvec=lambda x:
                        factor2.dot(x)-self.dot(x), rmatvec=lambda x:
                        factor2.rdot(x)-self.rdot(x), dtype=self.dtype)
            s_diff = svdp(linop_diff, 1, compute_u=0, compute_v=0, kmax=100)
            linop_factor = la.LinearOperator(self.shape, matvec=lambda x:
                    self.dot(x), rmatvec=lambda x:self.rdot(x),
                    dtype=self.dtype)
            s_factor = svdp(linop_factor, 1, compute_u=0, compute_v=0,
                    kmax=100)
        return s_diff[0][0]/s_factor[0][0]
