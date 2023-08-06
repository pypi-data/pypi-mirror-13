import numpy 
from numpy import amax             as numpy_amax
from numpy import amin             as numpy_amin
from numpy import argsort          as numpy_argsort
from numpy import average          as numpy_average
from numpy import broadcast_arrays as numpy_broadcast_arrays
from numpy import copy             as numpy_copy
from numpy import empty            as numpy_empty
from numpy import expand_dims      as numpy_expand_dims
from numpy import multiply         as numpy_multiply
from numpy import ones             as numpy_ones
from numpy import reshape          as numpy_reshape
from numpy import resize           as numpy_resize
from numpy import result_type      as numpy_result_type
from numpy import shape            as numpy_shape
from numpy import sum              as numpy_sum

from numpy.ma import array       as numpy_ma_array
from numpy.ma import average     as numpy_ma_average
from numpy.ma import is_masked   as numpy_ma_is_masked
from numpy.ma import masked_all  as numpy_ma_masked_all

from copy      import deepcopy
from itertools import izip
from operator  import mul as operator_mul

from ..ancillaryvariables import AncillaryVariables
from ..cellmethods        import CellMethods
from ..constants          import masked as cf_masked
from ..coordinate         import Coordinate, DimensionCoordinate
from ..coordinatebounds   import CoordinateBounds
from ..field              import Field
from ..fieldlist          import FieldList
from ..functions          import broadcast_array
from ..variable           import Variable

from ..data.data import Data

#_debug = True
_debug = False

def collapse(fields, method, axes=None, weights=None, biased=True,
             ignore_size1=True, squeeze=False, **kwargs):
    '''

Return new fields with dimensions collapsed by statistical operations.

In all cases, the presence of missing data in an input field's data
array is accounted for during the collapse.

The following collapse methods are available over any subset of the
fields' axes, where the methods are defined exactly as for CF cell
methods:

==================  ==============================  =======================
Method              Description                     Options
==================  ==============================  =======================
min                 Minima over the specified axes
                                                                                    
max                 Maxima over the specified axes

mid_range           Means of the minima and maxima  
                    over the specified axes

sum                 Sums over the specified axes     

mean                Means over the specified axes   Weighted or unweighted
                                                                                    
standard_deviation  Standard deviations over the    Weighted or unweighted,
                    specified axes                  biased or unbiased

variance            Variances over the specified    Weighted or unweighted,
                    axes                            biased or unbiased
==================  ==============================  =======================

:Parameters:

    fields : (sequence of) cf.Field or cf.FieldList
        The field or fields to be collapsed.

    method : str or CellMethods
        Define the collapse method (or methods). There are two ways of
        setting the collapse method:

           * A string containing a single method (such as ``'min'``).
           
             - The method is one of the available CF cell methods.

             - All of the dimensions specified by the *axes* parameter
               are collapsed simultaneously with this method.                 
        ..

           * A CF cell methods-like string (such as ``'time: max'`` or
             ``'time: max dim0: mean 2: min'``) or a `cf.CellMethods`
             object equivalent to such a string.
           
             - Specifies both collapse methods and the axes to apply
               them to.

             - Each method is one of the available CF cell
               methods. The axes are interpreted as for the *axes*
               parameter.

             - When multiple cell methods are specified, each collapse
               is carried out independently and in the order that they
               are given. The *axes* parameter must not be set.

    axes : (sequence of) int or str, optional
        The axis or axes which are to be simultaneously collapsed with
        the method specified by the *method* parameter. May be any
        one, or any combination of:

           * A dimension identity, as a defined by an appropriate
             coordinate's `~Coordinate.identity` method (such as
             ``'time'``).
             
           * The integer position of a dimension in the field's data
             array (such as ``2``).
             
           * The internal name of a dimension in the field's domain
             (such as ``'dim0'``).

        By default all dimensions with size greater than 1 are
        collapsed, unless the *method* is a CF cell methods-like
        string or a `cf.CellMethods` object, in which case the
        collapse axes are already specified and the *axes* parameter
        must not be set.

    weights : str or tuple, optional
        Specify the weights to be used in the collapse. One of:

           =============  ===============================================
           weights        Description
           =============  ===============================================
           `None`         Perform an unweighted collapse (this is the
                          default).
 
           ``'equal'``    Perform an unweighted collapse.
           
           `!tuple`       The axes for which non-equal weights are to
                          be computed. Each axis is specified by one
                          of:

                            * The identity of one of its one
                              dimensional coordinate objects (such as
                              ``'time'``)
                            
                            * A coordinate object type (one of
                              ``'T'``, ``'X'``, ``'Y'`` or ``'Z'``)
                            
                            * An axis or coordinate object domain
                              identifier (such as ``'dim1'``).

                          If cell measures are available for any
                          specified axes then they will constitute the
                          weights, otherwise weights are based on each
                          axis's dimension coordinate object.
                          
                          In general, dimension coordinate object
                          weights will be linear, with the exception
                          of a latitude axis, for which linear weights
                          of the sine of the coordinate values are
                          calculated.

                            Example: To specify latitude/longitude area
                            weights you could set ``weights=('X', 'Y')``.

                          If only coordinate object types are
                          specified, then they may be given as a
                          concatenated string instead of a tuple.

                            Example: ``weights=('X', 'T')`` is
                            equivalent to ``weights='XT'``.       
           =============  ===============================================

        .. note:: The interface for the specification of weights is
                  currently limited (version 0.9.8). A fully general
                  API for specifiying weights is under development.

    biased : bool, optional
        If False then calculate unbiased statisics where
        applicable. By default biased statistics are calculated.

    ignore_size1 : bool, optional
        If False then raise a ValueError if a dimension to be
        collapsed has size 1, regardless of whether or not it spans
        the data array. By default size 1 collapse dimensions are
        ignored, regardless of whether or not they span the data
        array.

    squeeze : bool, optional
        If True then remove collapsed dimensions from the output data
        array. By default the output data array retains collapsed
        dimensions with size 1 if they were spanned by the original
        data array. It is not possible to remove collapsed dimensions
        when mutliple methods have been specified.

:Returns:

   out : cf.Field or cf.FieldList
        The collapsed fields.

**Examples**

>>> g = cf.collapse(f, 'max')
>>> g = cf.collapse(f, 'min', axes=[2, 1])
>>> g = cf.collapse(f, 'sum', axes='dim2')
>>> g = cf.collapse(f, 'mid_range', axes=('latitude', 0, dim2'))
>>. g = cf.collapse(f, 'mean', axes='latitude', weights=None)
>>> g = cf.collapse(f, 'mean', axes='longitude', weights=None)
>>> g = cf.collapse(f, 'mean', axes=['longitude', 'latitude'], weights=None)
>>> g = cf.collapse(f, 'standard_deviation', weights=None)
>>> g = cf.collapse(f, 'variance', weights=None, biased=False)
>>> g = cf.collapse(f, 'mean', axes='latitude')
>>> g = cf.collapse(f, 'mean', axes='longitude')
>>> g = cf.collapse(f, 'mean', axes=['longitude', 'latitude'])
>>> g = cf.collapse(f, 'variance')
>>> g = cf.collapse(f, 'standard_deviation', biased=False)
>>> g = cf.collapse(f, 'longitude: mean latitude: max')

>>> weights = {'time': None,
...            (2, 'dim1'): numpy.arange(45).reshape(5, 9))
>>> g = cf.collapse(f, 'mean', weights=weights)

'''
    # ---------------------------------------------------------------
    # Flatten an input list or tuple of fields and field lists into a
    # single field list
    # ---------------------------------------------------------------
    if isinstance(fields, (list, tuple)):
        fields = [f for element in fields for f in element]

    # If method is a cell methods string (such as 'area: mean time:
    # max') then convert it to a CellMethods object
    if ':' in method:
        method = CellMethods(method)

    # ================================================================
    # If method is a CellMethods object then process its methods one
    # by one with recursive calls and then return.
    # ================================================================
    if isinstance(method, CellMethods):
        if squeeze:            
            raise ValueError(
"Can't collapse: Can't squeeze collapsed axes with multiple methods")

        if axes is not None:
            raise ValueError(
                "Can't collapse: Can't set both axes and cell methods")

        methods = list(method.method)
        axes    = list(method.names)
        for name, m in zip(axes, methods):
            if None in name:
                raise ValueError(
                    "Can't collapse: Invalid '%s' cell method name: %s" %
                    (m, None))
        #--- End: if

        # Collapse according to each cell method in turn with
        # recursive calls
        new = fields

        while methods:
            new = collapse(new, methods.pop(0), axes=axes.pop(0), weights=weights, 
                           biased=biased, ignore_size1=ignore_size1,
                           squeeze=False)
        #--- End: while

        return new
    #--- End: if

    # ================================================================
    # Still here? Then method is a string describing a single method
    # (e.g. 'mean')
    # ================================================================
    out = FieldList()

    weights_in = deepcopy(weights)

    for f in fields:
        new = f.copy()

        # ------------------------------------------------------------
        # Find which axes have been requested for callapsing
        # ------------------------------------------------------------
        domain = new.domain
        all_collapse_axes = domain.axes(axes, **kwargs)

        if not all_collapse_axes:
            # --------------------------------------------------------
            # Requested axes do not exist in field's domain
            # --------------------------------------------------------
            out.append(new)
            continue

        # ------------------------------------------------------------
        # Find which axes actually need collapsing in the data array
        # ------------------------------------------------------------
        axes_sizes = domain.dimension_sizes
        data_axes  = domain.data_axes()
        collapse_axes = [axis for axis in all_collapse_axes 
                         if axis in data_axes and axes_sizes[axis] > 1]

        if not collapse_axes:
            # --------------------------------------------------------
            # All collapse axes in the data array are size 1
            # --------------------------------------------------------
            _update_cell_methods(new, method, all_collapse_axes)
            if squeeze:            
                new.squeeze(all_collapse_axes, i=True)
            
            out.append(new)
            continue
        #--- End:if

        # Still here?

        # ------------------------------------------------------------
        # Some size > 1 axes need collapsing in the data array
        # ------------------------------------------------------------
        non_collapse_axes = [axis for axis in data_axes
                             if axis not in collapse_axes]
        transpose_axes = non_collapse_axes + collapse_axes
        if transpose_axes != data_axes:
