.. pfd-kit documentation master file, created by
   sphinx-quickstart on Sat Oct 26 14:00:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pfd-kit documentation
=====================

PFD-kit version |version| documentation
----------------------------------------

.. raw:: html

   <div style="text-align: justify;">
   PFD-kit is a cloud-based workflow written in Python, delicately designed to generate a deep learning based model of interatomic potential energy and force field. PFD-kit is based on pre-trained (P) Large Atomic Models through fine-tune (F) and distillation (D). Compared to concurrent learning method, e.g. DP-GEN, the PFD-kit requires less computational resources and time, eliminates the need for supervision by materials science experts while producing models with stronger generalization capabilities. This makes it highly effective for supporting high-throughput calculations and addressing challenges in training models for complex material systems, such as high-entropy alloys and surfaces/interfaces.

   The main features of PFD-kit include automated data generation, model training, evaluation and maintain job queues on HPC machines (High Performance Cluster), making it a powerful tool for researchers in the field of computational materials science.
   </div>

.. toctree::
   :maxdepth: 2
   :caption: The Basics

   basics/overview
   basics/getting-started

.. toctree::
   :maxdepth: 2
   :caption: User guide

   usage/guide-on-cli
   usage/guide-on-script
   usage/argument-for-script
   usage/examples

.. toctree::
   :maxdepth: 2
   :caption: Developer guide

   development/modules
