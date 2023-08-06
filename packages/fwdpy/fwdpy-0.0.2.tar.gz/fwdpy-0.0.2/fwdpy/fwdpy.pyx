# distutils: language = c++
# distutils: sources = fwdpy/fwdpy/sample.cc fwdpy/fwdpy/neutral.cc fwdpy/fwdpy/deps.cc fwdpy/fwdpy/evolve_regions.cc fwdpy/fwdpy/trajectories.cc
from libcpp.vector cimport vector
from libcpp.utility cimport pair
from libcpp.string cimport string

## for DataFrame
import pandas

include "classes.pyx"
include "evolve_simple.pyx"
include "sampling.pyx"
include "evolve_regions.pyx"
include "regions.pyx"
include "slim.pyx"
include "trajectories.pyx"
include "copy.pyx"
include "views.pyx"

def pkg_version():
    """
    Return version numbers of this package

    This function is very handy when reporting bugs!

    :returns: dict
    """
    cdef vector[string] v = fwdpy_version()
    return ({'fwdpy':v[0]})

def cite():
    """
    Returns how to cite this package
    """
    fwdpy_citation()
