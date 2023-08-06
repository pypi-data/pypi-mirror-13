
Creating a Matlab actor
=======================

``MatlabMethod`` is similar to ``FuncActor``.

.. code:: python

    from wowp.actors.matlab import MatlabMethod

.. code:: python

    ceil = MatlabMethod('ceil', inports='x')

``MatlabMethod`` is directly callable.

.. code:: python

    print(ceil(3.1))


.. parsed-literal::

    4.0
    

Let's try a simple workflow.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from wowp.actors import FuncActor

.. code:: python

    # create a simple +1 actor
    def add_one(x) -> ('y'):
        return x+1
    
    add_one_actor = FuncActor(add_one)

.. code:: python

    # connect actors
    ceil.inports['x'] += add_one_actor.outports['y']
    # get the workflow object
    wf = ceil.get_workflow()

.. code:: python

    # run the workflow
    wf(x=2.1)




.. parsed-literal::

    {'result': deque([4.0])}


