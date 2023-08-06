
Map-reduce with WOW:-P
======================

.. code:: python

    %load_ext autoreload
    %autoreload 2

.. code:: python

    from wowp.actors import FuncActor
    from wowp.schedulers import LinearizedScheduler

.. code:: python

    # create two FuncActors
    actor1 = FuncActor(lambda x: x * 2)
    actor2a = FuncActor(lambda x: x + 1)
    actor2b = FuncActor(lambda x: x + 2)
    
    # chain the actors
    # FuncActor output port is by default called out
    actor2a.inports['x'] += actor1.outports['out']
    actor2b.inports['x'] += actor1.outports['out']

.. code:: python

    len(actor1.outports)




.. parsed-literal::

    1



Get the resulting workflow.

.. code:: python

    wf = actor1.get_workflow()

Execute the workflow just like an actor.

.. code:: python

    wf(x=3)




.. parsed-literal::

    {'out': deque([8])}



.. code:: python

    from wowp.actors.mapreduce import Map

.. code:: python

    map_act = Map(FuncActor, args=(lambda x: x * 2, ), scheduler=LinearizedScheduler())

.. code:: python

    map_act.inports.inp.put(range(5))




.. parsed-literal::

    True



.. code:: python

    map_act.run()


::


    ---------------------------------------------------------------------------

    UnboundLocalError                         Traceback (most recent call last)

    <ipython-input-19-72525be82702> in <module>()
    ----> 1 map_act.run()
    

    d:\Workspace\wowp\wowp\actors\mapreduce.py in run(self, *args, **kwargs)
         95         else:
         96             map_scheduler = self.map_scheduler
    ---> 97         result = map_scheduler.run_workflow(map_workflow)
         98 
         99         return result
    

    d:\Workspace\wowp\wowp\schedulers.py in run_workflow(self, workflow, **kwargs)
         67                 scheduler.run_actor(inport.owner)
         68         # TODO can this be run inside self.execute itsef?
    ---> 69         scheduler.execute()
         70 
         71         # collect results from output ports
    

    UnboundLocalError: local variable 'scheduler' referenced before assignment


.. code:: python

    %debug


