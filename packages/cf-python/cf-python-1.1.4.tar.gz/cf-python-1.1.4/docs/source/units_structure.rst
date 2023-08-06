.. currentmodule:: cf
.. default-role:: obj

.. _units:

Units handling by the `cf.Units` object
=======================================

A field (as well as any other object which :ref:`inherits
<inheritance_diagrams>` from `cf.Variable`) always contains a
`cf.Units` object which gives the physical units of the values
contained in its data array.

The `cf.Units` object is stored in the field's `~Field.Units`
attribute but may also be accessed through the field's `~Field.units`
and `~Field.calendar` CF properties, which may take any value allowed
by the `CF conventions
<http://cf-pcmdi.llnl.gov/documents/cf-conventions/latest-cf-conventions-document-1>`_. In
particular, the value of the `~Field.units` CF property is a string
that can be recognized by `UNIDATA's Udunits-2 package
<http://www.unidata.ucar.edu/software/udunits/>`_, with a few
exceptions for greater consistency with CF. These are detailed by the
`cf.Units` object.

Assignment
----------

The Field's units may be assigned directly to its `cf.Units` object:

>>> f.Units.units = 'days since 1-1-1'
>>> f.Units.calendar = 'noleap'

>>> f.Units = cf.Units('metre')

But the same result is achieved by assigning to the field's
`~Field.units` and `~Field.calendar` CF properties:

>>> f.units = 'days since 1-1-1'
>>> f.calendar = 'noleap'
>>> f.Units
<CF Units: days since 1-1-1 calendar=noleap>
>>> f.units
'days since 1-1-1'
>>> f.calendar
'noleap'


Time units
----------

Time units may be given as durations of time or as an amount of time
since a reference time:

>>> f.units = 'day'
>>> f.units = 'seconds since 1992-10-8 15:15:42.5 -6:00'

.. note::

   It is recommended that the units ``'year'`` and ``'month'`` be used
   with caution, as explained in the following excerpt from the CF
   conventions: "The Udunits package defines a year to be exactly
   365.242198781 days (the interval between 2 successive passages of
   the sun through vernal equinox). It is not a calendar year. Udunits
   includes the following definitions for years: a common_year is 365
   days, a leap_year is 366 days, a Julian_year is 365.25 days, and a
   Gregorian_year is 365.2425 days. For similar reasons the unit
   ``'month'``, which is defined to be exactly year/12, should also be
   used with caution."

Calendar
^^^^^^^^

The date given in reference time units is always associated with one
of the calendars recognized by the CF conventions and may be set with
the *calendar* CF property (on the field or Units object).

If the calendar is not set then, as in the CF conventions, for the
purposes of calculation and comparison, it defaults to the mixed
Gregorian/Julian calendar as defined by Udunits:

>>> f.units = 'days since 2000-1-1'
>>> f.calendar
AttributeError: Can't get 'Field' attribute 'calendar'
>>> g.units = 'days since 2000-1-1'
>>> g.calendar = 'gregorian'
>>> g.Units.equals(f.Units)
True

The calendar is ignored for units other than reference time units.

Changing units
--------------

Changing units to equivalent units causes the variable's data array
values to be modified in place (if required) when they are next
accessed, and not before:

>>> f.units
'metre'
>>> f.array
array([    0.,  1000.,  2000.,  3000.,  4000.])
>>> f.units = 'kilometre'
>>> f.units
'kilometre'
>>> f.array
array([ 0.,  1.,  2.,  3.,  4.])

>>> f.units
'hours since 2000-1-1'
>>> f.array
array([-1227192., -1227168., -1227144.])
>>> f.units = 'days since 1860-1-1'
>>> f.array
array([ 1.,  2.,  3.])

The `cf.Units` object may be operated on with augmented arithmetic
assignments and binary arithmetic operations:

>>> f.units
'kelvin'
>>> f.array
array([ 273.15,  274.15,  275.15,  276.15,  277.15])

>>> f.Units -= 273.15
>>> f.units
'K @ 273.15'
>>> f.array
array([ 0.,  1.,  2.,  3.,  4.])

>>> f.Units = f.Units + 273.15
>>> f.units
'K'
>>> f.array
array([ 273.15,  274.15,  275.15,  276.15,  277.15])

>>> f.units = 'K @ 237.15'
'K @ 273.15'
>>> f.array
array([ 0.,  1.,  2.,  3.,  4.])

If the field has a data array and its units are changed to
non-equivalent units then a :py:mod:`TypeError` will be raised when
the data are next accessed:

>>> f.units
'm s-1'
>>> f.units = 'K'
>>> f.array
TypeError: Units are not convertible: <CF Units: m s-1>, <CF Units: K>


Changing the calendar
^^^^^^^^^^^^^^^^^^^^^

.. warning:: 

   Do not change the calendar of reference time units in the current
   version. Whilst this is possible, it will almost certainly result
   in an incorrect interpretation of the data array or an
   error. Allowing the calendar to be changed is under development and
   will be available soon.

Equality and equivalence of units
---------------------------------

The `cf.Units` object has methods for assessing whether two units are
equivalent or equal, regardless of their exact string representations.

Two units are equivalent if and only if numeric values in one unit are
convertible to numeric values in the other unit (such as
``'kilometres'`` and ``'metres'``). Two units are equal if and only if
they are equivalent and their conversion is a scale factor of 1 (such
as ``'kilometres'`` and ``'1000 metres'``). Note that equivalence and
equality are based on internally stored binary representations of the
units, rather than their string representations.

>>> f.units = 'm/s'

>>> g.units = 'm s-1'
>>> f.Units == g.Units
True
>>> f.Units.equals(g.Units)
True

>>> g.units = 'km s-1'
>>> f.Units.equivalent(g.Units)
False

>>> f.units = 'days since 1987-12-3'
>>> g.units = 'hours since 2000-12-1'	
>>> f.Units == g.Units
False
>>> f.Units.equivalent(g.Units)
True


Coordinate units
----------------

The units of a coordinate's bounds are always the same as the
coordinate itself, and the units of the bounds automatically change
when a coordinate's units are changed:

>>> c.units
'degrees'
>>> c.bounds.units
'degrees'
>>> c.bounds.array
array([  0.,  90.])
>>> c.units = 'radians'
>>> c.bounds.units
'radians'
>>> c.bounds.array
array([ 0.        ,  1.57079633])

