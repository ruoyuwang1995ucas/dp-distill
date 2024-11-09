.. _submitargs:

Arguments of the input script
==============================


Host and nodes
--------------

.. dargs:: 
    :module: pfd.entrypoint.args
    :func: wf_args

Task definition
--------------

.. dargs:: 
    :module: pfd.entrypoint.args
    :func: task_args

Structure generation
--------------------

.. dargs:: 
    :module: pfd.entrypoint.args
    :func: conf_generation_args

Model training
--------------

.. dargs:: 
    :module: pfd.entrypoint.args
    :func: training_args

Inference & labeling
-------------------

.. dargs:: 
    :module: pfd.entrypoint.args
    :func: label_args

Exploration
-----------
.. dargs:: 
    :module: pfd.entrypoint.args
    :func: explore_args


Explore task group definition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LAMMPS task group
****************
.. dargs:: 
    :module: pfd.exploration.task
    :func: lmp_task_group_args