#            f = f.copy()
            new.transpose(transpose_axes, i=True)
            data_axes = new.domain.data_axes()
#        else:
#            new = f.copy(_omit_Data=True)

        domain = new.domain

        # ------------------------------------------------------------
        # Calculate inferred weights, if required
        # ------------------------------------------------------------
        collapse_iaxes = []
        if weights_in in (None, 'equal'):
            weights = {}

        elif weights_in:
            weights = {}
            weights_axes = new.axes(tuple(weights_in)).intersection(collapse_axes)

            # Get weights from cell measures, if possible.
            for key, cm in domain.items(role='m', axes=weights_axes).iteritems():
                cm_axes = domain.item_axes(key)
#                print cm_axes
#                print domain.dimensions
#                print 'ttttttttt', repr(cm)
                # Remove any axes which are not spanned by the field's
                # data array.
                iaxes = [i for i, axis in enumerate(cm_axes) 
                         if axis not in data_axes]
                if iaxes:
                    cm = cm.squeeze(iaxes)

                iaxes = [data_axes.index(axis) for axis in cm_axes
                         if axis in data_axes]
                weights[tuple(iaxes)] = cm.data
#                print 'ttttttttt', cm.array
                weights_axes.difference_update(cm_axes)

                collapse_iaxes += iaxes
            #--- End: for

            # Get weights for any remaining axes from dimension
            # coordinates, if possible.
            for axis in weights_axes:
                w = calc_weights(domain.item(axis), infer_bounds=True)
                if w is not None:
                    iaxis = data_axes.index(axis)
                    weights[(iaxis,)] = w
  
                    collapse_iaxes.append(iaxis)
            #--- End: for

        else:
            raise ValueError("Can't collapse %s: Invalid weights specification: %s" % 
                             (self.__clas__.__name__, repr(weights_in)))

#        print weights
        # ------------------------------------------------------------
        # Collapse the data array
        # ------------------------------------------------------------
        n_collapse_axes = len(collapse_axes)
        new.Data = _collapse_data(new.data, method, n_collapse_axes, weights,
                                  squeeze=squeeze, unbiased=not biased)

        if squeeze:            
            # --------------------------------------------------------
            # Squeeze the collapse axes from the collapsed field's
            # data array
            # --------------------------------------------------------
            n_non_collapse_axes = f.ndim - n_collapse_axes
            domain.dimensions['data'] = domain.dimensions['data'][:n_non_collapse_axes]

        # ------------------------------------------------------------
        # Update ancillary variables
        # ------------------------------------------------------------
        _update_ancillary_variables(new, collapse_axes)

        # ------------------------------------------------------------
        # Update coordinate references
        # ------------------------------------------------------------
        _update_ref_fields(new, collapse_axes)

        #-------------------------------------------------------------
        # Collapse the domain
        #-------------------------------------------------------------
        _collapse_domain_items(new.domain, collapse_axes)

        # ------------------------------------------------------------
        # Update the cell methods
        # ------------------------------------------------------------
        _update_cell_methods(new, method, all_collapse_axes)

        out.append(new)
    #--- End: for

    if isinstance(fields, out[0].__class__):
        # Return a Field
        return out[0]
    else:
        # Return a FieldList
        return out
