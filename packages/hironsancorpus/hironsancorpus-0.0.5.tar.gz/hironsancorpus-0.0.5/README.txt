Hironsan corpus
===============

Japanese IOB2 tagged corpus for named entity recognition.

Quick Start
-----------

.. code:: shell

    pip install hironsancorpus

Usage
-----

.. code:: python

    from hironsan.corpus import hiron2016
    train_sents = hiron2016.iob_sents('train')
    test_sents = hiron2016.iob_sents('test')
