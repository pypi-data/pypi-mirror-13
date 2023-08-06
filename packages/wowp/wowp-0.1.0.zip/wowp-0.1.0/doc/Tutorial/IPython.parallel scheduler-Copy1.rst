
.. code:: python

    %load_ext autoreload
    %autoreload 2

.. code:: python

    from wowp.actors.numpy import Rand, RandInt
    

.. code:: python

    ra = Rand()
    ri = RandInt()

.. code:: python

    ra(n=2)




.. parsed-literal::

    {'out': array([ 0.26999227,  0.45962118])}



.. code:: python

    ri(low=3)




.. parsed-literal::

    {'out': 2}



.. code:: python

    ra.inports['n'] += ri.outports['out']

.. code:: python

    wf = ra.get_workflow()

.. code:: python

    wf(low=5)




.. parsed-literal::

    {'out': deque([array([ 0.65299637])])}



.. code:: python

    from IPython.parallel import Client

.. code:: python

    cli = Client(profile='default')
    dv = cli[:]
    node = cli[0]

.. code:: python

    import wowp.schedulers

.. code:: python

    wf(scheduler_=wowp.schedulers.LinearizedScheduler(), low=5)




.. parsed-literal::

    {'out': deque([array([ 0.41783864,  0.67931241,  0.88909701,  0.01978796])])}



.. code:: python

    wf(scheduler_=wowp.schedulers.IPyClusterScheduler(), low=5)


.. parsed-literal::

    Run actor <wowp.actors.numpy.RandInt object at 0x0000000005ED1D30>
    Run actor <wowp.actors.numpy.Rand object at 0x0000000005ED1D68>
    



.. parsed-literal::

    {'out': deque([array([ 0.71343407,  0.64201533,  0.93965964])])}



.. code:: python

    wf(scheduler_=wowp.schedulers.ThreadedScheduler(), low=5)


.. parsed-literal::

    Join thread
    Everything finished. Waiting for threads to end.
    0 End
    Join thread
    1 End
    



.. parsed-literal::

    {'out': deque([array([ 0.44900702])])}



