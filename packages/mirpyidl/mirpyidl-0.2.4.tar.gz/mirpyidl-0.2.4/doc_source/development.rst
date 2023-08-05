
*******************
 Development Notes 
*******************

This page contains information for developers of mirpyidl.


Building the documentation
==========================

To build the mirpyidl documentation separately from the main installation, the type following from the mirpyidl source directory::

    sphinx-build -b html doc_source doc_build


Updating the repository
=======================

First commit the code locally::

    git add -A .
    git diff --staged
    git commit -m "Some useful comment"

Then update the bitbuket repository::

    git push bitbucket --all

    
Testing
=======

These are instructions for testing on OS X.  Testing on Linux is similar.


Testing needs to be done separately for both Python 2.7 and Python 3.4.  Switch versions by using one of the following::

    sudo port select --set python python27
    sudo port select --set python python34

Uninstall mirpyidl if was previously installed (note that this will install mirpyidl if it was not installed)::

    sudo pip uninstall mirpyidl

Clean the current development directory::

    python setup.py clean --all

Build mirpyidl::

    python setup.py build_ext --inplace

Run the tests for both the `mirpyidl` and the `mirpyidlrp` versions.::

    python testing/run_examples.py
    python testing/run_examples.py --idlrpc

    python testing/run_tests.py
    python testing/run_tests.py --idlrpc

Now switch python versions and start over again.


Updating the public release
===========================

After doing a repository update we need to also update the website and pypi entry. Generally we will only do this afer creating a new release.

First update setup.py with the new version number and commit the changes.

To tag a new release use::

    git tag -a 0.1.3 -m "Version 0.1.3"
    git push --tags bitbucket master
    

To update the website do the following::

    cd ../bitbucket.org
    sphinx-build -b html ../mirpyidl/doc_source/ mirpyidl/
    git add -A .
    git commit -m "Updated the mirpyidl documentation"
    git push bitbucket master

To update the pyPI repository::

    cd ../mirpyidl
    python setup.py clean --all
    python setup.py register
    python setup.py sdist upload


Testing the public release
==========================

Hopefully I've already done testing before making a release, but it is still good to do a final check.

Here is my tesing procedure for OS X::

   cd mirpyidl
   sudo port select --set python python27
   sudo pip-2.7 uninstall mirpyidl

   sudo pip-2.7 install mirpyidl
   python tests/examples.py

   sudo port select --set python python34
   sudo pip-3.4 uninstall mirpyidl

   sudo pip-3.4 install mirpyidl
   python tests/examples.py
