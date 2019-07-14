.. LightEx documentation master file, created by
   sphinx-quickstart on Tue Jul  9 17:48:18 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to LightEx's documentation!
===================================


.. toctree::
   :maxdepth: 2
   :caption: Contents

   anatomy
   config
   readme


Experiments
-----------

Experiments are at core of the data science workflow. 

    * tweaking data pipelines, observing results
    * changing hyper-parameters -> observing metrics -> selecting models.
    * comparing and visualizing the metrics across multiple experiments.
    * moving between terminal-based, jupyter-based, process-based, docker-based workflows.

LightEx
-------

LightEx is a lightweight framework to create, monitor and record your machine learning experiments. Targeted towards individual data scientists, researchers, small teams and, in general, resource-constrained experimentation. 

* Features:
    * configure your experiments with ease using dataclass based namedconfigs.
    * switch easily between process-based, docker-based, kubernetes-based experiment dispatch
    * log to multiple logger backends using an unified interface
    * enable disciplined yet flexible experimentation.



* Quick Start
    * `pip install lightex`
    * Initialize one or more backend `loggers <https://github.com/ofnote/lightex/backend>`_
    * new project: `lx init` 
        * creates `config.py` and `run_expts.py` in the project directory.
    * Update `config.py` with project- and experiment-specific values.

* Examples
    * sklearn: train model with a hyper-parameter (HP) *group*.
    * mnist-pytorch: train model with unified logging (to mlflow, tensorboard), separate data and working directories.
    * efficient-net-pytorch. retrain starting with multiple pre-trained models (in a HP group). 








Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
