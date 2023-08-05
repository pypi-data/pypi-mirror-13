import sys
import numpy as np
from numpy.ctypeslib import ndpointer
import networkx as nx
from ctypes import *
import ctypes.util
import itertools


__all__ = ['tacsim_in_C', 'tacsim_self_in_C']


## Find and load tacsim library
tacsimlib = ctypes.util.find_library('tacsim')
if not tacsimlib:
    raise "Can't find libtacsim. Please install it first."
    sys.exit(-1)

libc = CDLL(tacsimlib, mode=ctypes.RTLD_GLOBAL)


def graph_properties(G, node_attribute='weight', edge_attribute='weight'):
    nodes = G.nodes()
    edges = G.edges()
    V = len(nodes)
    E = len(edges)
    nnadj = np.zeros((V, V), dtype=np.int)
    nnadj.fill(-1)
    node_weight_vec = np.ones(V, dtype=np.double)
    edge_weight_vec = np.ones(E, dtype=np.double)

    node_id_lookup_tbl = {}
    for i, n in enumerate(nodes):
        node_id_lookup_tbl[n] = i
        node_weight_vec[i] = G.node[n][node_attribute]

    edges = [(node_id_lookup_tbl[e[0]], node_id_lookup_tbl[e[1]], e[2]) for e in G.edges(data=True)]
    sorted(edges, key=lambda x: (x[0], x[1]))

    for i in range(len(edges)):
        src, dst, weight = edges[i]
        nnadj[src][dst] = i
        edge_weight_vec[i] = weight[edge_attribute]

    return nnadj, node_weight_vec, edge_weight_vec, V, E


def matrix_to_cpointer(arr, shape, dtype=c_double):
    row, col = shape
    DTARR = dtype * row
    PTR_DT = POINTER(dtype)
    PTR_DTARR = PTR_DT * col

    ptr = PTR_DTARR()
    for i in range(row):
        ptr[i] = DTARR()
        for j in range(col):
            ptr[i][j] = arr[i][j]

    return ptr

def vector_to_cpointer(vec, vlen, dtype=c_double):
    DTARR = dtype * vlen
    ptr = DTARR()
    for i in range(vlen):
        ptr[i] = vec[i]
    return ptr


def cpointer_to_matrix(ptr, shape):
    mat = np.empty(shape)
    for i in range(shape[0]):
        for j in range(shape[1]):
            mat[i][j] = ptr[i][j]
    return mat


def cpointer_to_ndarray(ptr, size, dtype, shape):
    """ Reverse of ndarray.ctypes.data_as. There are still
        some problems to use this method.
    """
    buf = np.core.multiarray.int_asbuffer(
        ctypes.addressof(ptr.contents), np.dtype(dtype).itemsize * size)
    arr = np.ndarray(shape, dtype=dtype, buffer=buf)
    return arr


def tacsim_in_C(G1, G2, node_attribute='weight', edge_attribute='weight', max_iter=100, eps=1e-4, tol=1e-6):
    ## Calculate similarity of two attributed graphs
    calculate_tacsim = libc.calculate_tacsim
    calculate_tacsim.argtypes = [
        POINTER(POINTER(c_int)),
        POINTER(c_double),
        POINTER(c_double), c_int, c_int,
        POINTER(POINTER(c_int)),
        POINTER(c_double),
        POINTER(c_double), c_int, c_int,
        POINTER(POINTER(POINTER(c_double))),
        POINTER(POINTER(POINTER(c_double))),
        c_int, c_double, c_double
    ]
    calculate_tacsim.restype = c_int

    nnadj, nwgt, ewgt, nlen, elen = graph_properties(G1, node_attribute, edge_attribute)
    nnadj2, nwgt2, ewgt2, nlen2, elen2 = graph_properties(G2, node_attribute, edge_attribute)

    nsim = POINTER(POINTER(c_double))()
    esim = POINTER(POINTER(c_double))()

    calculate_tacsim(
        matrix_to_cpointer(nnadj, (nlen, nlen), dtype=c_int),
        vector_to_cpointer(nwgt, nlen, dtype=c_double),
        vector_to_cpointer(ewgt, elen, dtype=c_double),
        c_int(nlen), c_int(elen),
        matrix_to_cpointer(nnadj2, (nlen2, nlen2), dtype=c_int),
        vector_to_cpointer(nwgt2, nlen2, dtype=c_double),
        vector_to_cpointer(ewgt2, elen2, dtype=c_double),
        c_int(nlen2), c_int(elen2),
        byref(nsim), byref(esim),
        c_int(max_iter), c_double(eps), c_double(tol)
    )

    nsim2 = cpointer_to_matrix(nsim, (nlen, nlen2))
    esim2 = cpointer_to_matrix(esim, (elen, elen2))

    return nsim2, esim2


def tacsim_self_in_C(G, node_attribute='weight', edge_attribute='weight', max_iter=100, eps=1e-4, tol=1e-6):
    ## Calculate self-similarity of an attributed graph
    calculate_tacsim_self = libc.calculate_tacsim_self
    calculate_tacsim_self.argtypes = [
        POINTER(POINTER(c_int)),
        POINTER(c_double),
        POINTER(c_double), c_int, c_int,
        POINTER(POINTER(POINTER(c_double))),
        POINTER(POINTER(POINTER(c_double))),
        c_int, c_double, c_double
    ]
    calculate_tacsim_self.restype = c_int

    # Convert graph attributes to ctypes
    nnadj, nwgt, ewgt, nlen, elen = graph_properties(G, node_attribute, edge_attribute)

    nsim = POINTER(POINTER(c_double))()
    esim = POINTER(POINTER(c_double))()

    calculate_tacsim_self(
        matrix_to_cpointer(nnadj, (nlen, nlen), dtype=c_int),
        vector_to_cpointer(nwgt, nlen, dtype=c_double),
        vector_to_cpointer(ewgt, elen, dtype=c_double),
        c_int(nlen), c_int(elen),
        byref(nsim), byref(esim),
        c_int(max_iter), c_double(eps), c_double(tol)
    )

    nsim2 = cpointer_to_matrix(nsim, (nlen, nlen))
    esim2 = cpointer_to_matrix(esim, (elen, elen))

    return nsim2, esim2


if __name__ == '__main__':
    G1 = nx.DiGraph()
    G1.add_weighted_edges_from([(1,0,8), (0,2,12), (1,2,10), (2,3,15)])
    G1.node[0]['weight'] = 1
    G1.node[1]['weight'] = 1
    G1.node[2]['weight'] = 5
    G1.node[3]['weight'] = 1

    G2 = nx.DiGraph()
    G2.add_weighted_edges_from([(0,1,15), (1,2,10)])
    G2.node[0]['weight'] = 1
    G2.node[1]['weight'] = 3
    G2.node[2]['weight'] = 1

    print tacsim_in_C(G1, G2)

    print tacsim_self_in_C(G1)

