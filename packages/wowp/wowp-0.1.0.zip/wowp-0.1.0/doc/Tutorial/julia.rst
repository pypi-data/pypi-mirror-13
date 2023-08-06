
Julia methods as actors
=======================

Installing necessary requirements
---------------------------------

1) Install Julia itself. Start from here:
   http://julialang.org/downloads/

2) Install ``PyCall`` which is a Python binding library for Julia (i.e.
   calling Python from Julia).

.. code:: julia

    julia> Pkg.update()
    julia> Pkg.add("PyCall")

3) Install ``pyjulia`` Python package:

3a) Download it from github.com:

.. code:: bash

    git clone git@github.com:JuliaLang/pyjulia.git

3b) Install the package:

.. code:: bash

    cd pyjulia
    pip install .              # Copy to site-packages
    # pip install -e .         # Makes link to current directory in site-packages

4) Try in Python:

.. code:: python

    import julia
    jl = julia.Julia()        # Takes a few seconds
    jl.eval("2 + 2")          # Should immediately return "4"

.. code:: python

    %load_ext autoreload
    %autoreload(2)

.. code:: python

    from wowp.actors.julia import JuliaMethod
    from wowp.schedulers import LinearizedScheduler
    import numpy as np

Simple calling
--------------

.. code:: python

    sqrt = JuliaMethod("sqrt", inports="a")
    sqrt(4)




.. parsed-literal::

    2.0



Calling on numpy arrays
-----------------------

.. code:: python

    sqrt = JuliaMethod("sqrt", inports="a")
    
    array = np.random.rand(5, 5)
    scheduler = LinearizedScheduler()
    scheduler.put_value(sqrt.inports.a, array)
    scheduler.execute()
    sqrt.outports.result.pop()




.. parsed-literal::

    array([[ 0.91379381,  0.76452054,  0.62925355,  0.62860044,  0.42112238],
           [ 0.57866373,  0.47615751,  0.96195498,  0.41679105,  0.91152029],
           [ 0.48007553,  0.94239266,  0.98561812,  0.72003329,  0.79679892],
           [ 0.67424912,  0.68200927,  0.89729095,  0.61858826,  0.56059416],
           [ 0.18894945,  0.53575159,  0.5243968 ,  0.67798176,  0.90987452]])



Chain sqrt method to pass numpy arrays
--------------------------------------

.. code:: python

    sqrt = JuliaMethod("sqrt", inports="a")
    sqrt2 = JuliaMethod("sqrt", inports="a")
    
    sqrt.outports.result.connect(sqrt2.inports.a)
    
    array = np.random.rand(5, 5)
    scheduler = LinearizedScheduler()
    scheduler.put_value(sqrt.inports.a, array)
    scheduler.execute()
    sqrt2.outports.result.pop()




.. parsed-literal::

    array([[ 0.49515004,  0.7059926 ,  0.75179199,  0.89298972,  0.68658485],
           [ 0.54016483,  0.70598213,  0.72611978,  0.81153936,  0.65909235],
           [ 0.86581432,  0.95754091,  0.99006334,  0.94470668,  0.66350372],
           [ 0.89233693,  0.95196157,  0.98033928,  0.59451821,  0.74976972],
           [ 0.4110181 ,  0.73543385,  0.93298482,  0.96431895,  0.83253339]])



Using method from a package
---------------------------

.. code:: python

    %%file ABCD.jl
    
    module ABCD
    
    VERSION < v"0.4-" && using Docile
    
    export quad
    
    @doc doc"""Fourth power of the argument.""" ->
    function quad(a)
        a ^ 4
    end
    
    end


.. parsed-literal::

    Overwriting ABCD.jl
    

.. code:: python

    quad = JuliaMethod(package_name="ABCD", method_name="quad", inports="a")
    quad(4.0)




.. parsed-literal::

    256.0



.. code:: python

    quad.name




.. parsed-literal::

    'ABCD.quad'



Non-existent module or package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    xxx = JuliaMethod(package_name="ABBD", method_name="x")
    xxx()


