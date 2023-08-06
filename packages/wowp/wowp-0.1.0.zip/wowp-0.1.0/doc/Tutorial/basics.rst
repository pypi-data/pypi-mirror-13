
Basic wowp usage
================

Turning functions into actors
-----------------------------

1. Define a function
~~~~~~~~~~~~~~~~~~~~

We will define a simple ``times2`` function. Annotations (see `PEP
3107 <https://www.python.org/dev/peps/pep-3107/>`__) will be used for
output port names.

.. code:: python

    def times2(x) -> ('y'):
        '''Multiplies the input by 2
        '''
        return x * 2

2. Turn the function into an *actor*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from wowp.actors import FuncActor
    
    times2_actor = FuncActor(times2)

3. Inspect actor's input and output ports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input / output ports are accessible via ``inports`` and ``outports``
properties.

.. code:: python

    print('input  ports: {}'.format(times2_actor.inports.keys()))
    print('output ports: {}'.format(times2_actor.outports.keys()))


.. parsed-literal::

    input  ports: ['x']
    output ports: ['y']
    

4. FuncActor is callable
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    x = 3
    print('times2({}) = {}'.format(x, times2(x)))
    print('times2_actor({}) = {}'.format(x, times2_actor(x)))
    assert times2(x) == times2_actor(x)


.. parsed-literal::

    times2(3) = 6
    times2_actor(3) = 6
    

From actors to workflows
------------------------

1. Workflows are created by connecting actor ports (input ports to
   output ports).
2. Ports get connected using the **``+=``** operator
   (``inport += outport``).

\*Better workflow creation will be implemented soon.
``Actor.get_workflow`` will create a workflow *automagically*. It will
also be possible to create wokflows *explicitely*, e.g. in cases when
``get_workflow`` cannot be used.\*

Two actors chained together
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's try something like ``x -> actor1 -> actor2 -> out``.

.. code:: python

    # create two FuncActors
    actor1 = FuncActor(lambda x: x * 2)
    actor2 = FuncActor(lambda x: x + 1)
    
    # chain the actors
    # FuncActor output port is by default called out
    actor2.inports['x'] += actor1.outports['out']

Get the resulting workflow.

.. code:: python

    wf = actor1.get_workflow()

Execute the workflow just like an actor.

.. code:: python

    wf(x=3)




.. parsed-literal::

    {'out': deque([7])}


