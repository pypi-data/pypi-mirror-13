
Custom actors
=============

Creating a custom actor class
-----------------------------

.. code:: python

    from wowp import Actor

Every actor must implement ``get_run_args`` and ``run`` methods: \*
``get_run_args`` returns an (args, kwargs) tuple for the later
``run(*args, **kwargs)`` call. This method is responsible for getting
(popping) values from input ports. ``args`` and ``kwargs`` needs to be
serializable for subprocess-based schedulers (e.g. IPython cluster). \*
The ``run`` method gets the input arguments returned by
``get_run_args``. The output must be a dictionary with output port names
as keys. ``run`` must be decorated by ``@staticmethod`` or
``@classmethod`` in order to be serializable---this is necessary for
subprocess-based schedulers (e.g. IPython cluster). \* The result of
``run`` must be a ``dict`` (like) object, whose keys are output port
names. Optional, these methods might be overridden: \* ``can_run``
returns True if the actor is ready to be run (usually when it has
received enough inputs). ``can_run`` is called whenever a new input
arrives (on an input port). By default, ``can_run`` waits for values on
all connected ports.

.. code:: python

    class StrActor(Actor):
    
        def __init__(self, *args, **kwargs):
            super(StrActor, self).__init__(*args, **kwargs)
            # specify input port
            self.inports.append('input')
            # and output ports
            self.outports.append('output')
            
        def get_run_args(self):
            # get input value(s) using .pop()
            args = (self.inports['input'].pop(), )
            kwargs = {}
            return args, kwargs
    
        @staticmethod
        def run(value):
            # return a dictionary with port names as keys
            res = {'output': str(value)}
            return res

Create an instance.

.. code:: python

    actor = StrActor(name='str_actor')

Test the actor by direct call.

.. code:: python

    # we can call the actor directly -- see what's output
    value = 123
    print(actor(input=value))


.. parsed-literal::

    {'output': '123'}
    

.. code:: python

    # and check that the output is as expected
    assert actor(input=value)['output'] == str(value)

Using in a workflow
-------------------

.. code:: python

    from wowp.actors import FuncActor

.. code:: python

    # use randint as input to out StrActor
    import random
    rand = FuncActor(random.randint)

.. code:: python

    actor.inports['input'] += rand.outports['out']

.. code:: python

    # get the workflow
    wf = actor.get_workflow()

.. code:: python

    # and execute
    wf(a=0, b=5)




.. parsed-literal::

    {'output': deque(['5'])}


