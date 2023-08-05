#cython: cdivision=True
#cython: boundscheck=False
#cython: nonecheck=False
#cython: wraparound=False
import numpy as np

cimport numpy as cnp
cimport cython

from libc.math cimport abs, fabs, sqrt, ceil, atan2, M_PI
from libc.stdlib cimport rand
import logging as _logging

_logger = _logging.getLogger(__name__)


cdef double PI_2 = 1.5707963267948966
cdef double NEG_PI_2 = -PI_2


def hough_ellipse(cnp.ndarray img, int threshold=4, accuracy=None,
                  xmean=None, ymean=None,
                  int min_size=4, max_size=None):
    """Perform an elliptical Hough transform.
    Parameters
    ----------
    img : (M, N) ndarray
        Input image with nonzero values representing edges.
    threshold: int, optional (default 4)
        Accumulator threshold value.
    accuracy : double, optional (default 1)
        Bin size on the minor axis used in the accumulator.
    min_size : int, optional (default 4)
        Minimal major axis length.
    max_size : int, optional
        Maximal minor axis length. (default None)
        If None, the value is set to the half of the smaller
        image dimension.
    Returns
    -------
    result : ndarray with fields [(accumulator, y0, x0, a, b, orientation)]
          Where ``(yc, xc)`` is the center, ``(a, b)`` the major and minor
          axes, respectively. The `orientation` value follows
          `skimage.draw.ellipse_perimeter` convention.
    Examples
    --------
    >>> img = np.zeros((25, 25), dtype=np.uint8)
    >>> rr, cc = ellipse_perimeter(10, 10, 6, 8)
    >>> img[cc, rr] = 1
    >>> result = hough_ellipse(img, threshold=8)
    [(10, 10.0, 8.0, 6.0, 0.0, 10.0)]
    Notes
    -----
    The accuracy must be chosen to produce a peak in the accumulator
    distribution. In other words, a flat accumulator distribution with low
    values may be caused by a too low bin size.
    References
    ----------
    .. [1] Xie, Yonghong, and Qiang Ji. "A new efficient ellipse detection
           method." Pattern Recognition, 2002. Proceedings. 16th International
           Conference on. Vol. 2. IEEE, 2002
    """
    if img.ndim != 2:
            raise ValueError('The input image must be 2D.')

    cdef Py_ssize_t[:, ::1] pixels = np.row_stack(np.nonzero(img))
    cdef Py_ssize_t num_pixels = pixels.shape[1]
    cdef list acc = list()
    cdef list myacc = list()
    cdef list results = list()
    # cdef double bin_size = accuracy ** 2
    cdef double bin_size
    cdef int autobin
    if accuracy is None:
        autobin = 1
    else:
        autobin=0
        bin_size = accuracy

    cdef int max_b_squared
    if max_size is None:
        if img.shape[0] < img.shape[1]:
            max_b_squared = np.round(0.5 * img.shape[0]) ** 2
        else:
            max_b_squared = np.round(0.5 * img.shape[1]) ** 2
    else:
        max_b_squared = max_size**2

    cdef Py_ssize_t p1, p2, p3, p1x, p1y, p2x, p2y, p3x, p3y
    # cdef double xc, yc, a, b, d, k
    cdef double cos_tau_squared, b_squared, f_squared, orientation, count_density

    cdef list ind1 = list()
    cdef list ind2 = list()

    if xmean is not None and ymean is not None:
        pymean = xmean
        pxmean = ymean
    else:
        pymean = np.mean(pixels[0, :])
        pxmean = np.mean(pixels[1, :])

    # print('Mean: ({}, {})'.format(pxmean, pymean))

    for p1 in range(num_pixels):
        if (pixels[1, p1] - pxmean)**2 < 2:
            if pixels[0, p1] < pymean:
                ind1.append(p1)
                # print('Left point coords: ({}, {})'.format(pixels[1, p1], pixels[0, p1]))

            if pixels[0, p1] > pymean:
                ind2.append(p1)
                # print('Right point coords: ({}, {})'.format(pixels[1, p1], pixels[0, p1]))

    for p1 in ind1:
        p1x = pixels[1, p1]
        p1y = pixels[0, p1]

        for p2 in ind2:
            p2x = pixels[1, p2]
            p2y = pixels[0, p2]

            if p1x == p2x:
            
                acc = []
                myacc = []

                # Candidate: center (xc, yc) and main axis a
                a = 0.5 * sqrt((p1x - p2x)**2 + (p1y - p2y)**2)
                if a > 0.5 * min_size:
                    xc = 0.5 * (p1x + p2x)
                    yc = 0.5 * (p1y + p2y)

                    for p3 in range(num_pixels):
                        p3x = pixels[1, p3]
                        p3y = pixels[0, p3]

                        d = sqrt((p3x - xc)**2 + (p3y - yc)**2)
                        if d > min_size:
                            f_squared = (p3x - p1x)**2 + (p3y - p1y)**2
                            cos_tau_squared = ((a**2 + d**2 - f_squared)
                                               / (2 * a * d))**2
                            # Consider b2 > 0 and avoid division by zero
                            k = a**2 - d**2 * cos_tau_squared
                            if k > 0 and cos_tau_squared < 1:
                                b_squared = a**2 * d**2 * (1 - cos_tau_squared) / k
                                # b2 range is limited to avoid histogram memory
                                # overflow
                                if b_squared <= max_b_squared:
                                    acc.append(b_squared)

                    if len(acc) > threshold:
                        # bins = np.arange(0, np.max(acc) + bin_size, bin_size)
                        # Remove things 3sig away from mean
                        mean = np.mean(acc)
                        sig = np.std(acc)
                        filt1 = (acc-mean) < 5*sig

                        for i, val in enumerate(acc):
                            if filt1[i] and val > 0.0:
                                myacc.append(val)

                        if len(myacc) > threshold:
                            # Estimate ideal bin width
                            if autobin:
                                # _logger.debug('Autobinning')
                                # print('Autobinning')
                                iqr = np.subtract(*np.percentile(myacc, [75, 25]))
                                num_myacc = np.size(myacc)
                                bin_size = 2*iqr/(num_myacc**(0.3333333333333333))
                                autobin = 1
                            else:
                                autobin = 0

                            bins = np.arange(np.min(myacc), np.max(myacc) + bin_size, bin_size)
                            
                            hist, bin_edges = np.histogram(myacc, bins=bins)
                            hist_max = np.max(hist)
                            count_density = hist_max / bin_size
                            # print(hist_max)
                            if hist_max > threshold:
                                orientation = -atan2(p2x - p1x, p2y - p1y)
                                b = sqrt(bin_edges[hist.argmax()])
                                # print('b: {}'.format(b))
                                _logger.debug('b: {}'.format(b))
                                # to keep ellipse_perimeter() convention
                                if a < b:
                                    a, b = b, a
                                    orientation = orientation + (M_PI / 2.)
                                    if orientation > M_PI:
                                        orientation = orientation - M_PI

                                results.append((count_density, hist_max, # Accumulator
                                                yc, xc,
                                                p1x, p1y,
                                                p2x, p2y,
                                                a, b,
                                                bin_size,
                                                orientation, hist, bin_edges, np.array(myacc), autobin))
                            acc = []
                            myacc = []

    return np.array(results, dtype=[('count_density', np.double),
                                    ('hist_max', np.intp),
                                    ('yc', np.double),
                                    ('xc', np.double),
                                    ('p1x', np.double),
                                    ('p1y', np.double),
                                    ('p2x', np.double),
                                    ('p2y', np.double),
                                    ('a', np.double),
                                    ('b', np.double),
                                    ('bin_size', np.double),
                                    ('orientation', np.double),
                                    ('hist', object),
                                    ('bin_edges', object),
                                    ('myacc', object),
                                    ('autobin', np.intp)
                                    ])
