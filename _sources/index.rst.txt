.. pfd-kit documentation master file, created by
   sphinx-quickstart on Sat Oct 26 14:00:12 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PFD-kit documentation (|version|)
=====================

.. raw:: html

   <style>
     p {
       text-align: justify;
     }
   </style>


**PFD-kit** is a cloud-based workflow automating the generation of deep-learning based force fields from pre-trained atomic models (**P**) through fine-tuning (**F**) and distillation (**D**) for large scale atomic simulation of practical materials. 
By exploiting the transferable knowledge in the pre-trained model, force field generation using PFD workflow requires much less training data, saving significant time and computational resources. 
This feature makes PFD workflow a powerful tool in computational materials science, addressing challenges in training force fields for complex material systems (*e.g.*, high-entropy alloys, surfaces/interfaces) that are previously intractable. 

This documentation gives an in-depth view of PFD-kit, which includes background introduction, hand-on tutorials and detailed explanation for input parameters.

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
