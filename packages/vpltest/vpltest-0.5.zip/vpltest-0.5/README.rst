vpltest
=======

Background
----------
VPL (http://vpl.dis.ulpgc.es/) allows customizing evaluation process with custom execution files. This can be used for testing students' submissions with professional testing frameworks. ``vpltest`` makes this easier for Python assignments by translating output from `nose <https://nose.readthedocs.org>`_ or `pytest <http://pytest.org>`_ to the format required by VPL. 

.. note::

    You may want to use ``vpltest`` together with `edutest <http://edutest.readthedocs.org>`_.

Basic usage
-----------
1. Write normal `unittest <https://docs.python.org/3/library/unittest.html>`_, `nose <https://nose.readthedocs.org>`_ or `pytest <http://pytest.org>`_ tests without worrying about VPL.
2. Test your tests without worrying about VPL. 
3. Create a VPL activity and upload your test files under *Advanced settings => Execution files*.
4. Upload also *vpltest.py*
5. To *vpl_execution.sh* write following lines:


.. sourcecode:: bash
    
    #!/bin/bash
    python3 vpltest.py


Replace ``python3`` with ``python`` if you're using Python 2.


Command line arguments
----------------------
You can tweak ``vpltest`` with following command line arguments:

* ``--nose`` and ``--pytest`` select the framework for collecting and running the tests. If neither flag is present, ``vpltest`` uses the one which happens to be installed. It prefers nose if both are installed;
* ``--show-grade`` makes ``vpltest`` propose a grade based on how big part of the tests passed;
* ``--show-stacktrace`` includes stacktraces in the reports;
* ``--allow-deletion`` (see "Automatically keeping all execution files available");
* all other arguments are passed on to the testing framework.

Example. If you want ``vpltest`` to compute the grade, run your tests with pytest and make pytest run also doctests, then your *vpl_evaluation.sh* should be 

.. sourcecode:: bash
    
    #!/bin/bash
    python3 vpltest.py --show-grade --pytest --doctest-modules



Test discovery
--------------
By default all execution files matching *\*test\*.py* (except *vpltest.py*) are considered to be test files and are passed on to testing framework. You can override this by specifying test files in *vpl_evaluation.sh*, eg:

.. sourcecode:: bash
    
    #!/bin/bash
    python3 vpltest.py --show-grade --pytest basic_tests.py style_checks.py



Test discovery inside the modules are up to chosen framework.

Installing to server
--------------------
If you use ``vpltest`` a lot, then it makes sense to install it into your testing server so that you don't need to upload it every time. It can be installed with ``pip``, eg. ``sudo pip3 install pytest``.

Note that now ``python3 vpltest.py`` in your *vpl_execution.sh* won't do as there won't be *vpltest.py* in testing directory anymore. Use ``python3 -m vpltest`` instead.

Automatically creating *vpl_execution*
--------------------------------------
VPL is designed so that *vpl_execution.sh* is not meant for running the tests but for executing the compilation phase, which includes preparing *vpl_execution*, which will be used to run the tests. This design makes sense with compiled languages, but with Python the compilation phase is just a nuisance. ``vpltest`` tries to make its usage experience smoother, by taking care of creating *vpl_execution* if necessary. That's why you need to write only 2 lines into *vpl_execution.sh*.

Automatically keeping all execution files available
---------------------------------------------------
After compilation phase, VPL by default deletes all original execution files, unless you tick them under *Advanced settings => Files to keep when running*.

``vpltest`` needs original test files to be present when running, but you don't need remember it, because it uses a trick which makes originals always available. If you don't like this, then run it with ``--allow-deletion``.