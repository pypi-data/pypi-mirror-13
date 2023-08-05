#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bilinear Bayer CFA Demosaicing
==============================

*Bayer* CFA (Colour Filter Array) bilinear demosaicing.

References
----------
.. [1]  Losson, O., Macaire, L., & Yang, Y. (2010). Comparison of color
        demosaicing methods. Advances in Imaging and Electron Physics, 162(C),
        173–265. doi:10.1016/S1076-5670(10)62005-8
"""

from __future__ import division, unicode_literals

import numpy as np
from scipy.ndimage.filters import convolve
from colour import tstack

from colour_demosaicing.bayer import masks_CFA_Bayer

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['demosaicing_CFA_Bayer_bilinear']


def demosaicing_CFA_Bayer_bilinear(CFA, pattern='RGGB'):
    """
    Returns the demosaiced *RGB* colourspace array from given *Bayer* CFA using
    bilinear interpolation.

    Parameters
    ----------
    CFA : array_like
        *Bayer* CFA.
    pattern : unicode, optional
        **{'RGGB', 'BGGR', 'GRBG', 'GBRG'}**
        Arrangement of the colour filters on the pixel array.

    Returns
    -------
    ndarray
        *RGB* colourspace array.

    Examples
    --------
    >>> CFA = np.array([[0.30980393, 0.36078432, 0.30588236, 0.3764706],
    ...                 [0.35686275, 0.39607844, 0.36078432, 0.40000001]])
    >>> demosaicing_CFA_Bayer_bilinear(CFA)
    array([[[ 0.69705884,  0.17941177,  0.09901961],
            [ 0.46176472,  0.4509804 ,  0.19803922],
            [ 0.45882354,  0.27450981,  0.19901961],
            [ 0.22941177,  0.5647059 ,  0.30000001]],
    <BLANKLINE>
           [[ 0.23235295,  0.53529412,  0.29705883],
            [ 0.15392157,  0.26960785,  0.59411766],
            [ 0.15294118,  0.4509804 ,  0.59705884],
            [ 0.07647059,  0.18431373,  0.90000002]]])
    >>> CFA = np.array([[0.3764706, 0.36078432, 0.40784314, 0.3764706],
    ...                 [0.35686275, 0.30980393, 0.36078432, 0.29803923]])
    >>> demosaicing_CFA_Bayer_bilinear(CFA, 'BGGR')
    array([[[ 0.07745098,  0.17941177,  0.84705885],
            [ 0.15490197,  0.4509804 ,  0.5882353 ],
            [ 0.15196079,  0.27450981,  0.61176471],
            [ 0.22352942,  0.5647059 ,  0.30588235]],
    <BLANKLINE>
           [[ 0.23235295,  0.53529412,  0.28235295],
            [ 0.4647059 ,  0.26960785,  0.19607843],
            [ 0.45588237,  0.4509804 ,  0.20392157],
            [ 0.67058827,  0.18431373,  0.10196078]]])
    """

    CFA = np.asarray(CFA)
    R_m, G_m, B_m = masks_CFA_Bayer(CFA.shape, pattern)

    H_G = np.asarray(
        [[0, 1, 0],
         [1, 4, 1],
         [0, 1, 0]]) / 4

    H_RB = np.asarray(
        [[1, 2, 1],
         [2, 4, 2],
         [1, 2, 1]]) / 4

    R = convolve(CFA * R_m, H_RB)
    G = convolve(CFA * G_m, H_G)
    B = convolve(CFA * B_m, H_RB)

    return tstack((R, G, B))
