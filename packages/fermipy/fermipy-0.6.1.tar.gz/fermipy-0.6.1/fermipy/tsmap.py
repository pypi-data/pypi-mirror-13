from __future__ import absolute_import, division, print_function, \
    unicode_literals

import os
import copy
import itertools
import functools
from multiprocessing import Pool, cpu_count

import numpy as np
import warnings
import fermipy.config
import fermipy.defaults as defaults
import fermipy.utils as utils
from fermipy.utils import Map
from fermipy.logger import Logger
from fermipy.logger import logLevel

MAX_NITER = 100


def overlap_slices(large_array_shape, small_array_shape, position):
    """
    Modified version of `~astropy.nddata.utils.overlap_slices`.

    Get slices for the overlapping part of a small and a large array.

    Given a certain position of the center of the small array, with
    respect to the large array, tuples of slices are returned which can be
    used to extract, add or subtract the small array at the given
    position. This function takes care of the correct behavior at the
    boundaries, where the small array is cut of appropriately.

    Parameters
    ----------
    large_array_shape : tuple
        Shape of the large array.
    small_array_shape : tuple
        Shape of the small array.
    position : tuple
        Position of the small array's center, with respect to the large array.
        Coordinates should be in the same order as the array shape.

    Returns
    -------
    slices_large : tuple of slices
        Slices in all directions for the large array, such that
        ``large_array[slices_large]`` extracts the region of the large array
        that overlaps with the small array.
    slices_small : slice
        Slices in all directions for the small array, such that
        ``small_array[slices_small]`` extracts the region that is inside the
        large array.
    """
    # Get edge coordinates
    edges_min = [int(pos - small_shape // 2) for (pos, small_shape) in
                 zip(position, small_array_shape)]
    edges_max = [int(pos + (small_shape - small_shape // 2)) for
                 (pos, small_shape) in
                 zip(position, small_array_shape)]

    # Set up slices
    slices_large = tuple(slice(max(0, edge_min), min(large_shape, edge_max))
                         for (edge_min, edge_max, large_shape) in
                         zip(edges_min, edges_max, large_array_shape))
    slices_small = tuple(slice(max(0, -edge_min),
                               min(large_shape - edge_min, edge_max - edge_min))
                         for (edge_min, edge_max, large_shape) in
                         zip(edges_min, edges_max, large_array_shape))

    return slices_large, slices_small


def truncate_array(array1, array2, position):
    """Truncate array1 by finding the overlap with array2 when the
    array1 center is located at the given position in array2."""

    slices = []
    for i in range(array1.ndim):
        xmin = 0
        xmax = array1.shape[i]
        dxlo = array1.shape[i] // 2
        dxhi = array1.shape[i] - dxlo
        if position[i] - dxlo < 0:
            xmin = max(dxlo - position[i], 0)

        if position[i] + dxhi > array2.shape[i]:
            xmax = array1.shape[i] - (position[i] + dxhi - array2.shape[i])
            xmax = max(xmax, 0)
        slices += [slice(xmin, xmax)]

    return array1[slices]


def extract_array(array_large, array_small, position):
    shape = array_small.shape
    slices = []
    for i in range(array_large.ndim):

        if shape[i] is None:
            slices += [slice(0, None)]
        else:
            xmin = max(position[i] - shape[i] // 2, 0)
            xmax = min(position[i] + shape[i] // 2, array_large.shape[i])
            slices += [slice(xmin, xmax)]

    return array_large[slices]


def extract_large_array(array_large, array_small, position):
    large_slices, small_slices = overlap_slices(array_large.shape,
                                                array_small.shape, position)
    return array_large[large_slices]


def extract_small_array(array_small, array_large, position):
    large_slices, small_slices = overlap_slices(array_large.shape,
                                                array_small.shape, position)
    return array_small[small_slices]


def _cast_args_to_list(args):
    maxlen = max([len(t) if isinstance(t, list) else 1 for t in args])
    new_args = []
    for i, arg in enumerate(args):
        if not isinstance(arg, list):
            new_args += [[arg] * maxlen]
        else:
            new_args += [arg]

    return new_args


def _sum_wrapper(fn):
    """
    Wrapper to perform row-wise aggregation of list arguments and pass
    them to a function.  The return value of the function is summed
    over the argument groups.  Non-list arguments will be
    automatically cast to a list.
    """

    def wrapper(*args, **kwargs):
        v = 0
        new_args = _cast_args_to_list(args)
        for arg in zip(*new_args): v += fn(*arg, **kwargs)
        return v

    return wrapper


def _collect_wrapper(fn):
    """


    """

    def wrapper(*args, **kwargs):
        v = []
        new_args = _cast_args_to_list(args)
        for arg in zip(*new_args): v += [fn(*arg, **kwargs)]
        return v

    return wrapper


def _amplitude_bounds(counts, background, model):
    """
    Compute bounds for the root of `_f_cash_root_cython`.

    Parameters
    ----------
    counts : `~numpy.ndarray`
        Count map.
    background : `~numpy.ndarray`
        Background map.
    model : `~numpy.ndarray`
        Source template (multiplied with exposure).
    """

    if isinstance(counts, list):
        counts = np.concatenate([t.flat for t in counts])
        background = np.concatenate([t.flat for t in background])
        model = np.concatenate([t.flat for t in model])

    s_model = np.sum(model)
    s_counts = np.sum(counts)

    sn = background / model
    imin = np.argmin(sn)
    sn_min = sn.flat[imin]
    c_min = counts.flat[imin]

    b_min = c_min / s_model - sn_min
    b_max = s_counts / s_model - sn_min
    return max(b_min, 0), b_max


def _f_cash_root(x, counts, background, model):
    """
    Function to find root of. Described in Appendix A, Stewart (2009).

    Parameters
    ----------
    x : float
        Model amplitude.
    counts : `~numpy.ndarray`
        Count map slice, where model is defined.
    background : `~numpy.ndarray`
        Background map slice, where model is defined.
    model : `~numpy.ndarray`
        Source template (multiplied with exposure).
    """

    return np.sum(model * (counts / (x * model + background) - 1.0))


def _root_amplitude_brentq(counts, background, model, root_fn=_f_cash_root):
    """Fit amplitude by finding roots using Brent algorithm.

    See Appendix A Stewart (2009).

    Parameters
    ----------
    counts : `~numpy.ndarray`
        Slice of count map.
    background : `~numpy.ndarray`
        Slice of background map.
    model : `~numpy.ndarray`
        Model template to fit.

    Returns
    -------
    amplitude : float
        Fitted flux amplitude.
    niter : int
        Number of function evaluations needed for the fit.
    """
    from scipy.optimize import brentq

    # Compute amplitude bounds and assert counts > 0
    amplitude_min, amplitude_max = _amplitude_bounds(counts, background, model)

    if not sum_arrays(counts) > 0:
        return amplitude_min, 0

    args = (counts, background, model)

    if root_fn(0.0, *args) < 0:
        return 0.0, 1

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            result = brentq(root_fn, amplitude_min, amplitude_max, args=args,
                            maxiter=MAX_NITER, full_output=True, rtol=1E-4)
            return result[0], result[1].iterations
        except (RuntimeError, ValueError):
            # Where the root finding fails NaN is set as amplitude
            return np.nan, MAX_NITER


def poisson_log_like(counts, model):
    """Compute the Poisson log-likelihood function for the given
    counts and model arrays."""
    return model - counts * np.log(model)


def cash(counts, model):
    """Compute the Poisson log-likelihood function."""
    return 2 * poisson_log_like(counts, model)


def f_cash_sum(x, counts, background, model):
    return np.sum(f_cash(x, counts, background, model))


def f_cash(x, counts, background, model):
    """
    Wrapper for cash statistics, that defines the model function.

    Parameters
    ----------
    x : float
        Model amplitude.
    counts : `~numpy.ndarray`
        Count map slice, where model is defined.
    background : `~numpy.ndarray`
        Background map slice, where model is defined.
    model : `~numpy.ndarray`
        Source template (multiplied with exposure).
    """

    return 2.0 * poisson_log_like(counts, background + x * model)

def sum_arrays(x):
    return sum([t.sum() for t in x])    

def _ts_value(position, counts, background, model, C_0_map, method,logger=None):
    """
    Compute TS value at a given pixel position using the approach described
    in Stewart (2009).

    Parameters
    ----------
    position : tuple
        Pixel position.
    counts : `~numpy.ndarray`
        Count map.
    background : `~numpy.ndarray`
        Background map.
    model : `~numpy.ndarray`
        Source model map.

    Returns
    -------
    TS : float
        TS value at the given pixel position.
    """

    if not isinstance(position,list): position = [position]
    if not isinstance(counts,list): counts = [counts]
    if not isinstance(background,list): background = [background]
    if not isinstance(model,list): model = [model]
    if not isinstance(C_0_map,list): C_0_map = [C_0_map]

    extract_fn = _collect_wrapper(extract_large_array)
    truncate_fn = _collect_wrapper(extract_small_array)

    # Get data slices
    counts_ = extract_fn(counts, model, position)
    background_ = extract_fn(background, model, position)
    C_0_ = extract_fn(C_0_map, model, position)
    model_ = truncate_fn(model, counts, position)

#    C_0 = sum(C_0_).sum()
#    C_0 = _sum_wrapper(sum)(C_0_).sum()
    C_0 = sum_arrays(C_0_)    
    if method == 'root brentq':
        amplitude, niter = _root_amplitude_brentq(counts_, background_, model_,
                                                  root_fn=_sum_wrapper(
                                                      _f_cash_root))
    else:
        raise ValueError('Invalid fitting method.')

    if niter > MAX_NITER:
        #log.warning('Exceeded maximum number of function evaluations!')
        if logger is not None:
            logger.warning('Exceeded maximum number of function evaluations!')
        return np.nan, amplitude, niter

    with np.errstate(invalid='ignore', divide='ignore'):
        C_1 = _sum_wrapper(f_cash_sum)(amplitude, counts_, background_, model_)

    # Compute and return TS value
    return (C_0 - C_1) * np.sign(amplitude), amplitude, niter


class TSMapGenerator(fermipy.config.Configurable):
    defaults = dict(defaults.tsmap.items(),
                    fileio=defaults.fileio,
                    logging=defaults.logging)

    def __init__(self, config=None, **kwargs):
        fermipy.config.Configurable.__init__(self, config, **kwargs)
        self.logger = Logger.get(self.__class__.__name__,
                                 self.config['fileio']['logfile'],
                                 logLevel(self.config['logging']['verbosity']))

    def run(self, gta, prefix, **kwargs):

        models = kwargs.get('models', self.config['models'])

        if isinstance(models,dict):
            models = [models]

        o = []

        for m in models:
            self.logger.info('Generating TS map')
            self.logger.info(m)
            o += [self.make_ts_map(gta,prefix,copy.deepcopy(m),
                                   **kwargs)]

        return o

    def make_ts_map(self, gta, prefix, src_dict=None,**kwargs):
        """
        Make a TS map from a GTAnalysis instance.  The
        spectral/spatial characteristics of the test source can be
        defined with the src_dict argument.  By default this method
        will generate a TS map for a point source with an index=2.0
        power-law spectrum.

        Parameters
        ----------

        gta : `~fermipy.gtanalysis.GTAnalysis`
            Analysis instance.

        src_dict : dict or `~fermipy.roi_model.Source` object
            Dictionary or Source object defining the properties of the
            test source that will be used in the scan.

        """
        
        make_fits = kwargs.get('make_fits', True)
        exclude = kwargs.get('exclude', None)
        multithread = kwargs.get('multithread',self.config['multithread'])
        threshold = kwargs.get('threshold',1E-2)
        max_kernel_radius = kwargs.get('max_kernel_radius',
                                       self.config['max_kernel_radius'])

        erange = kwargs.get('erange', self.config['erange'])
        if erange is not None:            
            if len(erange) == 0: erange = [None,None]
            elif len(erange) == 1: erange += [None]            
            erange[0] = (erange[0] if erange[0] is not None 
                         else gta.energies[0])
            erange[1] = (erange[1] if erange[1] is not None 
                         else gta.energies[-1])
        else:
            erange = [gta.energies[0],gta.energies[-1]]
        
        # Put the test source at the pixel closest to the ROI center
        xpix, ypix = (np.round((gta.npix - 1.0) / 2.),
                      np.round((gta.npix - 1.0) / 2.))
        cpix = np.array([xpix, ypix])

        skywcs = gta._skywcs
        skydir = utils.pix_to_skydir(cpix[0], cpix[1], skywcs)

        if src_dict is None: src_dict = {}
        src_dict['ra'] = skydir.ra.deg
        src_dict['dec'] = skydir.dec.deg
        src_dict.setdefault('SpatialModel', 'PointSource')
        src_dict.setdefault('SpatialWidth', 0.3)
        src_dict.setdefault('Index', 2.0)
        src_dict.setdefault('Prefactor', 1E-13)

        counts = []
        background = []
        model = []
        c0_map = []
        eslices = []
        enumbins = []
        model_npred = 0
        for c in gta.components:

            imin = utils.val_to_edge(c.energies,erange[0])[0]
            imax = utils.val_to_edge(c.energies,erange[1])[0]

            eslice = slice(imin,imax)
            bm = c.model_counts_map(exclude=exclude).counts.astype('float')[eslice,...]
            cm = c.counts_map().counts.astype('float')[eslice,...]

            background += [bm]
            counts += [cm]
            c0_map += [cash(cm, bm)]
            eslices += [eslice]
            enumbins += [cm.shape[0]]

        self.logger.info(src_dict)
        gta.add_source('tsmap_testsource', src_dict, free=True,
                       init_source=False)
        src = gta.roi['tsmap_testsource']
        modelname = utils.create_model_name(src)
        for c, eslice in zip(gta.components,eslices):
            mm = c.model_counts_map('tsmap_testsource').counts.astype('float')[eslice,...]
            model_npred += np.sum(mm)
            model += [mm]
            
        gta.delete_source('tsmap_testsource')
        
        for i, mm in enumerate(model):

            dpix = 3
            for j in range(mm.shape[0]):

                ix,iy = np.unravel_index(np.argmax(mm[j,...]),mm[j,...].shape) 
                mx = mm[j,ix, :] > mm[j,ix,iy] * threshold
                my = mm[j,:, iy] > mm[j,ix,iy] * threshold
                dpix = max(dpix, np.round(np.sum(mx) / 2.))
                dpix = max(dpix, np.round(np.sum(my) / 2.))
                
            if max_kernel_radius is not None and \
                    dpix > int(max_kernel_radius/gta.components[i].binsz):
                dpix = int(max_kernel_radius/gta.components[i].binsz)

            xslice = slice(max(xpix-dpix,0),min(xpix+dpix+1,gta.npix))
            model[i] = model[i][:,xslice,xslice]
            
        ts_values = np.zeros((gta.npix, gta.npix))
        amp_values = np.zeros((gta.npix, gta.npix))
        
        wrap = functools.partial(_ts_value, counts=counts, 
                                 background=background, model=model,
                                 C_0_map=c0_map, method='root brentq')
#                                 logger=self.logger)

        positions = []
        for i,j in itertools.product(range(gta.npix),range(gta.npix)):
            p = [[k//2,i,j] for k in enumbins]
            positions += [p]

        if multithread:            
            pool = Pool()
            results = pool.map(wrap,positions)
            pool.close()
            pool.join()
        else:
            results = map(wrap,positions)

        for i, r in enumerate(results):
            ix = positions[i][0][1]
            iy = positions[i][0][2]
            ts_values[ix, iy] = r[0]
            amp_values[ix, iy] = r[1]

        files = {}

        if make_fits:

            ts_map_file = utils.format_filename(self.config['fileio']['workdir'],
                                                'tsmap_ts.fits',
                                                prefix=[prefix,modelname])

            sqrt_ts_map_file = utils.format_filename(self.config['fileio']['workdir'],
                                                     'tsmap_sqrt_ts.fits',
                                                     prefix=[prefix, modelname])

            npred_map_file = utils.format_filename(self.config['fileio']['workdir'],
                                                   'tsmap_npred.fits',
                                                   prefix=[prefix, modelname])

            amp_map_file = utils.format_filename(self.config['fileio']['workdir'],
                                                 'tsmap_amplitude.fits',
                                                 prefix=[prefix, modelname])

            utils.write_fits_image(ts_values, skywcs, ts_map_file)
            utils.write_fits_image(ts_values**0.5, skywcs, sqrt_ts_map_file)
            utils.write_fits_image(amp_values*model_npred, skywcs, npred_map_file)
            utils.write_fits_image(amp_values, skywcs, amp_map_file)

            files = {'ts': os.path.basename(ts_map_file),
                     'sqrt_ts': os.path.basename(sqrt_ts_map_file),
                     'npred': os.path.basename(npred_map_file),
                     'amplitude': os.path.basename(amp_map_file),
                     }

        o = {'name': '%s_%s' % (prefix, modelname),
             'src_dict': copy.deepcopy(src_dict),
             'files': files,
             'ts': Map(ts_values, skywcs),
             'sqrt_ts': Map(ts_values**0.5, skywcs),
             'npred': Map(amp_values*model_npred, skywcs),
             'amplitude': Map(amp_values, skywcs),
             }

        return o

