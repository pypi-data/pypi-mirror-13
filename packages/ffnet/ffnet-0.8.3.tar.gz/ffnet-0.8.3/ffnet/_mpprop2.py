"""
Parallel training functions
"""
from fortran import _ffnet as netprop

# Data splitter function
def splitdata(N, nproc):
    """
    Creates splitters for dataset of length *N* for *nproc* processes.

    Splits to *nproc* equal data chunks.
    """
    n = N // nproc
    i = (nproc - N % nproc) * n
    idx = range(n, i, n) + range(i, N, n+1)
    idx1 = [0] + idx
    idx2 = idx + [N]
    return zip(idx1, idx2)

func = netprop.func
def procfunc(x, net, i, t):
    """
    Per process function netprop.func function
    """
    return func(x, net.conec, net.bconecno, net.units, net.inno, net.outno, i, t)
def mpfunc(x, pool, net, inp, trg, splitters):
    """
    Execute netprop.func in parallel on multiprocessing *pool*
    """
    res = []
    for splitter in splitters:
        s, e = splitter
        res += [pool.apply_async(procfunc, (x, net, inp[s:e], trg[s:e]))]
    return sum([r.get() for r in res])

grad = netprop.grad
def procgrad(x, net, i, t):
    """
    Per process function netprop.grad function
    """
    return grad(x, net.conec, net.bconecno, net.units, net.inno, net.outno, i, t)
def mpgrad(x, pool, net, inp, trg, splitters):
    """
    Execute netprop.grad in parallel on multiprocessing *pool*
    """
    res = []
    for splitter in splitters:
        s, e = splitter
        res += [pool.apply_async(procgrad, (x, net, inp[s:e], trg[s:e]))]
    return sum([r.get() for r in res])
