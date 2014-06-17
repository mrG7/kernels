import numpy as np
from microscopes.models.mixture.dp import DPMM
from distributions.dbg.random import sample_discrete_log

class numpy_iter(object):
    def __init__(self, Y, inds=None):
        self._Y = Y
        self._i = 0
        self._N = Y.shape[0]
        self._inds = inds

    def __iter__(self):
        return self

    def next(self):
        if self._i == self._N:
            raise StopIteration()
        i = self._inds[self._i] if self._inds is not None else self._i
        self._i += 1
        return i, Y[i]

class numpy_dataset(object):
    def __init__(self, Y):
        self._Y = Y

    def data(self, shuffle=False):
        inds = np.random.permutation(self.size()) if shuffle else None
        return numpy_iter(self._Y, inds)

    def size(self):
        return self._Y.shape[0]

def griddy_gibbs(m, dataset, niters_gibbs, niters_grid, hyperpriors, hypergrids):
    for _ in xrange(niters_grid):
        gibbs(m, dataset, niters_gibbs)
        # XXX: this can be done in parallel
        for fi, (hprior, hgrid) in enumerate(zip(hyperpriors, hypergrids)):
            scores = np.zeros(len(hgrid))
            for i, hp in enumerate(hgrid):
                m.set_feature_hp(fi, hp)
                scores[i] = hprior(hp) + m.score_data(fi)
            choice = sample_discrete_log(scores)
            m.set_feature_hp(fi, hgrid[choice])

def gibbs(m, dataset, niters):
    empty_gids = list(m.empty_groups())
    empty_gid = empty_gids[0] if len(empty_gids) else m.create_group()
    for _ in xrange(niters):
        for ei, yi in dataset.data(shuffle=True):
            gid = m.remove_entity_from_group(ei, yi)
            if not m.nentities_in_group(gid):
                m.delete_group(gid)
            idmap, scores = m.score_value(yi)
            gid = idmap[sample_discrete_log(scores)]
            m.add_entity_to_group(gid, ei, yi)
            if gid == empty_gid:
                empty_gid = m.create_group()

if __name__ == '__main__':
    from distributions.dbg.models import bb
    import itertools as it
    import math
    def mk_bb_hyperprior_grid(n):
        return tuple({'alpha':alpha, 'beta':beta} for alpha, beta in it.product(np.linspace(0.01, 10.0, n), repeat=2))
    def bb_hyperprior_pdf(hp):
        alpha, beta = hp['alpha'], hp['beta']
        # http://iacs-courses.seas.harvard.edu/courses/am207/blog/lecture-9.html
        return math.pow(alpha + beta, -2.5)
    N = 10
    D = 5
    dpmm = DPMM(N, {'alpha':2.0}, [bb]*D, [{'alpha':1.0, 'beta':1.0}]*D)
    Y = np.vstack(dpmm.sample(N))
    dataset = numpy_dataset(Y)
    dpmm.bootstrap(dataset.data())
    #gibbs(dpmm, dataset, 10)
    griddy_gibbs(dpmm, dataset, 10, 10, (bb_hyperprior_pdf, bb_hyperprior_pdf), (mk_bb_hyperprior_grid(5), mk_bb_hyperprior_grid(5)))