#--- End: def

def _collapse_data(data, method, n_collapse_axes, weights,
                   squeeze=False, unbiased=False):
    '''

Return a data array collapsed over one or more dimensions.

:Parameters:

    data : cf.Data
        Data to be collapsed.

        .. note:: It is assumed, and must be the case, that the
                  collapse axes are all in the fastest varying
                  (outermost) positions.

    method : str

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    weights : dict or None
    
        .. note:: The weights may get changed in place.

    unbiased : bool, optional

:Returns:

    out : cf.Data

**Examples**

'''
    ndim = data.ndim
    n_non_collapse_axes = ndim - n_collapse_axes
    collapse_iaxes = range(n_non_collapse_axes, ndim)

    #-----------------------------------------------------------------
    # Initialize the output data array
    #-----------------------------------------------------------------
    new = data[(Ellipsis,) + (0,)*n_collapse_axes]
    
    #-----------------------------------------------------------------
    # Parse the weights.
    #
    # * Change the keys from dimension names to the integer positions
    #   of the dimensions.
    #
    # * Make sure all non-null weights are Data objects.
    # -----------------------------------------------------------------
    if weights:
        # Get rid of null weights
        for key, weight in weights.items():
            # Ignore undefined weights
            if weight is None:
                del weights[key]
                continue
            
            # Ignore string-valued weights
            if weight.dtype.char == 'S':
                del weights[key]
                continue
                
            # Ignore size 1 weights
            if weight.size == 1:
                del weights[key]
                continue

            # Check that the shape of the weights match the sizes of
            # their corresponding data array dimensions.
            data_shape = data.shape
            weight_shape = weight.shape
            for i, j in enumerate(key):
                if weight_shape[i] != data_shape[j]:
                    raise ValueError(
                        "Can't collapse: Incorrect weights shape: %s" %
                        weight_shape)
            #--- End :for
        #--- End: for

        # Optimize when weights span only non-partitioned axes (do
        # this before permuting the order of the weight axes to be
        # consistent with the order of the data axes)
        weights = _optimize_weights(data, weights)

        # Permute the order of the weight axes to be consistent with
        # the order of the data axes
        for key, weight in weights.items():
            if weight.ndim > 1:
                key1 = sorted(key)
                if key1 != list(key):
#                    weight = weight.copy()
                    weight = weight.transpose(numpy_argsort(key))
                    del weights[key]
                    weights[tuple(key1)] = weight
        #--- End: for
#        for key, weight in weights.items():
#            print key, weight.shape, weight.array

    else:
        weights = None

    # ----------------------------------------------------------------
    # Define the collapse function
    # ----------------------------------------------------------------
    collapse_function = _collapse_functions[method]

    datatype = data.dtype

    for partition in new.partitions.flat:
        del partition.subarray

    data.to_memory()

#    save = new.save_to_disk()
    save = not new.fits_in_memory(new.dtype.itemsize)

    p_axes  = new._axes[:n_non_collapse_axes]
    p_units = new.Units

    c_location = [(0, 1)]       * n_collapse_axes
    c_shape    = [1]            * n_collapse_axes
    c_slice    = (slice(None),) * n_collapse_axes

    for partition in new.partitions.flat:
        partition.axes  = p_axes
        partition.flip  = []
        partition.part  = []
        partition.Units = p_units

        master_indices = partition.indices[:n_non_collapse_axes] + c_slice

        partition.subarray = collapse_function(data, master_indices,
                                               n_non_collapse_axes,
                                               n_collapse_axes,
                                               weights=weights,
                                               unbiased=unbiased)

        p_datatype = partition.subarray.dtype
        if datatype != p_datatype:
            datatype = numpy_result_type(p_datatype, datatype)
            
        partition.location = partition.location[:n_non_collapse_axes]
        partition.shape    = partition.shape[:n_non_collapse_axes]
        if not squeeze:
            partition.location += c_location
            partition.shape    += c_shape

        partition.masked = None
        partition.close(save)
    #--- End: for

    new._all_axes = None
    new._flip     = []
    new.dtype     = datatype

    if squeeze:
        new._axes  = p_axes
        new._ndim  = ndim - n_collapse_axes
        new._shape = new._shape[:new._ndim]

    # ----------------------------------------------------------------
    # Return the collapsed data
    # ----------------------------------------------------------------
    return new
#--- End: def

def _collapse_domain_items(domain, collapse_axes):
    '''

Collapse dimensions of a domain to size 1 in place.

A dimension coordinate for a collapse dimension is replaced with a
size 1 coordinate whose bounds are the maximum and minimum of the
original bounds array (of the original data array if there are no
bounds) and whose datum is the average of the new bounds.

All auxiliary coordinates and cell measures which span any of the
collapse dimensions are removed.

:Parameters:

    domain : cf.Domain
        The domain to be collapsed.

    collapse_axes : sequence of str
        The collapse axes of the field's data array, defined by their
        domain identifiers.

:Returns:

    None

**Examples**

>>> _collapse_domain_items(f.domain, ['dim2', 'dim1'])

'''
    for axis in collapse_axes:
        # Ignore axes which are already size 1
        if domain.dimension_sizes[axis] == 1:
            continue
        
        dim_coord = domain.item(axis)
        if dim_coord is None:
            continue

        if dim_coord.hasbounds:
            bounds = [dim_coord.bounds.datum(0), dim_coord.bounds.datum(-1)]
        else:
            bounds = [dim_coord.datum(0), dim_coord.datum(-1)]

        units = dim_coord.Units
        data   = Data([(bounds[0] + bounds[1])*0.5], units)
        bounds = Data([bounds], units)

        dim_coord.insert_data(data, bounds=bounds, copy=False)

        # Put the new dimension coordinate into the domain
        domain.insert_axis(1, key=axis, replace=True)
        domain.insert_dim(dim_coord, key=axis, copy=False, replace=True)
        
        # Remove all auxiliary coordinates and cell measures which
        # span this axis
        domain.remove_items(role=('a', 'm'), axes=axis)
    #--- End: for
#--- End: def

