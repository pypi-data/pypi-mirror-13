.. set tocdepth in sidebar
:tocdepth: 2

.. currentmodule:: cf
.. default-role:: obj

.. _manipulating-fields:

Manipulating `cf.Field` objects
===============================

Manipulating a field generally involves operating on its data array
and making any necessary changes to the field's domain to make it
consistent with the new array.


Data array
----------

Conversion to a numpy array
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A field's data array may be converted to either an independent numpy
array or a numpy array view (`numpy.ndarray.view`) with its
`~Field.array` and `~Field.varray` attributes respectively:

>>> a = f.array
>>> print a
[[2 -- 4 -- 6]]
>>> a[0, 0] = 999
>>> print a
[[999 -- 4 -- 6]]
>>> print f.array
[[2 -- 4 -- 6]]

Changing the numpy array view in place will also change the
field's data array in-place:

>>> v = f.varray
>>> print v
[[2 -- 4 -- 6]]
>>> v[0, 0] = 999
>>> print f.array
[[999 -- 4 -- 6]]

A field exposes the numpy array interface and so may be used as input
to any of the `numpy array creation functions
<http://docs.scipy.org/doc/numpy/reference/routines.array-creation.html#from-existing-data>`_:

>>> print f.array
[[2 -- 4 -- 6]]
>>> numpy.all(f.array)
True
>>> numpy.all(f)
True

.. note::

   The numpy array created by the `~Field.varray` or `~Field.array`
   attributes forces all of the data to be read into memory at the
   same time, which may not be possible for very large arrays.

Data mask
^^^^^^^^^

A copy of a field's missing data mask is returned by its
`~cf.Field.mask` attribute.

This mask is an independent field in its own right, and so changes to
it will not be seen by the field which generated it. See the
:ref:`assignment section <fm_assignment>` for details on how to edit
the field's mask in place.


Copying
-------

A deep copy of a field may be created with its `~Field.copy` method,
which is functionally equivalent to, but faster than, using the
:py:obj:`copy.deepcopy` function:

>>> g = f.copy()
>>> import copy
>>> g = copy.deepcopy(f)

Copying utilizes :ref:`LAMA copying functionality <LAMA_copying>`.

.. _Subspacing:

Subspacing
----------

Subspacing a field means subspacing its data array and its domain in a
consistent manner.

A field may be subspaced via its `~Field.subspace` attribute. This
attribute returns an object which may be :ref:`indexed <indexing>` to
select a subspace by data array index values (``f.subspace[indices]``)
or :ref:`called <calling>` to select a subspace by dimension
coordinate array values (``f.subspace(**coordinate_values)``):

>>> g = f.subspace[0, ...]
>>> g = f.subspace(latitude=30, longitude=cf.wi(0, 90, 'degrees'))

The result of subspacing a field is a new, independent field whose
data array and, crucially, any data arrays within the field's metadata
(such as coordinates, ancillary variables, coordinate references,
*etc.*) are appropriate subspaces of their originals:

>>> print f
air_temperature field summary
-----------------------------
Data           : air_temperature(time(12), latitude(73), longitude(96)) K
Cell methods   : time: mean
Axes           : time(12) = [1860-01-16 12:00:00, ..., 1860-12-16 12:00:00]
               : latitude(73) = [-90, ..., 90] degrees_north
               : longitude(96) = [0, ..., 356.25] degrees_east
               : height(1) = [2] m
>>> g = f.subspace[-1, :, 48::-1]
>>> print g
air_temperature field summary
-----------------------------
Data           : air_temperature(time(1), latitude(73), longitude(49)) K
Cell methods   : time: mean
Axes           : time(1) = [1860-12-16 12:00:00]
               : latitude(73) = [-90, ..., 90] degrees_north
               : longitude(49) = [180, ..., 0] degrees_east
               : height(1) = [2] m

Subspacing utilizes :ref:`LAMA subspacing functionality
<LAMA_subspacing>`.

.. _indexing:

Indexing
^^^^^^^^

Subspacing by axis indices uses an extended Python slicing syntax,
which is similar to :ref:`numpy array indexing
<numpy:arrays.indexing>`:

>>> f.shape
(12, 73, 96)
>>> f.subspace[...].shape
(12, 73, 96)
>>> f.subspace[slice(0, 12), :, 10:0:-2].shape
(12, 73, 5)
>>> f.subspace[..., f.coord('longitude')<180].shape
(12, 73, 48)

