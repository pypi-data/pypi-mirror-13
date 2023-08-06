
.. code:: python

    import wowp.components
    import wowp.schedulers

.. code:: python

    from wowp.actors import FuncActor
    import wowp.schedulers

.. code:: python

    import math

.. code:: python

    math.acos(math.cos(math.pi))




.. parsed-literal::

    3.141592653589793



.. code:: python

    import math
    sin = FuncActor(math.sin)
    asin = FuncActor(math.asin)
    pi = math.pi
    

.. code:: python

    asin.inports['inp'] += sin.outports['out']

.. code:: python

    sin.inports['inp'].owner




.. parsed-literal::

    <wowp.actors.FuncActor at 0x535dba8>



.. code:: python

    wf = sin.get_workflow()

.. code:: python

    scheduler = wowp.schedulers.NaiveScheduler()

.. code:: python

    scheduler.run_workflow(wf, inp=1.0)




.. parsed-literal::

    {'out': deque([1.0])}



.. code:: python

    wf.scheduler = wowp.schedulers.NaiveScheduler()

.. code:: python

    wf(inp=math.pi/2)




.. parsed-literal::

    {'out': deque([1.5707963267948966])}



