======
hironsan corpus
======

Japanese IOB2 tagged corpus for named entity recognition.

Quick Start
------

::

    pip install hironcorpus


Usage
------

::

    from corpus import hiron2016
    train_sents = hiron2016.iob_sents('train')
    test_sents = hiron2016.iob_sents('test')