There are three extensions to the numpy indexing functionality:

* Size 1 axes are never removed.

  An integer index *i* takes the *i*-th element but does not reduce
  the rank of the output array by one:

  >>> f.shape
  (12, 73, 96)
  >>> f.subspace[0].shape
  (1, 73, 96)
  >>> f.subspace[3, slice(10, 0, -2), 95:93:-1].shape
  (1, 5, 2)

* The indices for each axis work independently.

  When more than one axis’s slice is a 1-d boolean sequence or 1-d
  sequence of integers, then these indices work independently along
  each axis (similar to the way vector subscripts work in Fortran),
  rather than by their elements:

  >>> f.shape
  (12, 73, 96)
  >>> f.subspace[:, [0, 72], [5, 4, 3]].shape
  (12, 2, 3)

  Note that the indices of the last example would raise an error when
  given to a numpy array.

* Boolean indices may be any object which exposes the numpy array
  interface, such as the field's coordinate objects:

  >>> f.subspace[:, f.coord('latitude')<0].shape
  (12, 36, 96)


.. _calling:

Coordinate values
^^^^^^^^^^^^^^^^^

Subspacing by values of 1-d coordinates allows a subspaced field to be
defined via coordinate values of its domain. The benefits of
subspacing in this fashion are:

* The axes to be subspaced may identified by name.

* The position in the data array of each axis need not be known and
  the axes to be subspaced may be given in any order.

* Axes for which no subspacing is required need not be specified.

* Size 1 axes of the domain which are not spanned by the data array
  may be specified.

Coordinate values are provided as keyword arguments to a call to the
`~Field.subspace` attribute. Coordinates are identified by their
`~Coordinate.identity` or their axis's identifier in the field's
domain.

