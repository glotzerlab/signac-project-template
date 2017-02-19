=========
Reference
=========

Introduction
============

A signac_ project manages a data space which is divided into segments, where each segment is strongly associated with a unique set of parameters: a *state point*.
The signac-flow_ extension provides means to implement a workflow via the :py:class:`flow.FlowProject` which inherits from :py:class:`signac.Project`.
This workflow is based on two core concepts: job *classification* and data space *operations*.

.. _signac: https://glotzerlab.engin.umich.edu/signac
.. _signac-flow: https://signac-flow.readthedocs.io

Classfication
=============

We classify the state of a ``Job`` using text *labels*.
These labels can be determined by a simple generator function, e.g.:

.. code-block:: python

   def classify(job):
      if job.isfile('init.txt'):
          yield 'initialized'

Operations
==========

A *data space operation* is any action that will modify the data space.

This is an example for an operation implemented in python:

.. code-block:: python

    def initialize(job):
        with job:
            with open('init.txt', 'w') as file:
                file.write('Hello world!')

The *initialize* operation will create a file called ``init.txt`` within a ``job``'s workspace.


The default workflow
====================

Combining the concepts of *classification* and *operations* we can define the workflow logic of a :py:class:`flow.FlowProject` by implementing the :py:meth:`~flow.FlowProject.classify` and the :py:meth:`~flow.FlowProject.next_operation` method:

.. code-block:: python

   from flow import FlowProject
   from flow import JobOperation

   class MyProject(FlowProject):

       def classify(self, job):
          if job.isfile('init.txt'):
              yield 'initialized'
          if job.isfile('dump.txt'):
              yield 'processed'

       def next_operation(self, job):
          labels = set(self.classify(job))

          def op(name):
              return JobOperation(name, job, 'python scripts/run.py {} {}'.format(name, job))

          if 'initialized' not in labels:
              return op('initialize')
          if 'processed' not in labels:
              return op('process')

The :py:meth:`~flow.FlowProject.next_operation` returns the **default operation** to execute **next** for a job in the identified state.
This operation is a command, which can be executed on the command line.
In the template, all operations are defined in the ``scripts/operations.py`` module and are executed by the ``scripts/run.py`` script.

We can get a quick overview of our project's status via the :py:meth:`~flow.FlowProject.print_status()` method:

.. code-block:: python

    >>> project = MyProject()
    >>> project.print_status(detailed=True, params=('a',))
    Status project 'MyProject':
    Total # of jobs: 10
    label        progress
    -----------  -------------------------------------------------
    initialized  |########--------------------------------| 20.00%
    processed    |####------------------------------------| 10.00%

    Detailed view:
    job_id                            S    next_op       a  labels
    --------------------------------  ---  ----------  ---  ----------------------
    108ef78ec381244447a108f931fe80db  U !  sample      1 1  processed, initialized
    be01a9fd6b3044cf12c4a83ee9612f84  U !  process     3 2  initialized
    32764c28ef130baefebeba76a158ac4e  U !  initialize  2.3
    # ...

.. tip::

    You can print the project's status from the command line by executing ``$ python -m my_project.status``.

Running operations
==================

All python-based *operations* are implemented in the ``scripts/operations.py`` module.
We can use the ``scripts/run.py`` script to execute them directly, e.g.:

.. code-block:: bash

    $ python scripts/run.py initialize 108e

This command will execute the *initialize* operation for the job identified by the `108e...` id.

Scheduling
==========

To take full advantage of the workflow management, it is advantagous to use a :py:class:`~flow.manage.Scheduler` which schedules the execution of *job-operations* for us.
The **project template** attempts to detect available schedulers through the :py:mod:`.environment` module, but might require some tweaking based off your particular computing environment.

To submit job-operations to a scheduler, call the :py:meth:`~flow.FlowProject.submit` method.

.. tip::

    You can submit *job operations* to a scheduler from the command line, by executing ``$ python my_project.submit``.

The :py:meth:`~flow.FlowProject.submit` method will schedule the execution of operations for specified jobs by generating and submitting a *jobscript* to the scheduler.

Every *job submission script* has the same basic structure:

  1. environment dependent header (e.g. scheduler options)
  2. operation-agnostic header (e.g. switching into the project root directory)
  3. commands to execute operations

The *scheduler header* will vary across different scheduler implementations and should be configured via the :py:mod:`.environment` module.

In summary, if we only execute *operations* defined in the :py:mod:`.operations` module, we can run them either directly or submit them to a scheduler:

  .. code-block:: bash

        python scripts/run.py OPERATION [JOBID] ...
        python -m my_project.submit [-j OPERATION] [JOBID] ...