def _update_cell_methods(f, method, all_collapse_axes):
    '''

:Parameters:

    f : cf.Field

    method : str

    all_collapse_axes : sequence of str
        The collapse axes of the field, defined by their domain
        identifiers. May contain axes which are not spanned by the
        field's data array.

:Returns:

    None

**Examples**

'''
    if not hasattr(f, 'cell_methods'):
         f.cell_methods = CellMethods()

    domain = f.domain

    all_collapse_axes = sorted(all_collapse_axes)

    name = []
    for axis in all_collapse_axes:
        item = domain.item(axis)
        if item is not None:
            name.append(item.identity(default=axis))
        else:
            name.append(axis)
    #--- End: for

    string = '%s: %s' % (': '.join(name), method)

    cell_method = CellMethods(string)
    
    cell_method[0].axes = tuple(all_collapse_axes[:])

    if not f.cell_methods or f.cell_methods[-1] != cell_method:
        f.cell_methods += cell_method
#--- End: def

def _update_ancillary_variables(f, collapse_axes):
    '''

:Parameters:

    f : cf.Field

    collapse_axes : sequence of str
        The collapse axes of the field's data array, defined by their
        domain identifiers.

:Returns:

    None

**Examples**

'''
    if not hasattr(f, 'ancillary_variables'):
        return

    new_av = AncillaryVariables()

    for av in f.ancillary_variables:

        axis_map = av.domain.map_axes(f.domain)

        # Don't keep the ancillary variable if its master data array
        # has an undefined dimension with size > 1.
        keep = True
        for axis1 in set(av.data_axes()).difference(axis_map):
            if av.domain.dimension_sizes[axis1] > 1:
                keep = False
                break
        #--- End: for
        if not keep:
            continue

        # Don't keep the ancillary variable if its master data array
        # has a defined dimension with size > 1 which is also a
        # collapse dimension.
        keep = True
        for axis1, axis0 in axis_map.iteritems():
            if axis0 in collapse_axes and av.domain.dimension_sizes[axis1] > 1:
                keep = False
                break
        #--- End: for
        if not keep:
            continue

        new_av.append(av)
    #--- End: for

    if new_av:
        f.ancillary_variables = new_av
    else:
        del f.ancillary_variables 
#--- End: def

def _update_ref_fields(f, collapse_axes):
    '''

:Parameters:

    f : cf.Field

    collapse_axes : sequence of str
        The collapse axes of the field's data array, defined by their
        domain identifiers.

:Returns:

    None

**Examples**

'''
    for t in f.refs().itervalues():
        
        for term, value in t.items():
            if not isinstance(value, Field):
                # Keep the term if it isn't a field
                continue 

            data_axes = set(value.data_axes())

            if data_axes.isdisjoint(collapse_axes):
                # Keep the term if it doesn't span any collapse axes
                continue

            axis_map = value.domain.map_axes(f.domain)
                
            # Don't keep the term if its master data array has an
            # undefined axis with size > 1.
            for axis1 in data_axes.difference(axis_map):
                if av.domain.dimension_sizes[axis1] > 1:
                    t[term] = None
                    break
            #--- End: for
            if t[term] is None:
                continue

            # Don't keep the ancillary variable if its master data
            # array has a defined axis with size > 1 which is also a
            # collapse axis
            for axis1, axis0 in axis_map.iteritems():
                if (axis0 in collapse_axes and axis1 in data_axes and
                    value.domain.dimension_sizes[axis1] > 1):
                    t[term] = None
                    break
            #--- End: for
        #--- End: for
    #--- End: for
#--- End: def

def _max(data, indices, n_non_collapse_axes, n_collapse_axes,
         **kwargs):
    '''
        
Return the maximum along a subset of the axes of a subspace of a data
array.

:Parameters:

    data : cf.Data
        The data array.

    indices : tuple
        The indices which define the subspace of *data* which is to be
        collapsed.

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    kwargs : *optional*
        Ignored.

:Returns:

    out : numpy array
        The maximum value, an array with *n_non_collapse_axes*
        dimensions.

**Examples**

>>> indices = (slice(1), slice(0), slice(None))

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[0.0 1.0 -- 3.0]]]
>>> print _max(d, indices, 2, 1)
[[ 3.]]           
>>> print _max(d, indices, 0, 3)
3.0

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[--  -- --  -- ]]]
>>> print _max(d, (slice(None,)*3, 2, 1)
[[--]]
>>> print _max(d, (slice(None,)*3, 0, 3)
--

'''
    master_shape = data.shape
    data = data[indices]
    
    out, n = _collapse_subspace(_numpy_amax, _numpy_amax, data, indices,
                                master_shape, n_non_collapse_axes,
                                n_collapse_axes, weights=None)
    if not out:
        # data[indices] is all missing data
        return numpy_ma_masked_all(data.shape[:n_non_collapse_axes], data.dtype)
    
    pmaxs = out[0]
    if n:
        return pmaxs
    elif pmaxs.shape[0] == 1:
        # There is a partial maximum axis, but it has size 1.
        return pmaxs[0]        
    else:
        # Find maximum of the partial maxima
        return numpy_amax(pmaxs, axis=0)
#--- End: def

def _mean(data, indices, n_non_collapse_axes, n_collapse_axes,
          weights=None, **kwargs):
    '''

Return the mean along a subset of the axes of a subspace of a data
array.

The mean may be weighted or unweighted.

:Parameters:

    data : cf.Data
        The data array.

    indices : tuple
        The indices which define the subspace of *data* which is to be
        collapsed.

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    weights : dict, optional

    kwargs : *optional*
        Ignored.

:Returns:

    out : numpy array
        The mean value, an array with *n_non_collapse_axes*
        dimensions.

**Examples**

'''
    master_shape = data.shape
    data = data[indices]

    out, n = _collapse_subspace(numpy_average, numpy_ma_average, data,
                                indices, master_shape, n_non_collapse_axes,
                                n_collapse_axes, weights=weights, returned=True)
    
    if not out:
        # data[indices] is all missing data
        return numpy_ma_masked_all(data.shape[:n_non_collapse_axes], data.dtype)
    
    pmeans, psums_of_weights = out

    if n:
        return pmeans
    elif pmeans.shape[0] == 1:
        # There is a partial mean axis, but it has size 1.
        return pmeans[0]
    else:
        # Find the mean from the partial means
        if numpy_ma_is_masked(pmeans):
            return numpy_ma_average(pmeans, axis=0, weights=psums_of_weights)
        else:
            return numpy_average(pmeans, axis=0, weights=psums_of_weights)
#--- End: def