>>> f.subspace().shape
(12, 73, 96)
>>> f.subspace(latitude=0).shape
(12, 1, 96)
>>> f.subspace(latitude=cf.wi(-30, 30)).shape
(12, 25, 96)
>>> f.subspace(long=cf.ge(270, 'degrees_east'), lat=cf.set([0, 2.5, 10])).shape
(12, 3, 24)
>>> f.subspace(latitude=cf.lt(0, 'degrees_north'))
(12, 36, 96)
>>> f.subspace(latitude=[cf.lt(0, 'degrees_north'), 90])
(12, 37, 96)
>>> import math
>>> f.subspace('exact', longitude=cf.lt(math.pi, 'radian'), height=2)
(12, 73, 48)
>>> f.subspace(height=cf.gt(3))
IndexError: No indices found for 'height' values gt 3
>>> f.subspace(dim2=3.75).shape
(12, 1, 96)
>>> f.subspace(time=cf.le(cf.dt('1860-06-16 12:00:00')).shape
(6, 73, 96)
>>> f.subspace(time=cf.gt(cf.dt(1860, 7)),shape
(5, 73, 96)

Note that if a comparison function (such as `cf.wi`) does not specify
any units, then the units of the named coordinate are assumed.

.. _fm_cyclic_axes:

Cyclic axes
-----------


>>> f.subspace[..., -10, 10]
(12, 25, 96)
>>> f.subspace(longitude=cf.wi(-30, 30))
(12, 3, 24)
>>> f.subspace(long=cf.ge(270, 'degrees_east'), lat=cf.set([0, 2.5, 10])).shape
(12, 3, 24)


.. _fm_assignment:

Assignment
----------

Elements of a field's data array may be changed by assigning values
directly to a subspace of the field defined by the
`~cf.Field.subspace` attribute or by using the `~cf.Field.setdata`
method.

Assignment uses :ref:`LAMA functionality <LAMA>`, so it is possible to
assign to fields which are larger than the available memory.

Array elements may be set from a field or logically scalar object,
using the same :ref:`metadata-aware broadcasting rules <broadcasting>`
as for field arithmetic and comparison operations. In the
`~cf.Field.subspace` case, the object attribute must be broadcastable
to the defined subspace, whilst in the `~cf.Field.setdata` case the
object must be broadcastable to the field itself.

The treatment of missing data elements depends on the value of field's
`~cf.Field.hardmask` attribute. If it is True then masked elements
will not unmasked, otherwise masked elements may be set to any
value. In either case, unmasked elements may be set to any value
(including missing data).

Set all values to 273.15:

>>> f.subspace[...] = 273.15

or equivalently:

>>> f.setdata(273.15, None)

Double the values where longitude is zero degrees:

>>> index = f.indices(longitude=0)
>>> f.subspace[index] = f.suspace[index] * 2

or equivalently:

>>> f.setdata(f*2, None, longitude=0)

Assignment by one dimensionsal coordinate values is also possible. For
example, to set all values lying between 210 and 270 degrees longitude
and -5 and 5 degrees latitude to missing data:

>>> f.setdata(cf.masked, None,
...           longitude=cf.wi(210, 270, 'degrees_east'),
...           latitude=cf.wi(-5, 5, 'degrees_north'))

Set all values less than 10 Celcius to 10 Celcius:

>>> x = cf.Data(10, 'K @ 273.15')
>>> f.setdata(x, None, f<x)

Set all values less than 273.15 to 1 and all other values to -1:

>>> f.setdata(1, -1, f<273.15)

Set all values less than 280 and greater than 290 to missing data and
multiply all other elements by -1:

>>> f.setdata(cf.masked, -f, (f<280) | (f>290))


Selection
---------

Field selection
^^^^^^^^^^^^^^^

Fields may be tested for matching given conditions with the
`~Field.match` method and selected by matching given conditions with
the `~FieldList.select` method. Both methods share the same
interface. Conditions may be given on:

=============================  ============================================== 
Field conditions               Example
=============================  ============================================== 
CF properties                  ``'standard_name'``
Coordinate values              ``coord={'latitude': 0}``
Coordinate cell sizes          ``cellsize={'time': cf.wi(28, 31, 'days')}``
Number of axes                 ``rank=3``
=============================  ============================================== 

For example:

>>> f
[<CF Field: eastward_wind(grid_latitude(110), grid_longitude(106)) m s-1>,
 <CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>]
>>> f.match('air_temperature')
[False, True]
>>>  f.select('air_temperature')
[<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>]

>>>  f.select('air_temperature', rank=2)
[]
>>>  f.select('air_temperature', cvalue={'latitude': cf.gt(0)}, rank=cf.ge(3))
[<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>]

Any of the `~Field.match` and `~FieldList.select` arguments may also
be used with `cf.read` to select fields when reading from files:

>>> f = cf.read('file*.nc', match={'match': 'air_temperature', 'rank': cf.gt(2)})

Selection may also be applied to a field, rather than a field list. In
this case, the `~Field.select` method returns the field itself, if
there is a match:

>>> f
<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>
>>> f.match('air_temperature')
True
>>> f.select('air_temperature')
<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>
>>> f.select('eastward_wind')
[]

Domain item selection
^^^^^^^^^^^^^^^^^^^^^

asdasds

Aggregation
-----------

Fields are aggregated into as few multidimensional fields as possible
with the `cf.aggregate` function, which implements the `CF aggregation
rules
<http://www.met.reading.ac.uk/~david/cf_aggregation_rules.html>`_.

>>> f
[<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>,
 <CF Field: air_temperature(latitude(73), longitude(96)) K @ 273.15>]
>>> print f
air_temperature field summary
-----------------------------
Data           : air_temperature(time(12), latitude(73), longitude(96)) K
Cell methods   : time: mean
AXes           : time(12) = [1860-01-16 12:00:00, ..., 1860-12-16 12:00:00]
               : latitude(73) = [-90, ..., 90] degrees_north
               : longitude(96) = [0, ..., 356.25] degrees_east
               : height(1) = [2] m
air_temperature field summary
-----------------------------
Data           : air_temperature(latitude(73), longitude(96)) K @ 273.15
Cell methods   : time: mean
Axes           : time(12) = [1859-12-16 12:00:00]
               : longitude(96) = [356.25, ..., 0] degrees_east
               : latitude(73) = [-90, ..., 90] degrees_north
               : height(1) = [2] m
...
>>> g = cf.aggregate(f)
>>> g
[<CF Field: air_temperature(time(13), latitude(73), longitude(96)) K>]
>>> print g
air_temperature field summary
-----------------------------
Data           : air_temperature(time(13), latitude(73), longitude(96)) K
Cell methods   : time: mean
Axes           : time(13) = [1859-12-16 12:00:00, ..., 1860-12-16 12:00:00]
               : latitude(73) = [-90, ..., 90] degrees_north
               : longitude(96) = [0, ..., 356.25] degrees_east
               : height(1) = [2] m

By default, the fields returned by `cf.read` have been aggregated:

>>> f = cf.read('file*.nc')
>>> len(f)
1
>>> f = cf.read('file*.nc', aggregate=False)
>>> len(f)
12


.. _Arithmetic-and-comparison:

Arithmetic and comparison
-------------------------

Arithmetic, bitwise and comparison operations are defined on a field
as element-wise operations on its data array which yield a new
`cf.Field` object or, for augmented assignments, modify the field's
data array in-place.

A field's data array is modified in a very similar way to how a numpy
array would be modified in the same operation, i.e. :ref:`broadcasting
<broadcasting>` ensures that the operands are compatible and the data
array is modified element-wise.

Broadcasting is metadata-aware and will automatically account for
arbitrary configurations, such as axis order, but will not allow
fields with incompatible metadata to be combined, such as adding a
field of height to one of temperature.

The :ref:`resulting field's metadata <resulting_metadata>` will be
very similar to that of the operands which are also
fields. Differences arise when the existing metadata can not correctly
describe the newly created field. For example, when dividing a field
with units of *metres* by one with units of *seconds*, the resulting
field will have units of *metres per second*.

Arithmetic and comparison utilizes :ref:`LAMA functionality <LAMA>` so
data arrays larger than the available physical memory may be operated
on.

.. _broadcasting:

Broadcasting
^^^^^^^^^^^^

The term broadcasting describes how data arrays of the operands with
different shapes are treated during arithmetic, comparison and
assignment operations. Subject to certain constraints, the smaller
array is "broadcast" across the larger array so that they have
compatible shapes.

The general broadcasting rules are similar to the :mod:`broadcasting
rules implemented in numpy <numpy.doc.broadcasting>`, the only
difference occurring when both operands are fields, in which case the
fields are temporarily conformed so that:

* The fields have matching units.

* Axes are aligned according to their coordinates' metadata to ensure
  that matching axes are broadcast against each other.

* Common axes have matching axis directions.

This restructuring of the field ensures that the matching axes are
broadcast against each other.

Broadcasting is done without making needless copies of data and so is
usually very efficient.


Valid operands
^^^^^^^^^^^^^^

A field may be combined or compared with the following objects:

+----------------+----------------------------------------------------+
| Object         | Description                                        |
+================+====================================================+
|:py:obj:`int`,  | The field's data array is combined with            |
|:py:obj:`long`, | the python scalar                                  |
|:py:obj:`float` |                                                    |
+----------------+----------------------------------------------------+
|`cf.Data`       | The field's data array                             |
|with size 1     | is combined with the `cf.Data` object's scalar     |
|                | value, taking into account:                        |
|                |                                                    |
|                | * Different but equivalent units                   |
+----------------+----------------------------------------------------+
|`cf.Field`      | The two field's must satisfy the field combination |
|                | rules. The fields' data arrays and domains are     |
|                | combined taking into account:                      |
|                |                                                    |
|                | * Axis identities                                  |
|                | * Array units                                      |
|                | * Axis orders                                      |
|                | * Axis directions                                  |
|                | * Missing data values		              |
+----------------+----------------------------------------------------+


A field may appear on the left or right hand side of an operator.

.. warning::

   Combining a numpy array on the *left* with a field on the *right*
   does work, but will give generally unintended results -- namely a
   numpy array of fields.


.. _resulting_metadata:

Resulting metadata
^^^^^^^^^^^^^^^^^^

When creating a new field which has different physical properties to
the input field(s) the units will also need to be changed:

>>> f.units
'K'
>>> f += 2
>>> f.units
'K'

>>> f.units
'K'
>>> f **= 2
>>> f.units
'K2'

>>> f.units, g.units
('m', 's')
>>> h = f / g
>>> h.units
'm s-1'

When creating a new field which has a different domain to the input
fields, the new domain will in general contain the superset of the
axes of the two input fields, but may not have some of either input
field's auxiliary coordinates or size 1 dimension coordinates. Refer
to the field combination rules for details.


.. _floating_point_errors:

Floating point errors
^^^^^^^^^^^^^^^^^^^^^

It is possible to set the action to take when an arithmetic operation
produces one of the following floating-point errors:

.. tabularcolumns:: |l|l|
=================  =================================
Error              Description                      
=================  =================================
Division by zero   Infinite result obtained from    
                   finite numbers.

Overflow           Result too large to be expressed.

Invalid operation  Result is not an expressible     
                   number, typically indicates that 
                   a NaN was produced.

Underflow          Result so close to zero that some
                   precision was lost.
=================  =================================

For each type of error, one of the following actions may be chosen:

* Take no action. Allows invalid values to occur in the result data
  array.

* Print a `RuntimeWarning` (via the Python `warnings` module). Allows
  invalid values to occur in the result data array.

* Raise a `FloatingPointError` exception.

The treatment of floating-point errors is set with
`cf.Data.seterr`. Converting invalid numbers to masked values after an
arithmetic operation may be done with the `cf.Field.mask_invalid`
method. It is also possible to mask invalid numbers during arithmetic
operations (see `cf.Data.mask_fpe`).

Note that these setting apply to all data array arithmetic within the
`cf` package.

Statistical operations
----------------------

Axes of a field may be collapsed by statistical methods with the
`cf.Field.collapse` method. Collapsing an axis involves reducing its
size with a given (typically statistical) method.

By default all axes with size greater than 1 are collapsed completely
with the given method. For example, to find the minumum of the data
array:

>>> g = f.collapse('min')

By default the calculations of means, standard deviations and
variances use a combination of volume, area and linear weights based
on the field's metadata. For example to find the mean of the data
array, weighted where possible:

>>> g = f.collapse('mean')

Specific weights may be forced with the weights parameter. For example
to find the variance of the data array, weighting the X and Y axes by
cell area, the T axis linearly and leaving all other axes unweighted:

>>> g = f.collapse('variance', weights=['area', 'T'])

A subset of the axes may be collapsed. For example, to find the mean
over the time axis:

>>> f
<CF Field: air_temperature(time(12), latitude(73), longitude(96) K>
>>> g = f.collapse('T: mean')
>>> g
<CF Field: air_temperature(time(1), latitude(73), longitude(96) K>

For example, to find the maximum over the time and height axes:

>>> g = f.collapse('T: Z: max')

or, equivalently:

>>> g = f.collapse('max', axes=['T', 'Z'])

An ordered sequence of collapses over different (or the same) subsets
of the axes may be specified. For example, to first find the mean over
the time axis and subequently the standard deviation over the latitude
and longitude axes:

>>> g = f.collapse('T: mean area: sd')

or, equivalently, in two steps:

>>> g = f.collapse('mean', axes='T').collapse('sd', axes='area')

Grouped collapses are possible, whereby groups of elements along an
axis are defined and each group is collapsed independently. The
collapsed groups are concatenated so that the collapsed axis in the
output field has a size equal to the number of groups. For example, to
find the variance along the longitude axis within each group of size
10 degrees:

>>> g = f.collapse('longitude: variance', group=cf.Data(10, 'degrees'))

Climatological statistics (a type of grouped collapse) as defined by
the CF conventions may be specified. For example, to collapse a time
axis into multiannual means of calendar monthly minima:

>>> g = f.collapse('time: minimum within years T: mean over years',
...                 within_years=cf.M())

In all collapses, missing data array elements are accounted for in the
calculation.

The following collapse methods are available, over any subset of the
axes:

=========================  =====================================================
Method                     Notes
=========================  =====================================================
Maximum                    The maximum of the values.
                           
Minimum                    The minimum of the values.
                                    
Sum                        The sum of the values.
                           
Mid-range                  The average of the maximum and the minimum of the
                           values.
                           
Range                      The absolute difference between the maximum and
                           the minimum of the values.
                           
Mean                       The unweighted mean, :math:`m`, of :math:`N`
                           values :math:`x_i` is
                           
                           .. math:: m=\frac{1}{N}\sum_{i=1}^{N} x_i
                           
                           The weighted mean, :math:`\tilde{m}`, of :math:`N`
                           values :math:`x_i` with corresponding weights
                           :math:`w_i` is
                           

                           .. math:: \tilde{m}=\frac{1}{\sum_{i=1}^{N} w_i}
                                               \sum_{i=1}^{N} w_i x_i
                           
Standard deviation         The unweighted standard deviation, :math:`s`, of
                           :math:`N` values :math:`x_i` with mean :math:`m`
                           and with :math:`N-ddof` degrees of freedom
                           (:math:`ddof\ge0`) is
                           
                           .. math:: s=\sqrt{\frac{1}{N-ddof}
                                       \sum_{i=1}^{N} (x_i - m)^2}
                           
                           The weighted standard deviation,
                           :math:`\tilde{s}_N`, of :math:`N` values
                           :math:`x_i` with corresponding weights
                           :math:`w_i`, weighted mean
                           :math:`\tilde{m}` and with :math:`N`
                           degrees of freedom is
                           
                           .. math:: \tilde{s}_N=\sqrt{\frac{1}
                                         {\sum_{i=1}^{N} w_i}
                                         \sum_{i=1}^{N} w_i(x_i -
                                         \tilde{m})^2}
                           
                           The weighted standard deviation,
                           :math:`\tilde{s}`, of :math:`N` values
                           :math:`x_i` with corresponding weights
                           :math:`w_i` and with :math:`N-ddof` degrees
                           of freedom :math:`(ddof>0)` is
                           
                           .. math:: \tilde{s}=\sqrt{ \frac{a
                                     \sum_{i=1}^{N} w_i}{a
                                     \sum_{i=1}^{N} w_i - ddof}}
                                     \tilde{s}_N
                           
                           where :math:`a` is the smallest positive
                           number whose product with each weight is an
                           integer. :math:`a \sum_{i=1}^{N} w_i` is
                           the size of a new sample created by each
                           :math:`x_i` having :math:`aw_i` repeats. In
                           practice, :math:`a` may not exist or may be
                           difficult to calculate, so :math:`a` is
                           either set to a predetermined value or an
                           approximate value is calculated (see
                           `cf.Field.collapse` for details).
                           
Variance                   The variance is the square of the standard
                           deviation.
                           
Sample size                The sample size, :math:`N`, as would be used for 
                           other statistical calculations.
                           
Sum of weights             The sum of sample weights,
                           :math:`\sum_{i=1}^{N} w_i`, as would be
                           used for other statistical calculations.

Sum of squares of weights  The sum of squares of sample weights,
                           :math:`\sum_{i=1}^{N} {w_i}^{2}`,
                           as would be used for other statistical
                           calculations.
=========================  =====================================================

See `cf.Field.collapse` for more details.

Regridding operations
---------------------

A field may be regridded onto a new latitude-longitude grid:

>>> f
<CF Field: air_temperature(time(12), latitude(73), longitude(96) K>
>>> g
<CF Field: precipitation(time(24), longitude(128), latitude(64)) kg m-2 s-1>
>>> h = f.regrids(g)
>>> h
<CF Field: air_temperature(time(12), longitude(128), latitude(64) K>

By default the interpolation is first-order conservative, but bilinear
interpolation is also possible. The missing data masks of the field
and the new grid are aslo taken into account. 

See `cf.Field.regrids` for more details.

Manipulating other variables
----------------------------

A field is a subclass of `cf.Variable`, and that class and other
subclasses of `cf.Variable` share generally similar behaviours and
methods:

========================  ===============================================
Class		          Description
========================  ===============================================
`cf.AuxiliaryCoordinate`  A CF auxiliary coordinate construct.

`cf.CellMeasure`          A CF cell measure construct containing
                          information that is needed about the size,
                          shape or location of the field's cells.
		          
`cf.Coordinate`           Base class for storing a coordinate.

`cf.CoordinateBounds`     A CF coordinate's bounds object containing cell
                          boundaries or intervals of climatological time.
	          
`cf.DimensionCoordinate`  A CF dimension coordinate construct.
		          
`cf.Variable`             Base class for storing a data array with
                          metadata.
========================  ===============================================

In general, different axis identities, different axis orders and
different axis directions are not considered, since these objects do
not contain a coordinate system required to define these properties
(unlike a field).

Coordinates
^^^^^^^^^^^

Coordinates are a special case as they may contain a data array for
their coordinate bounds which needs to be treated consistently with
the main coordinate array. If a coordinate has bounds then all
coordinate methods also operate on the bounds in a consistent manner:

>>> c
<CF Coordinate: latitude(73, 96)>
>>> c.bounds
<CF CoordinateBounds: (73, 96, 4)>
>>> d = c.subspace[0:10]
>>> d.shape
(10, 96)
>>> d.bounds.shape
(10, 96, 4)
>>> d.transpose([1, 0])
>>> d.shape
(96, 10)
>>> d.bounds.shape
(96, 10, 4)

.. note:: 

   If the coordinate bounds are operated on independently, care should
   be taken not to break consistency with the parent coordinate.

