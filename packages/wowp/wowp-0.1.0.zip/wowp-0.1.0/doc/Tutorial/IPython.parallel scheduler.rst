
IPython parallel scheduler
==========================

IPython cluster consists of one or more engines running as *individual
processes* on local or remote computers. This brings a number of
advantages, such as scalability or safety. However, only *picklable*
(serializable) actors can be used. For exaple, lamda functions are not
picklable and thus FuncActor with lamba (or interactively defined)
function cannot be used.

**Important**: You must start ipython cluster first. Either use the
Clusters tab in the main Jupyter screen or follow the
`documentation <http://ipython.org/ipython-doc/stable/parallel/parallel_process.html>`__.

A trivial workflow with numpy actors
------------------------------------

.. code:: python

    from numpy.random import random_sample
    from numpy import dot
    from numpy.linalg import norm, det

.. code:: python

    from wowp.actors import FuncActor

.. code:: python

    dims = 4, 4
    A = random_sample(dims)
    B = random_sample(dims)

.. code:: python

    dot_actor = FuncActor(dot, inports=('a', 'b'))
    det_actor = FuncActor(det)

.. code:: python

    det_actor.inports['a'] += dot_actor.outports['out']
    wf = det_actor.get_workflow()

Try to run with default scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    wf_res = wf(a=A, b=B)
    assert wf_res['out'][0] == det(dot(A, B))

Now with the IPython Cluster scheduler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from wowp.schedulers import IPyClusterScheduler
    ipyscheduler = IPyClusterScheduler()

.. code:: python

    wf_res = wf(scheduler=ipyscheduler, a=A, b=B)
    assert wf_res['out'][0] == det(dot(A, B))