def _mid_range(data, indices, n_non_collapse_axes, n_collapse_axes,
               **kwargs):
    '''
 
Return the mid range along a subset of the axes of a subspace of a
data array.

The mid range is the unweighted average of minimum and maximum values.

:Parameters:

    data : cf.Data
        The data array.

    indices : tuple
        The indices which define the subspace of *data* which is to be
        collapsed.

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    kwargs : *optional*
        Ignored.

:Returns:

    out : numpy array
        The mid range value, an array with *n_non_collapse_axes*
        dimensions.

**Examples**

>>> indices = (slice(1), slice(0), slice(None))

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[0.0 1.0 -- 3.0]]]
>>> print _mid_range(d, (slice(None,)*3, 2, 1)
[[ 1.5]]
>>> print _mid_range(d, (slice(None,)*3, 0, 3)
1.5

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[--  -- --  -- ]]]
>>> print _mid_range(d, (slice(None,)*3, 2, 1)
[[--]]
>>> print _mid_range(d, (slice(None,)*3, 0, 3)
--

'''
    master_shape = data.shape
    data = data[indices]

    out, n = _collapse_subspace(_numpy_amin_amax, _numpy_amin_amax, data,
                                indices, master_shape, n_non_collapse_axes,
                                n_collapse_axes, weights=None)

    if not out:
        # data[indices] is all missing data
        return numpy_ma_masked_all(data.shape[:n_non_collapse_axes], data.dtype)
    
    pmins, pmaxs = out

    if n:
        gmin = pmins
        gmax = pmaxs
    elif pmins.shape[0] == 1:
        # There is are partial maximum and minimum axes, but it they
        # have size 1.
        gmin = pmins[0]
        gmax = pmaxs[0]
    else:
        # Find the minimum from the paritial minima and the maximum
        # from the parital maxima
        gmin = numpy_amin(pmins, axis=0)
        gmax = numpy_amax(pmaxs, axis=0)
    #--- End: if

    gmax -= gmin
    gmax *= 0.5
    return gmax
#--- End: def

def _min(data, indices, n_non_collapse_axes, n_collapse_axes,
         **kwargs):
    '''
        
Return the minimum along a subset of the axes of a subspace of a data
array.

:Parameters:

    data : cf.Data
        The data array.

    indices : tuple
        The indices which define the subspace of *data* which is to be
        collapsed.

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    kwargs : *optional*
        Ignored.

:Returns:

    out : numpy array
        The minimum value, an array with *n_non_collapse_axes*
        dimensions.

**Examples**

>>> indices = (slice(1), slice(0), slice(None))

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[0.0 1.0 -- 3.0]]]
>>> print _min(d, (slice(None,)*3, 2, 1)
[[ 0.]]
>>> print _min(d, (slice(None,)*3, 0, 3)
0.0

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[--  -- --  -- ]]]
>>> print _min(d, (slice(None,)*3, 2, 1)
[[--]]
>>> print _min(d, (slice(None,)*3, 0, 3)
--

'''  
    master_shape = data.shape
    data         = data[indices]
    
    out, n = _collapse_subspace(_numpy_amin, _numpy_amin, data, indices,
                                master_shape, n_non_collapse_axes,
                                n_collapse_axes, weights=None)

    if not out:
        # data[indices] is all missing data
        return numpy_ma_masked_all(data.shape[:n_non_collapse_axes], data.dtype)

    pmins = out[0]

    if n:
        return pmins
    elif pmins.shape[0] == 1:
        # There is a partial minimum axis, but it has size 1.
        return pmins[0]
    else:
        # Find the minimum from the paritial minima
        return numpy_amin(pmins, axis=0)
#--- End: def

def _mode(*args, **kwargs):
    '''

Return the mode along a subset of the axes of a subspace of a data
array.

'''
    raise NotImplementedError("Haven't implement mode, yet. Sorry.")
#--- End: def

def _median(*args, **kwargs):
    '''

Return the median along a subset of the axes of a subspace of a data
array.

'''
    raise NotImplementedError("Haven't implement median, yet. Sorry.")
#--- End: def

def _standard_deviation(data, indices, n_non_collapse_axes,
                        n_collapse_axes, weights=None, unbiased=False,
                        **kwargs):
    '''

Return the standard deviation along a subset of the axes of a subspace
of a data array.

The standard deviation may be weighted or unweighted.

The standard deviation may be biased or unbiased.

The return type is numpy.float64 if the master data array is of
integer type, otherwise it is of the same type as master data array.

:Parameters:

    data : cf.Data
        The data array.

    indices : tuple
        The indices which define the subspace of *data* which is to be
        collapsed.

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    weights : dict, optional        

    unbiased : bool, optional
        If True then the unbiased sample standard deviation will be
        returned. By default the biased population standard deviation
        will be returned.

    kwargs : *optional*
        Ignored.

:Returns:

    out : numpy array
        The standard deviation value, an array with
        *n_non_collapse_axes* dimensions.

**Examples**

>>> print d.array
[-- 1 2 3]
>>> _standard_deviation(d)

>>> d[...] = cf.masked
>>> print d.array
[-- -- -- --]
>>> _standard_deviation(d)
masked

'''
    variance = _variance(data, indices, n_non_collapse_axes, n_collapse_axes,
                         weights=weights, unbiased=unbiased)

    variance **= 0.5

    return variance
#--- End: def

def _sum(data, indices, n_non_collapse_axes, n_collapse_axes,
         **kwargs):
    '''
        
Return the sum of the master data array along a subset of its axes.

:Parameters:

    data : cf.Data
        The data array.

    indices : tuple
        The indices which define the subspace of *data* which is to be
        collapsed.

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    kwargs : *optional*
        Ignored.

:Returns:

    out : numpy array
        The sum value, an array with *n_non_collapse_axes* dimensions.

**Examples**

>>> indices = (slice(1), slice(0), slice(None))

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[0.0 1.0 -- 3.0]]]
>>> print _sum(d, (slice(None,)*3, 2, 1)
[[ 4.]]
>>> print _sum(d, (slice(None,)*3, 0, 3)
4.0

>>> print d.array
[[[0.5 -- 0.7 0.8]]
 [[--  -- --  -- ]]]
>>> print _sum(d, (slice(None,)*3, 2, 1)
[[--]]
>>> print _sum(d, (slice(None,)*3, 0, 3)
--

'''
    shape = data.shape
    data = data[indices]
    
    out, n = _collapse_subspace(_numpy_sum, _numpy_sum, data, indices,
                                shape, n_non_collapse_axes, n_collapse_axes,
                                weights=None)
    
    if not out:
        # data[indices] is all missing data
        return numpy_ma_masked_all(data.shape[:n_non_collapse_axes], data.dtype)

    psums = out[0]

    if n:
        return psums
    elif psums.shape[0] == 1:
        # There is a partial sum axis, but it has size 1.
        return psums[0]
    else:
        # Find the sum from the paritial sums
        return numpy_sum(psums, axis=0)
