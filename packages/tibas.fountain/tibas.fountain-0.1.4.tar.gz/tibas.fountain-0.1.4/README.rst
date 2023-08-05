sphinx extension for rendering fountain screenplays
======================================================
:version: 0.1.4

Simple `Sphinx <http://www.sphinx-doc.org/en/stable/>`_ HTML extension for embedding screenplay fragments written in `Fountain <http://fountain.io>`_

This project uses the `fountain python module <https://bitbucket.org/gabriel.montagne/fountain>`_ to parse the markup.

Installation
--------------

Install the package by running::

    python3 setup.py install

Then add the ``tibas.fountain`` package to your ``conf.py`` ``extensions`` module names array. For example::

    extensions = [
        'sphinx.ext.extlinks',
        'sphinx.ext.intersphinx',
        'sphinx.ext.todo',
        'alabaster',
        'sphinxcontrib.blockdiag',
        'ablog',
        'tibas.fountain',
    ]

Usage
-------

The extension provides a ``fountain`` directive::

    .. fountain::

      EXT. MOTORWAY VERGE - NIGHT

      Sometime later, as the crowd disperses and the traffic begins to flow normally, James kneels besides the Lincoln and shows Vaughn the blood on his door.
      Catherine sits in the back seat.

      JAMES
      We must have driven through a pool of blood.
      If the police stops you again, they may impound the car while they have the blood analyzed.

      Vaughan kneels besides him and inspects the smears of blood.

      VAUGHAN
      You're right Ballard. 
      There's an all-night car-wash in the airport service area.

      Vaughan rises and holds the door open for James, who sits behind the wheel, expecting Vaughan to walk around the car and sit beside him.
      Instead, Vaughan pulls open the rear door and and climbs in beside Catherine.

      As they set off, Vaughan's camera lands on the front seat.

      INT. VAUGHAN'S CAR - NIGHT

    Etc.

This will produce HTML with classes you can then style however you prefer,

.. image:: screenshot-cronenberg.png

