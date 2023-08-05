=============
SinicValidate
=============

Asterisk Sinic Name & Phone & IDCard & etc

Installation
============

::

    pip install SinicAsterisk


Usage
=====

::

    Python 2.7.5 (default, Mar  9 2014, 22:15:05)
    Type "copyright", "credits" or "license" for more information.

    IPython 4.0.0 -- An enhanced Interactive Python.
    ?         -> Introduction and overview of IPython's features.
    %quickref -> Quick reference.
    help      -> Python's own help system.
    object?   -> Details about 'object', use 'object??' for extra details.

    In [1]: import SinicAsterisk as risk

    In [2]: risk.phone('18888888888')
    Out[2]: '188****8888'

    In [3]: risk.identity_card('320321198811118888')
    Out[3]: '3203211988****8888'

    In [4]:


Method
======

::

    def phone(self, message):

    def identity_card(self, message):