#--- End: def

def _variance(data, indices, n_non_collapse_axes, n_collapse_axes,
              weights=None, unbiased=False, **kwargs):
    '''

Return the variance along a subset of the axes of a subspace of a data
array.

The variance may be weighted or unweighted.

The variance may be biased or unbiased.

:Parameters:

    data : cf.Data
        The data array.

    indices : tuple
        The indices which define the subspace of *data* which is to be
        collapsed.

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    weights : dict, optional

    unbiased : bool, optional
        If True then the unbiased sample variance will be returned. By
        default the biased population variance will be returned.

    kwargs : *optional*
        Ignored.

:Returns:

    out : numpy array
        The variance value, an array with *n_non_collapse_axes*
        dimensions.

**Examples**

'''
    #-----------------------------------------------------------------
    # Methods:
    #
    # http://en.wikipedia.org/wiki/Standard_deviation#Population-based_statistics
    # http://en.wikipedia.org/wiki/Weighted_mean#Weighted_sample_variance
    #-----------------------------------------------------------------
    master_shape = data.shape
    data = data[indices]
    
    out, n = _collapse_subspace(_components, _components, data, indices,
                                master_shape, n_non_collapse_axes,
                                n_collapse_axes, weights=weights,
                                unbiased=unbiased)
                         
    if _debug:
        print '_variance: out =', out

    if not out:
        # data[indices] is all missing data
        return numpy_ma_masked_all(data.shape[:n_non_collapse_axes], data.dtype)

    if unbiased:        
        pmeans, pvariances, psums_of_weights, psums_of_weights2 = out
    else:
        pmeans, pvariances, psums_of_weights = out

    # -----------------------------------------------------------------------------
    # Calculate the biased variance
    # (http://en.wikipedia.org/wiki/Standard_deviation#Population-based_statistics)
    #
    # global biased variance = {[SUM(psw(pv+pm**2)]/sw} - m**2
    # 
    # where psw = partial sum of weights  (psums_of_weights)
    #       pv  = partial biased variance (pvariances)
    #       pm  = partial mean            (pmeans)
    #       sw  = global sum of weights   (gsum_of_weights)
    #       m   = global mean             (gmean)
    # -----------------------------------------------------------------------------
    if n:
        gvariance       = pvariances
        gsum_of_weights = psums_of_weights
        if unbiased:
            gsum_of_weights2 = psums_of_weights2
    
        if _debug:
            print '_variance: gmean              =', pmeans
            print '_variance: gsum_of_weights    =', gsum_of_weights
            print '_variance: gvariance (biased) =', gvariance

    elif pmeans.shape[0] == 1:
        # There is a partial variance axis, but it has size 1.
        gvariance       = pvariances[0]
        gsum_of_weights = psums_of_weights[0]
        if unbiased:
            gsum_of_weights2 = psums_of_weights2[0]
    
        if _debug:
            print '_variance: gmean              =', pmeans
            print '_variance: gsum_of_weights    =', gsum_of_weights
            print '_variance: gvariance (biased) =', gvariance

    else:
        # Find the variance from the paritial variances
        if not numpy_ma_is_masked(pmeans):
            gmean, gsum_of_weights = numpy_average(pmeans, axis=0,
                                                   weights=psums_of_weights,
                                                   returned=True)
        else:
            gmean, gsum_of_weights = numpy_ma_average(pmeans, axis=0,
                                                      weights=psums_of_weights,
                                                      returned=True)

        if _debug:
            print '_variance: gmean              =', gmean
            print '_variance: gsum_of_weights    =', gsum_of_weights

        pmeans *= pmeans
        pvariances += pmeans
        pvariances *= psums_of_weights
        gvariance = numpy_sum(pvariances, axis=0)

        # Divide by the global sum of weights
        gvariance /= gsum_of_weights
        # Subtract the square of the global mean
        gmean *= gmean
        gvariance -= gmean

        if _debug:
            print '_variance: gvariance (biased) =', gvariance

        if unbiased:
            gsum_of_weights2 = numpy_sum(psums_of_weights2, axis=0)
    #--- End: if

    if unbiased:
        # ---------------------------------------------------------------------
        # Convert the biased population variance to the unbiased
        # sample variance
        # (http://en.wikipedia.org/wiki/Weighted_mean#Weighted_sample_variance)
        #
        # global unbiased variance = [sw**2/(sw**2 - sw2)] * sigma2
        # 
        # where sw     = global sum of weights            (gsum_of_weights)
        #       sw2    = global sum of squares of weights (gsum_of_weights2)
        #       sigma2 = global biased variance           (gvariance)
        # ---------------------------------------------------------------------
        gsum_of_weights *= gsum_of_weights
        gvariance *= gsum_of_weights
        gsum_of_weights -= gsum_of_weights2
        gvariance /= gsum_of_weights

        if _debug:
            print '_variance: gsum_of_weights2   =', gsum_of_weights2
       #--- End: if

    if _debug:
        print '_variance: gvariance          =', gvariance
   
    # ------------------------------------------------------------
    # Return the global variance
    # ------------------------------------------------------------
    return gvariance
#--- End: def

def _numpy_amin(array, axis=None):
    '''

Return the minimum of an array or the minimum along an axis.

``_numpy_amin(array, axis=axis)`` is equivalent to
``(numpy.amin(array, axis=axis),)``

:Parameters:

    array : numpy array_like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

:Returns:

    out : tuple
        The minimum in a 1-tuple.

'''
    return (numpy_amin(array, axis=axis),)
#--- End: def

def _numpy_amax(array, axis=None):
    '''

Return the maximum of an array or the maximum along an axis.

``_numpy_amax(array, axis=axis)`` is equivalent to
``(numpy.amax(array, axis=axis),)``

:Parameters:


    array : numpy array_like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

:Returns:

    out : tuple
        The maximum in a 1-tuple.

'''
    return (numpy_amax(array, axis=axis),)
#--- End: def

def _numpy_amin_amax(array, axis=None):
    '''

Return the minimum and maximum of an array or the minima and maxima
along an axis.

``_numpy_amin_amax(array, axis=axis)`` is equivalent to
``(numpy.amin(array, axis=axis), numpy.amax(array, axis=axis))``

:Parameters:

    array : numpy array_like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

:Returns:

    out : tuple
        The minimum and maximum values in a 2-tuple.

'''
    return numpy_amin(array, axis=axis), numpy_amax(array, axis=axis)