::


    ---------------------------------------------------------------------------

    JuliaError                                Traceback (most recent call last)

    <ipython-input-9-4f98542fcbe1> in <module>()
          1 xxx = JuliaMethod(package_name="ABBD", method_name="x")
    ----> 2 xxx()
    

    /home/honza/code/wowp/wowp/actors/julia.py in __call__(self, *args, **kwargs)
         47     def __call__(self, *args, **kwargs):
         48         self._julia = Julia()
    ---> 49         return self._julia_method(*args)
    

    /home/honza/code/wowp/wowp/actors/julia.py in _julia_method(self)
         23     def _julia_method(self):
         24         if self.package_name:
    ---> 25             self._julia.eval("using %s" % self.package_name)
         26         return self._julia.eval(self._full_method_name)
         27 
    

    /home/honza/anaconda/envs/py34/lib/python3.4/site-packages/julia/core.py in eval(self, src)
        354         if src is None:
        355             return None
    --> 356         ans = self.call(src)
        357         res = self.api.jl_call1(void_p(self.api.PyObject), void_p(ans))
        358         if not res:
    

    /home/honza/anaconda/envs/py34/lib/python3.4/site-packages/julia/core.py in call(self, src)
        327                 exception_msg = "<couldn't get stack>"
        328             raise JuliaError(u'Exception \'{}\' ocurred while calling julia code:\n{}\n\nCode:\n{}'
    --> 329                              .format(exception_type, exception_msg, src))
        330         return ans
        331 
    

    JuliaError: Exception 'ErrorException' ocurred while calling julia code:
    <couldn't get stack>
    
    Code:
    using ABBD


.. code:: python

    xxx = JuliaMethod(package_name="ABCD", method_name="xx")
    xxx()


::


    ---------------------------------------------------------------------------

    JuliaError                                Traceback (most recent call last)

    <ipython-input-10-069d69df7745> in <module>()
          1 xxx = JuliaMethod(package_name="ABCD", method_name="xx")
    ----> 2 xxx()
    

    /home/honza/code/wowp/wowp/actors/julia.py in __call__(self, *args, **kwargs)
         47     def __call__(self, *args, **kwargs):
         48         self._julia = Julia()
    ---> 49         return self._julia_method(*args)
    

    /home/honza/code/wowp/wowp/actors/julia.py in _julia_method(self)
         24         if self.package_name:
         25             self._julia.eval("using %s" % self.package_name)
    ---> 26         return self._julia.eval(self._full_method_name)
         27 
         28     @property
    

    /home/honza/anaconda/envs/py34/lib/python3.4/site-packages/julia/core.py in eval(self, src)
        354         if src is None:
        355             return None
    --> 356         ans = self.call(src)
        357         res = self.api.jl_call1(void_p(self.api.PyObject), void_p(ans))
        358         if not res:
    

    /home/honza/anaconda/envs/py34/lib/python3.4/site-packages/julia/core.py in call(self, src)
        327                 exception_msg = "<couldn't get stack>"
        328             raise JuliaError(u'Exception \'{}\' ocurred while calling julia code:\n{}\n\nCode:\n{}'
    --> 329                              .format(exception_type, exception_msg, src))
        330         return ans
        331 
    

    JuliaError: Exception 'UndefVarError' ocurred while calling julia code:
    <couldn't get stack>
    
    Code:
    ABCD.xx


Unicode identifiers
~~~~~~~~~~~~~~~~~~~

The page of julia states that unicode identifiers are not valid. This is
true for automatically imported methods. But not for ``JuliaMethod``.
Names like ``πtimes!`` are fine :-)

.. code:: python

    %%file UnicodePi.jl
    
    module UnicodePi
    
    VERSION < v"0.4-" && using Docile
    
    export πtimes!
    
    @doc doc"""Return pi times argument""" ->
    function πtimes!(a)
        π * a
    end
    
    end


.. parsed-literal::

    Overwriting UnicodePi.jl
    

.. code:: python

    pi_times = JuliaMethod(package_name="UnicodePi", method_name="πtimes!", inports="x")
    print(pi_times.name)
    pi_times(4)


.. parsed-literal::

    UnicodePi.πtimes!
    



.. parsed-literal::

    12.566370614359172



.. code:: python

    from wowp.tools.plotting import ipy_show
    ipy_show(pi_times)




.. image:: julia_files%5Cjulia_21_0.png



