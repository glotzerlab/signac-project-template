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
  2. Data Space operations are implemented within the ``scripts/operations.py`` module.
  3. The project execution logic is implemented within the :py:class:`.project.MyProject` class.
  4. All jobs are classified via ``str``-labels with the :py:meth:`.MyProject.classify` method.
  5. The *next operation* is identified via the :py:meth:`.MyProject.next_operation` method.
  6. Job-operations may be executed directly via the ``scripts/run.py`` script.
  7. Job-operations may be submitted to a scheduler via the :py:mod:`.submit` module.
  8. The project **status** may be examined by executing the :py:mod:`.status` module.

A complete overview of all modules and functions an be found in the :ref:`project_api` chapter.

Step-by-step
------------

This is a description on how to execute the complete workflow of this project.

Initialize the data space using a random number or string, e.g. your username:

.. code-block::  bash

    $ python my_project.init $USER  # (or $ python my_project.init 42)

You can check the status of your project:

.. code-block:: bash

    $ python my_project.status -d
    Query scheduler...
    Determine job stati...
    Generate output...

    Status project 'MyProject':
    Total # of jobs: 5
    label        progress
    -----------  --------------------------------------------------
    initialized  |########################################| 100.00%

    Detailed view:
    job_id                            status    next_operation    labels
    --------------------------------  --------  ----------------  -----------
    8921709098d990fc70b19895653b7f01  unknown   estimate          initialized
    8deb24c26dcb0bf0322cbf45c6b3198f  unknown   estimate          initialized
    b76e21a18c46a90ed52ec3f1e2cd6250  unknown   estimate          initialized
    ed41e3073b4a4133c05bf7ed050ebceb  unknown   estimate          initialized
    fc89c69cb0f09b84f0b7f08c39bde326  unknown   estimate          initialized

Compute the ideal gas estimate, just like in the tutorial:

.. code-block:: bash

    $ python scripts/run.py estimate

Or execute a molecular dynamics simulation using hoomd-blue_ with:

.. _hoomd-blue: https://hoomd-blue.readthedocs.io

.. code-block:: bash

    $ python scripts/run.py equilibrate 8921

.. note::

    When no *job id* is provided as argument, the specified operation is executed for **all** jobs.

Instead of running the operations directly, we can also submit them to a scheduler:

.. code-block:: bash

    $ python my_project.submit -j equilibrate

In this case we explicitly specified which operation to submit.
If we omit the argument, the *next operation* for each job will be submitted.

.. note::

    The scheduler is determined from the environment with the :py:mod:`.environment` module.
    If your environment does not have a scheduler or it is not configured, signac-flow will default to a *fake scheduler*, which prints the job scripts to screen.