#--- End: def

def _numpy_sum(array, axis=None):
    '''

Return the sum of an array or the sum along an axis.

``_numpy_sum(array, axis=axis)`` is equivalent to ``(numpy.sum(array,
axis=axis),)``

:Parameters:

    array : numpy array-like
        Input array

    axis : int, optional
        Axis along which to operate. By default, flattened input is
        used.

:Returns:

    out : tuple
        The sum in a 1-tuple.

'''
    return (numpy_sum(array, axis=axis),)
#--- End: def

def _components(array, axis=None, weights=None, unbiased=False):
    '''

Return selected statistics derived from an array:

* Mean of the array
* Biased population variance of the array
* Sum of weights for the array
* Sum of squares of weights for the array (only if unbiased is True)

:Parameters:

    array : array-like
        The array from which the statistics are calculated.

    weights : array-like, optional
        The importance that each element has in the computations. If
        set then the weights array must have the same shape as
        *array*. By default all data in *array* are assumed to have a
        weight equal to one.

:Returns:

    out : tuple
        Either a 3-tuple of the mean, biased population variance and
        sum of weights in that order; or, if *unbiased* is True, a
        4-tuple which has an additional element of the sums of the
        squares of weights.

'''
    # ----------------------------------------------------------------
    # Methods:
    #
    # http://en.wikipedia.org/wiki/Standard_deviation#Population-based_statistics
    # http://en.wikipedia.org/wiki/Weighted_mean#Weighted_sample_variance
    # ----------------------------------------------------------------
    masked = numpy_ma_is_masked(array)

    if not masked:
        mean, sw = numpy_average(array, weights=weights, axis=axis,
                                 returned=True)

        

    else:
        # Do masked case separately since it is much slower
        mean, sw = numpy_ma_average(array, weights=weights, axis=axis,
                                    returned=True)
        
    if mean.size > 1:
        # We collapsed over axis=-1 and array has 2 or more
        # dimensions, so add an extra size 1 dimension to the mean so
        # that broadcasting works when we calculate sigma2.
        mean = numpy_expand_dims(mean, -1)
        reshape_mean = True
    else:
        reshape_mean = False
        
    sigma2   = array - mean
    sigma2 **= 2

    if not masked:
        sigma2 = numpy_average(sigma2, axis=axis, weights=weights)
    else:
        sigma2 = numpy_ma_average(sigma2, axis=axis, weights=weights)

    if reshape_mean:
        mean = mean.reshape(mean.shape[:-1])
        
    if unbiased:
        # Calculate the sum of the square of weights
        if weights is None:
            sw2 = numpy_copy(sw)
        else:
            if weights.ndim < array.ndim:
                weights = broadcast_array(weights, array.shape)

            if masked:
                # If the array is masked then we have to mask the
                # weights to get the correct sum of squares
                weights = numpy_ma_array(weights, mask=array.mask, copy=False)

            sw2 = numpy_sum(weights*weights, axis=axis) 
        #--- End: if

        return (mean, sigma2, sw, sw2)

    else:
        return (mean, sigma2, sw)
#--- End: def

def _create_weights(array, indices, master_indices, master_shape, 
                    master_weights, n_non_collapse_axes, n_collapse_axes):
    '''

:Parameters:

    array : numpy array

    indices : tuple

    master_indices : tuple

    master_shape : tuple

    master_weights : dict

    n_non_collapse_axes : int
        The number of array axes which are not being collapsed. It is
        assumed that they are in the slowest moving positions.

    n_collapse_axes : int
        The number of array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

:Returns:

    out : numpy.ma.array

**Examples**

'''
    array_shape = array.shape
    array_ndim  = array.ndim

    weights_indices = []
    for master_index, index, size in izip(master_indices,
                                          indices,
                                          master_shape):
        start , stop , step = master_index.indices(size)

        size1, mod = divmod(stop-start-1, step)            
        
        start1, stop1, step1 = index.indices(size1+1)
        
        size2, mod = divmod(stop1-start1, step1)

        if mod != 0:
            size2 += 1
            
        start += start1 * step
        step  *= step1
        stop   = start + (size2-1)*step + 1

        weights_indices.append(slice(start, stop, step))
    #--- End: for

    base_shape = (1,) * array_ndim

    weights = [] 
    for key, weight in master_weights.iteritems():
        shape = list(base_shape)
        index = []
        for i in key:
            shape[i] = array_shape[i]
            index.append(weights_indices[i])
        #--- End: for

        weight = weight[tuple(index)].unsafe_array

        if weight.ndim != array_ndim:
            # Make sure that the weight has the same number of
            # dimensions as the array
            weight = weight.reshape(shape)

        weights.append(weight)
    #--- End: for

    weights_out = weights[0]

    if len(weights) > 1:
        # There are two or more weights, so create their product
        for w in weights[1:]:
            # Can't do this in-place because of broadcasting woe
            weights_out = weights_out * w

    if weights_out.shape[:n_non_collapse_axes] == base_shape[:n_non_collapse_axes]:
        # The input weights only span collapse axes
        if weights_out.shape[n_non_collapse_axes:] != array_shape[n_non_collapse_axes:]:
            # The input weights span some, but not all, of the
            # collapse axes, so broadcast the weights over all
            # collapse axes.
            weights_out = broadcast_array(weights_out, array_shape[n_non_collapse_axes:])
        #--- End: if

        # Get rid of the non-collapse axes
        weights_out = weights_out.reshape(array_shape[n_non_collapse_axes:])
    else:
        # The input weights span at least one non-collapse axis, so
        # broadcast the weights over all axes.
        weights_out = broadcast_array(weights_out, array_shape)   

    return weights_out
#--- End: def