.. parsed-literal::

    > [1;32md:\workspace\wowp\wowp\schedulers.py[0m(69)[0;36mrun_workflow[1;34m()[0m
    [1;32m     68 [1;33m        [1;31m# TODO can this be run inside self.execute itsef?[0m[1;33m[0m[1;33m[0m[0m
    [0m[1;32m---> 69 [1;33m        [0mscheduler[0m[1;33m.[0m[0mexecute[0m[1;33m([0m[1;33m)[0m[1;33m[0m[0m
    [0m[1;32m     70 [1;33m[1;33m[0m[0m
    [0m
    ipdb> up
    > [1;32md:\workspace\wowp\wowp\actors\mapreduce.py[0m(97)[0;36mrun[1;34m()[0m
    [1;32m     96 [1;33m            [0mmap_scheduler[0m [1;33m=[0m [0mself[0m[1;33m.[0m[0mmap_scheduler[0m[1;33m[0m[0m
    [0m[1;32m---> 97 [1;33m        [0mresult[0m [1;33m=[0m [0mmap_scheduler[0m[1;33m.[0m[0mrun_workflow[0m[1;33m([0m[0mmap_workflow[0m[1;33m)[0m[1;33m[0m[0m
    [0m[1;32m     98 [1;33m[1;33m[0m[0m
    [0m
    ipdb> pp map_workflowe
    *** NameError: name 'map_workflowe' is not defined
    ipdb> q
    

::


    ---------------------------------------------------------------------------

    AttributeError                            Traceback (most recent call last)

    <ipython-input-20-2dc6c618a063> in <module>()
    ----> 1 get_ipython().magic('debug')
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\interactiveshell.py in magic(self, arg_s)
       2305         magic_name, _, magic_arg_s = arg_s.partition(' ')
       2306         magic_name = magic_name.lstrip(prefilter.ESC_MAGIC)
    -> 2307         return self.run_line_magic(magic_name, magic_arg_s)
       2308 
       2309     #-------------------------------------------------------------------------
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\interactiveshell.py in run_line_magic(self, magic_name, line)
       2226                 kwargs['local_ns'] = sys._getframe(stack_depth).f_locals
       2227             with self.builtin_trap:
    -> 2228                 result = fn(*args,**kwargs)
       2229             return result
       2230 
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\magics\execution.py in debug(self, line, cell)
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\magic.py in <lambda>(f, *a, **k)
        191     # but it's overkill for just that one bit of state.
        192     def magic_deco(arg):
    --> 193         call = lambda f, *a, **k: f(*a, **k)
        194 
        195         if callable(arg):
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\magics\execution.py in debug(self, line, cell)
        421 
        422         if not (args.breakpoint or args.statement or cell):
    --> 423             self._debug_post_mortem()
        424         else:
        425             code = "\n".join(args.statement)
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\magics\execution.py in _debug_post_mortem(self)
        429 
        430     def _debug_post_mortem(self):
    --> 431         self.shell.debugger(force=True)
        432 
        433     def _debug_exec(self, code, breakpoint):
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\interactiveshell.py in debugger(self, force)
       1020 
       1021         with self.readline_no_record:
    -> 1022             pm()
       1023 
       1024     #-------------------------------------------------------------------------
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\interactiveshell.py in <lambda>()
       1017         else:
       1018             # fallback to our internal debugger
    -> 1019             pm = lambda : self.InteractiveTB.debugger(force=True)
       1020 
       1021         with self.readline_no_record:
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\ultratb.py in debugger(self, force)
       1073                     etb = etb.tb_next
       1074                 self.pdb.botframe = etb.tb_frame
    -> 1075                 self.pdb.interaction(self.tb.tb_frame, self.tb)
       1076 
       1077         if hasattr(self, 'tb'):
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\debugger.py in interaction(self, frame, traceback)
        276         while True:
        277             try:
    --> 278                 OldPdb.interaction(self, frame, traceback)
        279             except KeyboardInterrupt:
        280                 self.shell.write('\n' + self.shell.get_exception_only())
    

    C:\Anaconda3\envs\wowp\lib\pdb.py in interaction(self, frame, traceback)
        344             return
        345         self.print_stack_entry(self.stack[self.curindex])
    --> 346         self._cmdloop()
        347         self.forget()
        348 
    

    C:\Anaconda3\envs\wowp\lib\pdb.py in _cmdloop(self)
        317                 # the current command, so allow them during interactive input
        318                 self.allow_kbdint = True
    --> 319                 self.cmdloop()
        320                 self.allow_kbdint = False
        321                 break
    

    C:\Anaconda3\envs\wowp\lib\cmd.py in cmdloop(self, intro)
        136                             line = line.rstrip('\r\n')
        137                 line = self.precmd(line)
    --> 138                 stop = self.onecmd(line)
        139                 stop = self.postcmd(stop, line)
        140             self.postloop()
    

    C:\Anaconda3\envs\wowp\lib\pdb.py in onecmd(self, line)
        410         """
        411         if not self.commands_defining:
    --> 412             return cmd.Cmd.onecmd(self, line)
        413         else:
        414             return self.handle_command_def(line)
    

    C:\Anaconda3\envs\wowp\lib\cmd.py in onecmd(self, line)
        215             except AttributeError:
        216                 return self.default(line)
    --> 217             return func(arg)
        218 
        219     def emptyline(self):
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\debugger.py in wrapper(*args, **kw)
        176     by Duncan Booth."""
        177     def wrapper(*args, **kw):
    --> 178         return new_fn(*args, **kw)
        179     if old_fn.__doc__:
        180         wrapper.__doc__ = old_fn.__doc__ + additional_text
    

    C:\Anaconda3\envs\wowp\lib\site-packages\IPython\core\debugger.py in new_do_quit(self, arg)
        304 
        305         # Pdb sets readline delimiters, so set them back to our own
    --> 306         self.shell.readline.set_completer_delims(self.shell.readline_delims)
        307 
        308         return OldPdb.do_quit(self, arg)
    

    AttributeError: 'NoneType' object has no attribute 'set_completer_delims'


Creating a custom actor
-----------------------

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
    # and check that the output is as expected
    assert actor(input=value)['output'] == str(value)


.. parsed-literal::

    {'output': '123'}
    
