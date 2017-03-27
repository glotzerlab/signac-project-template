.. _quickstart:

Quickstart
==========

This project is based on the basic workflow implemented in the signac tutorial_.
Being familiar with the tutorial_ will help in understanding the logic of this template.

.. _tutorial: https://signac.readthedocs.io/en/latest/tutorial.html

The project requires the signac-flow_ package, which implements the core logic of the example workflow within a :py:class:`flow.FlowProject` class.
In addition it adds functionality to work with schedulers in a cluster environment.

.. _signac-flow: https://signac-flow.readthedocs.io

The Basics
----------

This is a list of key things you need to know in order to efficiently work with this project:

  1. All modules are part of the :py:mod:`my_project` package located in the directory of the same name.
  2. The project execution logic is implemented within the :py:class:`.project.MyProject` class.
  3. All jobs are classified via ``str``-labels with the :py:meth:`.MyProject.classify` method.
  4. The *next operation* is identified via the :py:meth:`.MyProject.next_operation` method.
  5. The project **status** may be examined by executing the :py:mod:`.status` module.
  6. Job-operations may be submitted to a scheduler via the :py:mod:`.submit` module.
  7. Python-based operations are implemented within the ``scripts/operations.py`` module.
  8. Operations defined in the ``scripts/operations.py`` module can be executed directly via the
     ``scripts/run.py`` script.

A complete overview of all modules and functions an be found in the :ref:`project_api` chapter.

Step-by-step
------------

This is a description on how to execute the complete workflow of this project.

Initialize the data space using a random number or string, e.g. your username:

.. code-block::  bash

    $ python -m my_project.init $USER  # (or $ python my_project.init 42)

You can check the status of your project:

.. code-block:: bash

    $ python -m my_project.status -d
    Query scheduler...
    Determine job stati...
    Generate output...

    Status project 'MyProject':
    Total # of jobs: 10
    label    progress
    -------  ----------

    Detailed view:
    job_id                            S    next_op     labels
    --------------------------------  ---  ----------  --------
    6c57f630f0b62d449349ee2322cc16b6  U !  initialize
    e0cf9aa968b48b22c66bbfda41d46129  U !  initialize
    1677c153f81290d2e6e8b97a4f1d4297  U !  initialize
    a230567b8a54d5c44d88b806b390b426  U !  initialize
    3904431a51a3d3e4a31358f24b69d43f  U !  initialize
    ...

    Abbreviations used:
    !: requires_attention
    S: status
    U: unknown

We initialize the jobs for hoomd-blue_:

.. _hoomd-blue: https://hoomd-blue.readthedocs.io

.. code-block:: bash

    $ python scripts/run.py initialize

Notice that the next_op and labels have changed if you check the status again:

.. code-block:: bash

    $ python -m my_project.status -d
    Query scheduler...
    Determine job stati...
    Generate output...

    Status project 'MyProject':
    Total # of jobs: 10
    label        progress
    -----------  --------------------------------------------------
    initialized  |########################################| 100.00%

    Detailed view:
    job_id                            S    next_op    labels
    --------------------------------  ---  ---------  -----------
    6c57f630f0b62d449349ee2322cc16b6  U !  estimate   initialized
    e0cf9aa968b48b22c66bbfda41d46129  U !  estimate   initialized
    1677c153f81290d2e6e8b97a4f1d4297  U !  estimate   initialized
    a230567b8a54d5c44d88b806b390b426  U !  estimate   initialized
    3904431a51a3d3e4a31358f24b69d43f  U !  estimate   initialized
    ...

    Abbreviations used:
    !: requires_attention
    S: status
    U: unknown

Compute the ideal gas estimate, just like in the tutorial:

.. code-block:: bash

    $ python scripts/run.py estimate

Execute a molecular dynamics simulation using hoomd-blue_ with:

.. code-block:: bash

    $ python scripts/run.py sample 6c57

where *6c57* is the first few characters of the *job id*.

.. note::

    When no *job id* is provided as argument, the specified operation is executed for **all** jobs.

Instead of running the operations directly, we can also submit them to a scheduler:

.. code-block:: bash

    $ python -m my_project.submit -j sample

In this case we explicitly specified which operation to submit.
If we omit the argument, the *next operation* for each job will be submitted.

.. tip::

    Use the ``--pretend`` argument to print the submission script to the screen instead
    of submitting it during debugging.

The scheduler is determined from the environment with the :py:mod:`.environment` module.
If your environment does not have a scheduler or it is not configured, signac-flow will raise an exception.
However, you can use a test environment with ``--test`` argument, which will mock an
actual submission process.