def _collapse_subspace(func, ma_func, data, master_indices,
                       master_shape, n_non_collapse_axes, n_collapse_axes,
                       weights=None, **kwargs):
    '''

Collapse a subspace of a data array.

If set, *weights* and *kwargs* are passed to the function call. If
there is a *weights* keyword argument then this should either evaluate
to False or be a dictionary of weights for at least one of the data
dimensions.

:Parameters:

    func : function

    ma_func : function

    data : cf.Data
        A subspace of the master array.

    master_indices: tuple
        The indices of the master array corresponding to *data*.    

    n_non_collapse_axes : int
        The number of data array axes which are not being
        collapsed. It is assumed that they are in the slowest moving
        positions.

    n_collapse_axes : int
        The number of data array axes which are being collapsed. It is
        assumed that they are in the fastest moving positions.

    weights : dict, optional

    kwargs : *optional*

:Returns:

    out : list

**Examples**

'''    
    out = []
    one_partition = False
                
    if n_collapse_axes == 1:
        # Exactly one axis is to be collapsed. Note that it is
        # assumed that, by now, this axis is in position -1.
        kwargs['axis'] = -1      
    elif not n_non_collapse_axes:
        # All axes are to be collapsed
        kwargs.pop('axis', None)

    data.varray
        
    pda_args = data.pda_args(revert_to_file=True, readonly=True)

    for i, partition in enumerate(data.partitions.matrix.flat):
        array = partition.dataarray(**pda_args)

        masked = partition.masked

        if masked and array.mask.all():
            # The sub-array is all missing data
            continue

        # Still here? Then there are some non-missing sub-array
        # elements.
        if weights:
            kwargs['weights'] = _create_weights(
                array, partition.indices, master_indices, master_shape, weights,
                n_non_collapse_axes, n_collapse_axes)

        if n_collapse_axes > 1:
#            # Exactly one axis is to be collapsed. Note that it is
#            # assumed that, by now, this axis is in position -1.
#            kwargs['axis'] = -1
#
#        elif not n_non_collapse_axes:
#            # All axes are to be collapsed
#            kwargs.pop('axis', None)
#
#        else:
            # At least two, but not all, axes are to be
            # collapsed. Therefore we need to reshape the array and
            # the weights. Note that it is assumed that, by now, these
            # axes is in the last positions (-1, -2, ...).
            kwargs['axis'] = -1
            shape = array.shape
            ndim = array.ndim
            new_shape  = shape[:n_non_collapse_axes]
            new_shape += (reduce(operator_mul, shape[n_non_collapse_axes:]),)  
            array = numpy_reshape(array.copy(), new_shape)
            if weights:
                w = kwargs['weights']
                if w.ndim < ndim:
                    # The weights span only collapse axes
                    new_shape = (w.size,)

                kwargs['weights'] = numpy_reshape(w, new_shape)
        #--- End: if

        if not masked: 
            # The sub-array has no masked values so use the function
            # for unmasked arrays
            p_out = func(array, **kwargs)
        else:
            # The sub-array has at least one masked value so use the
            # function for masked arrays
            p_out = ma_func(array, **kwargs)

        partition.close()

        if not out:
            size = data._pmsize - i
            if size == 1:
                # There is exactly one partition with some valid data,
                # so we are done.
                out = p_out
                one_partition = True
                break
            else:
                # There is at least one partition with some valid data
                j = i
                datatype = p_out[0].dtype
                for y in p_out:
                    out.append(numpy_ma_masked_all((size,) + numpy_shape(y),
                                                   datatype))
        #--- End: if

        k = i - j
        for x, y in izip(out, p_out):
            x[k] = y
    #--- End: for

    return out, one_partition
#--- End: def

def calc_weights(coord, infer_bounds=False):
    '''

Calculate weights for collapsing. See def collapse for help

:Parameters:

    coord : cf.DimensionCoordinate

:Returns:

    out : cf.Data or None

'''

    if coord is None or coord.size == 1:
        return None
    elif coord.Y or coord.identity() == 'grid_latitude':
        return _latitude_area_weights(coord, infer_bounds=infer_bounds)    
    else:
        return _linear_weights(coord, infer_bounds=infer_bounds)
#--- End: def

def _equal_weights(size):
    '''

Return equal weights

:Parameters:

    size : int

:Returns:

    out : cf.Data

'''
    return Data(numpy_ones(size))
#--- End: def

def _linear_weights(coord, infer_bounds):
    '''

Calculate linear weights based on cell bounds.

:Parameters:

    coord : cf.DimensionCoordinate

:Returns:

    out : cf.Data

'''
#    if coord.size == 1:
#        return None

    bounds = coord.get_bounds(create=infer_bounds).data
    bounds = abs(bounds[..., 1] - bounds[..., 0])
    bounds.squeeze(-1, i=True)

    if (bounds == bounds.datum(0)).all():
        # The weights are equal
        return _equal_weights(bounds.size) #Data(numpy_ones(bounds.size))

    return bounds
#--- End: def

def _latitude_area_weights(coord, infer_bounds):
    '''

Calculate latitude-area weights based on cell bounds

:Parameters:

    coord : cf.DimensionCoordinate

:Returns:

    out : cf.Data

'''
    bounds = coord.get_bounds(create=infer_bounds).data
    bounds.sin()
    bounds = abs(bounds[..., 1] - bounds[..., 0])
    bounds.squeeze(-1, i=True)

    if (bounds == bounds.datum(0)).all():
        # The weights are equal
        return _equal_weights(bounds.size)

    return bounds
#--- End: def

def _optimize_weights(data, weights):
    '''
    
Optimise when weights span only non-partitioned axes.

    data : cf.Data

    weights : dict

'''
    axes   = data._axes
    pmaxes = data._pmaxes
    non_partitioned_iaxes = set([i for i, axis in enumerate(axes)
                                 if axis not in pmaxes])
    
    x = []
    new_key_iaxes = ()
    for iaxes in weights:
        if non_partitioned_iaxes.issuperset(iaxes):
            x.append(iaxes)
            new_key_iaxes += iaxes
    #--- End: for

    if len(x) > 1:
        reshaped_weights = []
        for key in x:
            w = weights.pop(key)
            w = w.array
            shape = [(w.shape[key.index(i)] if i in key else 1)
                     for i in new_key_iaxes]
            w = w.reshape(shape)
            
            reshaped_weights.append(w)
        #--- End: for
              
        # Create their product (Can't do this in-place because
        # of broadcasting woe ???)
        new_weight = reshaped_weights[0]
        for w in reshaped_weights[1:]:
            new_weight = new_weight * w

#        # Make sure that the new weight just a single partition
#        if new_weight._pmsize > 1:
#            new_weight.varray

        weights[new_key_iaxes] = Data(new_weight)

    #--- End: if

    return weights
#--- End: def

# --------------------------------------------------------------------
# Map each collapse method to its corresponding function
# --------------------------------------------------------------------
_collapse_functions = {'avg'               : _mean,
                       'average'           : _mean,
                       'mean'              : _mean,
                       'max'               : _max,
                       'maximum'           : _max,
                       'min'               : _min,
                       'minimum'           : _min,
                       'mid_range'         : _mid_range,
                       'var'               : _variance,
                       'variance'          : _variance,
                       'sd'                : _standard_deviation,
                       'std'               : _standard_deviation,
                       'standard_deviation': _standard_deviation,
                       'sum'               : _sum,
                       'median'            : _median,
                       'mode'              : _mode,
                       }
