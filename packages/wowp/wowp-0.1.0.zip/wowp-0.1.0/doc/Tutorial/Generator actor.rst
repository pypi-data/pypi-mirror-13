
Generator-like actors
=====================

.. code:: python

    %load_ext autoreload
    %autoreload 2

.. code:: python

    from wowp.actors.experimental import LineReader
    from wowp.schedulers import LinearizedScheduler

.. code:: python

    %%file shakespeare.txt
    Shall I compare thee to a summer’s day?
    Thou art more lovely and more temperate:
    Rough winds do shake the darling buds of May,
    And summer’s lease hath all too short a date:
    Sometime too hot the eye of heaven shines,
    And often is his gold complexion dimm’d;
    And every fair from fair sometime declines,
    By chance or nature’s changing course untrimm’d;
    But thy eternal summer shall not fade
    Nor lose possession of that fair thou owest;
    Nor shall Death brag thou wander’st in his shade,
    When in eternal lines to time thou growest:
    So long as men can breathe or eyes can see,
    So long lives this and this gives life to thee.


.. parsed-literal::

    Overwriting shakespeare.txt
    

.. code:: python

    reader = LineReader()
    scheduler = LinearizedScheduler()

.. code:: python

    scheduler.put_value(reader.inports.path, "shakespeare.txt")
    scheduler.execute()

.. code:: python

    port = reader.outports["line"]
    i = 1
    while not port.isempty():
        print("Output #%d: %s" % (i, port.pop()))
        i += 1


.. parsed-literal::

    Output #1: Shall I compare thee to a summer’s day?
    Output #2: Thou art more lovely and more temperate:
    Output #3: Rough winds do shake the darling buds of May,
    Output #4: And summer’s lease hath all too short a date:
    Output #5: Sometime too hot the eye of heaven shines,
    Output #6: And often is his gold complexion dimm’d;
    Output #7: And every fair from fair sometime declines,
    Output #8: By chance or nature’s changing course untrimm’d;
    Output #9: But thy eternal summer shall not fade
    Output #10: Nor lose possession of that fair thou owest;
    Output #11: Nor shall Death brag thou wander’st in his shade,
    Output #12: When in eternal lines to time thou growest:
    Output #13: So long as men can breathe or eyes can see,
    Output #14: So long lives this and this gives life to thee.
    
