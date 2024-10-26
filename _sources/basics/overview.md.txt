# Overview

[PFD-kit](https://github.com/ruoyuwang1995nya/dp-distill) automates the fine-tuning and distillation process of pre-trained atomic models, such as [DPA-2](https://github.com/deepmodeling/deepmd-kit.git). It enables practical atomistic simualtion with the highly transferable, but computationally expensive pre-trained models. PFD-kit is built upon the  [DPGEN2](https://github.com/deepmodeling/dpgen2) workflow and supports the Deep Potential models. The best experience of PFD-kit is found on Bohrium platform.

## Workflows 
### Fine-tune
Fig.1 shows the schematic of fine-tuning workflow. Given the initial structures of fine-tuning systems, the workflow generates perturbed structures, and executes a series of short *ab initio* molecular dynamics (AIMD) simulation based upon randomly perturbed structures. The pre-trained model is firstly fine-tuned by the AIMD dataset, then MD simulation with the fine-tuned model searches new configurations, which are then labeled by first-principle calculation softwares. If the fine-tuned model cannot predict the labeled dataset with sufficient accuracy, the collected dataset would be added to the fine-tuning training set, and the *train-search-label* process would iterate until convergence. 
<div>
    <img src="../_static/fine-tune.png" alt="Fig1" style="zoom: 35%;">
    <p style='font-size:1.0rem; font-weight:none'>Figure 1. Fine-tune workflow.</p>
</div>

### Distillation
A lightweight model can be generated from a fine-tuned model through distillation, which enables much faster simulation. The distilled model can be generated with training data labeled by the fine-tuned model. Figure 2 shows the schematic of the distillation workflow.
 <div>
    <img src="../_static/distillation.png" alt="Fig2" style="zoom: 25%;">
    <p style='font-size:1.0rem; font-weight:none'>Figure 2. Distillation workflow.</p>
</div>
