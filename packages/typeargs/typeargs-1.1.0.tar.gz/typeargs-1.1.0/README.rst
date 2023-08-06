typeargs
=========
*Smarter positional argument handling*

Installation
------------
Install via pip:

.. code-block:: bash

    $ pip install typeargs

Done.

If you insist on the (slightly) harder way of installing, from source,
you know how to do it already and don't need my help.

I might later upload the source to:
https://github.com/TaylorSMarks/typeargs

Documentation
-------------
When you call an ordinary Python function, it blindly passes in your positional arguments, and then it passes in your keyword arguments.

Suppose you had a function with a signature like this, as is the case for many things in Tkinter:

.. code-block:: python

    def makeWidget(master = None, contents = '', x = 0, y = 0, xSpan = 1, ySpan = 1):

You want to call this function now, without specifying a master. Here are your options normally:

.. code-block:: python

    makeWidget(None, 'This is impossible to read.', 5, 7, 2, 2)

Quick! Without looking at the signature, what the heck are those numbers at the end? Normally you solve it with this:

.. code-block:: python

    makeWidget(s = 'Better, but so much typing...', x = 5, y = 7, xSpan = 2, ySpan = 2)

Now that you include all the names, it's easier to tell what each argument is, but its so verbose... it's kind of heavy.

This is where typeargs comes in. If you go back to the original function and decorate it with typeargs as such:

.. code-block:: python

    @typeargs     (Master,        str,    int,   int,   int,       int)
    def makeWidget(master = None, s = '', x = 0, y = 0, xSpan = 1, ySpan = 1):

Now a caller can just type this:

.. code-block:: python

    makeWidget('Hello World!', 2, 2, x = 5, y = 7)

Okay now, what's what? Obviously our string is Hello World!, x is 5, y is 7, and we have two more arguments of ints. Those must be xSpan and ySpan, and no master was included, so it'll use the default None.

By intelligently handling positional arguments based on their types, you can skip over arguments you want default values for, without using key-word arguments for every name.

Another example - lets say that you want to pass in master at the end:

.. code-block:: python

    makeWidget('Hello World!', 2, 2, x = 5, y = 7, master = Master('Window'))
    makeWidget('Hello World!', 2, 2, Master('Window'), x = 5, y = 7)

Either one will work - we're just making argument delivery just a bit smarter than normal.

One more example, new in 1.1.0, you can now match string arguments using regular expressions, if you want. No need to define the re objects in advance - they can be right in the decorator call if you want.

.. code-block:: python

    from typeargs import re, typeargs

    phoneNumber = re(r'\d{3}-\d{4}')
    ssn         = re(r'\d{3}-\d{2}-\d{4}')
    fullName    = re(r'\w+ \w+')

    @typeargs(fullName, ssn, phoneNumber)
    def infos(fullName, ssn, phoneNumber):
        print(fullName, ssn, phoneNumber)

    infos('752-2723', 'Taylor Marks', '123-45-6789')
    # Prints out ('Taylor Marks', '123-45-6789', '752-2723')

Copyright
---------
This software is Copyright (c) 2016 Taylor Marks <taylor@marksfam.com>.

See the bundled LICENSE file for more information.
