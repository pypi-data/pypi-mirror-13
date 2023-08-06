# Copyright (c) 2016, Imperial College London
# Copyright (c) 2016, Ghislain Antony Vaillant
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the BSD license. See the accompanying LICENSE file
# or read the terms at https://opensource.org/licenses/BSD-3-Clause.

from __future__ import absolute_import

from ._wrappers import (PRE_PHI_HUT, PRE_PSI, PRE_FULL_PSI, nfft_create_plan,
                        nfft_destroy_plan, nfft_precompute_plan,
                        nfft_execute_forward, nfft_execute_adjoint,
                        nfft_execute_forward_direct,
                        nfft_execute_adjoint_direct,)
from enum import IntEnum, unique
import numpy

__all__ = ("Flag", "Plan")


@unique
class Flag(IntEnum):
    PRE_PHI_HUT = PRE_PHI_HUT
    PRE_PSI = PRE_PSI
    PRE_FULL_PSI = PRE_FULL_PSI


class Plan(object):
  
    """The NFFT plan class."""
    
    def __init__(self, N, M, n=None, m=6, flags=None, *args, **kwargs):
        "Instantiate the NFFT plan."        
        d = len(N)
        n = n if n is not None else tuple([2 * Nt for Nt in N])
        flags = flags if flags is not None else (0,)
        # Create plan handle.
        self.__handle = nfft_create_plan(N, M, n, m, flags)
        self.__f_hat = numpy.empty(N, dtype=numpy.complex128)
        self.__f = numpy.empty(M, dtype=numpy.complex128)
        if d == 1:
            self.__x = numpy.empty(M, dtype=numpy.float64)
        else:
            self.__x = numpy.empty([M, d], dtype=numpy.float64)

    def __del__(self):
        nfft_destroy_plan(self.__handle)

    def forward(self, direct=False):
        """Compute and return the forward transform."""
        if direct:
            self.execute_forward_direct()
        else:
            self.execute_forward()
        return self.__f

    def execute_forward(self):
        """Perform the foward transform."""
        nfft_execute_forward(self.__handle, self.__f_hat, self.__f)

    def execute_forward_direct(self):
        """Perform the foward transform."""
        nfft_execute_forward_direct(self.__handle, self.__f_hat, self.__f)

    def adjoint(self, direct=False):
        """Compute and return the adjoint transform."""
        if direct:
            self.execute_adjoint_direct()
        else:
            self.execute_adjoint()
        return self.__f_hat

    def execute_adjoint(self):
        """Perform the adjoint transform."""
        nfft_execute_adjoint(self.__handle, self.__f, self.__f_hat)

    def execute_adjoint_direct(self):
        """Perform the adjoint transform using direct computation."""
        nfft_execute_adjoint_direct(self.__handle, self.__f, self.__f_hat)

    def precompute(self):
        "Precompute the plan."
        nfft_precompute_plan(self.__handle, self.__x)

    @property
    def f_hat(self):
        return self.__f_hat

    @property
    def f(self):
        return self.__f

    @property
    def x(self):
        return self.__x
