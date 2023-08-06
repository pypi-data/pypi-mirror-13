
**************
 Introduction
**************


A library to call IDL (Interactive Data Language) from python.  Allows trasparent wrapping of IDL routines and objects as well as arbitrary execution of IDL code.  

|mirpyidl| requires a licenced installation of IDL .  Data is transfered back and forth using either the CallableIDL (idl_export.h) or the IDLRPC (idl_rpc.h) APIs, both of which are distrbuted with IDL. 

All standard IDL and python/numpy datatypes are supported, and |mirpyidl| transparently handles translating between equivilent datatypes. This includes translation between IDL structures and python dictionaries.

|mirpyidl| is hosted at: 
    https://bitbucket.org/amicitas/mirpyidl

Documentation can be found at:
    http://amicitas.bitbucket.org/mirpyidl


|mirpyidl| was written by Novimir A. Pablant, and is released under an MIT licence.

.. warning::

    |mirpyidl| is still in the develpment stage.  It works very well for my particular needs, but does not yet provide a complete solution.  If you run into problems, please let me know (or better yet, submit a pull request with a fix).  The documenation is also only partially finished, so there may be mistakes or missing information.


Dependencies
============

- IDL (8.0 or later)
- python (2.7, 3.0 or later)

  * numpy
  * psutil

- cython

|mirpyidl| requires a licenced installation of IDL.  Currently only IDL 8.0 or later is spported due to the additon of the ``HASH`` and ``LIST`` types. Older versions may be compatible but are untested.


|mirpyidl| is currently only supported on linux and OS X.  It should also work fine on windows, but the ``setup.py`` script has not been setup to find the IDL installation directory.  If you want to give this a try on windows, just add the appropriate directories to setup.py. (If it works submit a pull reqeust so that I can update the public package.)


Installation
============

|mirpyidl| can be installed from pypi.org using either easy_install or pip::

    easy_install mirpyidl
    pip install mirpyidl
    
|mirpyidl| can be installed using the following command::
  
    python setup.py install

For more control over the installation, all standard ``distutils`` commands are available.  If ``setuputils`` is installed, then the extended commands will also work.


If a full installation is not desired, the |mirpyidl| module can be built in place using::

    python setup.py build_ext --inplace

This will create the ``mirpyidl.so`` shared library which can then be directly imported from python.


.. warning::
  On Mac OS X the setup script will change the installation names of the libidl.dylib, libidl_rpc.dylib and related IDL libraries to be prefixed with `@rpath/`. This is the OS X standard way to specify run-path dependent libraries and is not known to have any side effects.


.. todo::

    Add windows stuff to the installation script.

Usage
=====

See the :ref:`examples` section for typical usage.


Limitations
===========

|mirpyidl| has several limitations due to differences between the IDL and python languages, and the |mirpyidl| data transfer mechanism.


Memory Usage
------------

When using |mirpyidl|, data cannot be shared between IDL and python, instead it is copied back and forth. This has the effect of (at least) doubling the required memory to handle any data that will be transfered.  When functions or methods are called, the results are removed from IDL after the transfer to python, so the memory doubling will only be transient.  

The memory situation when transfering data between structures, lists and hashes is worse.  In order to do these types of transfers, each element must be copied to a temporary variable in IDL as part of the transfer.  This means that the memory usage is *at least* tripled during the transfer.  For nested structures, hashes or lists, memory usage can be much worse. 

.. todo::

    I need to change the code that deals with transfering structures, lists, and hashes to be more efficent when deling with nesting.  This should be fairly straight forward.  I just need to check whether an element is a structure before copying to a temp variable, then recursivly call getStructure with the appropriate nested name.  With this fix my memory usage should never be more than triple the data size.
 

Speed
-----

Data transferes between idl and python are done entirely in memory, so data transfers will be quite fast. However, there is some overhead involved in calling IDL and transfering the data. This overhead will not generaly be significant unless simple IDL functions are being called repeatedly from python. In addtion, the need to create multiple copies of the data, partuclarly when transfering structures, lists and hashes will have an effect on data transfer speed, especially for large data sets.  


Argument and Keyword Passing
----------------------------

When using the standard |mirpyidl| wrapping methods, only the single return value of IDL functions and methods will be returned in python.  Any variables passed to the wrapped routine as arguments or keywords will remain unchanged. It is entirely possible to wrap IDL routines that modify the input variables, however this currently requires writing custom wrappers for each case. 

This design was chosen for several reasons:  

First, here is a significant difference in how IDL and python deal with passing data into and out of routines.  IDL, by default, always passes variables by reference.  This means that if input variables are changed inside a IDL routine, the changes are always reflected in calling scope. Python on the other hard always passes variables by object name.  Certain objects in python are immutable (string, int, etc.), and changes to those types of variables inside the routine will not be reflected in the calling scope.  Because of these differences, it not possible in many cases to have a python routine behave exactly like an IDL routine.  

Second, there is no way to know, from the python side, whether any of the IDL input parameters were modified. Since data needs to be explicity transfered between IDL and python, to support changes to the input variables it would be necessary to pass all of the input varibales back to python after the call to the IDL routine.  This is entirely feasible, but could potentially add significant unessary overhead.

.. todo::

    I should add a special method to simulate the IDL behavior with respect to input variables. This method would require all arguments and keywords to be passed in using two ``OrderedDict`` objects.  After the IDL routine is called, all of input variables, as well as the result, would be transfered back to python.

    
.. _examples:

Examples and Tutorial
=====================

The best way to learn how to use |mirpyidl| is by example.  This section is written in the style of a tutorial, so I suggest reading through all the examples in order.

With default usage |mirpyidl| will start an IDL interpreter internally.  See :ref:`idlrpc` for documentaiton on how to connect to and existing `idlrpc` server instead.


