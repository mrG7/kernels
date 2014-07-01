from libcpp.vector cimport vector
from libcpp.utility cimport pair
from libcpp.string cimport string
from libcpp.map cimport map
from libc.stddef cimport size_t

from microscopes.cxx.mixture._model_h cimport state
from microscopes.cxx.common._typedefs_h cimport scalar_1d_float_fn
from microscopes.cxx.common._dataview_h cimport dataview
from microscopes.cxx.common._random_fwd_h cimport rng_t

cdef extern from "microscopes/kernels/slice.hpp" namespace "microscopes::kernels::slice":
    ctypedef map[string, pair[scalar_1d_float_fn, float]] slice_t
    void hp(state &, vector[pair[size_t, slice_t]] &, rng_t &) except +
    float sample(scalar_1d_float_fn fn, float, float, rng_t &) except + 
