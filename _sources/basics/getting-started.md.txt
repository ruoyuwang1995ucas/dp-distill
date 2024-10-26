# Quickstart 
This section provides basics steps to take before running PFD-kit
## Installation
PFD-kit can be built and installed form the source.
```shell
git clone https://github.com/ruoyuwang1995nya/pfd-kit.git
cd pfd-kit && pip install .
```

## Submitting jobs
PFD-kit comes with a simple CLI interface. For instance, a finetune workflow can be submitted using following command:
```shell
pfd submit finetune.json -t finetune
```
The `finetune.json` specifies imput parameters of the finetune task, whose details can be found in the `examples` directory. 
It should be noted that PFD-kit is built upon the [dflow](https://github.com/dptech-corp/dflow.git) package and utilized OPs from the [DPGEN2](https://github.com/deepmodeling/dpgen2.git) project, thus it is best to experience PFD-kit on the cloud-based [Bohrium](https://bohrium.dp.tech) platform, though local deployment is also possible.