Executing Idl Code
------------------

Here is a simple example for executing arbitrary IDL code from python:

.. code-block:: python

    # Import mirpyidl.
    import mirpyidl as idl

    # Execute a command in IDL.
    # This will print 'Hello mom!' in the idlrpc window.
    idl.execute("PRINT, 'Hello mom!'")


As a more complex example, we will now send some data back and forth between IDL and python.

.. code-block:: python

    import numpy as np
    import mirpyidl as idl

    # Create a numpy array in python.
    py_array = np.random.normal(size=1000)

    # Copy this data to IDL.
    idl.setVariable('idl_array', py_array)

    # Calculate the standard devation and the mean in IDL.
    idl.execute('idl_stddev = STDDEV(idl_array)')
    idl.execute('idl_mean = MEAN(idl_array)')

    # Copy the results back to python.
    py_stddev = idl.getVariable('idl_stddev')
    py_mean = idl.getVariable('idl_mean')

    # Print out the results.
    print('Mean: {}, StdDev: {}'.format(py_mean, py_stddev))


.. note::

    The :py:mod:`pidlrpc` module has convenience methods :py:func:`ex`, :py:func:`set` and :py:func:`get` which are aliases for :py:func:`execute`, :py:func:`setVariable` and :py:func:`getVariable` respectively. These can be useful shorthand in certain cases, such as working on the command line, but should be avoided in general as the long names are more clear.

 
Calling Functions and Procedures
--------------------------------

In the examples above we used just the most basic commands, :py:func:`execute`, :py:func:`setVariable` and :py:func:`getVariable`, to control an IDL session and pass data between IDL and python. In these next examples we use the |mirpyidl| wrapping routines to do simplify the code in the previous example significantly.


.. code-block:: python

    import numpy as np
    import mirpyidl as idl

    # Create a numpy array in python.
    py_array = np.random.normal(size=1000)

    # Calculate the standard devication and mean using IDL.
    py_stddev = idl.callFunction('STDDEV', [py_array])
    py_mean = idl.callFunction('MEAN', [py_array])

    # Print out the results.
    print('Mean: {}, StdDev: {}'.format(py_mean, py_stddev))




In all the examples so far, we have been calling the module level functions. It is also possible to create an :py:class:`PyIDL` class and call the equivilent object methods instead.  This will have slightly less overhead since a new :py:class:`PyIDL` object is not created for every call. Notice that the following code looks exactly the same as before except for the import statement and the creation of the ``idl`` object.

.. code-block:: python
 
    import numpy as np
    from mirpyidl import PyIDL

    idl = PyIDL()

    # Create a numpy array in python.
    py_array = np.random.normal(size=1000)

    # Calculate the standard devication and mean using IDL.
    py_stddev = idl.callFunction('STDDEV', [py_array])
    py_mean = idl.callFunction('MEAN', [py_array])



Wraping Functions and Procedures
--------------------------------

Wrapping functions or procedures looks very similar to the example above.  Let say we want to wrap the IDL ``STDDEV`` and ``MEAN`` functions in python module name ``idlmath``.

.. code-block:: python

    # idlmath.py

    import mirpyidl as idl

    def stddev(input):
        return idl.callFunction('STDDEV', [input])

    def mean(input):
        return idl.callFunction('MEAN', [input])

That's all there is to it.  Now we can call these functions as though they were native python funcitons.

.. code-block:: python

    import numpy as np
    import idlmath

    array = np.random.normal(size=1000)

    # Here we transparently call the wrapped IDL functions.
    mean = idlmath.mean(array)
    stddev = idlmath.stddev(array)


While this was already easy, we can use pythons parameter passing mechanisms to simpify our wrapper ever further. This pattern will work for any IDL function or procedure.

.. code-block:: python

    # idlmath.py

    import mirpyidl as idl

    def stddev(*args, **kwargs):
        return idl.callFunction('STDDEV', args, kwargs)

    def mean(*args, **kwargs):
        return idl.callFunction('MEAN', args, kwargs)



Wrapping Objects
----------------

|mirpyidl| also has the ability to fully wrap IDL objects.
           
Python wrapping objects should all inherit from :py:class:`PyIDLObject`.  Here I show an example of wrapping a hypothetical Gaussian object.

.. code-block:: python


    # _IdlGaussan.py

    from mirpyidl import PyIDLObject

    class IdlGaussian(PyIDLObject):

        # Define the the IDL command needed to create the object.
        _creation_command = "OBJ_NEW"
        _creation_params = ['GAUSSIAN']
        _creation_keywords = None 

        def evaluate(self, *args, **kwargs):
            return self.callMethodFunction('EVALUATE', args, kwargs)

        def setParam(self, *args, **kwargs):
            return self.callMethodPro('SET_PARAM', args, kwargs)

        def getParam(self, *args, **kwargs):
            return self.callMethodFunction('GET_PARAM', args, kwargs)

            
.. _idlrpc:

Using an idlrpc server
======================

|mirpyidl| can also connect to a running ``idlrpc`` instance rather than starting an IDL interpreter internally. To use an idlrpc connection simply use ``import mirpyidl`` instead of ``import mirpyidlrpc``. All of the examples above will work equivalently with this change::

.. code-block:: python
                
    # Import mirpyidlrpc to use the idlrpc interface.
    import mirpyidlrpc

    # We can also import individual classes as before.
    from mirpyidlrpc import PyIdl

When using the idlrpc interface an ``idlrpc`` server will need to be started in a separate process. This can be done using the following command (which is part of any standard IDL installation)::

    idlrpc


    
.. |mirpyidl| raw:: html

    <span style="font-variant:small-caps">mirpyidl</span>


