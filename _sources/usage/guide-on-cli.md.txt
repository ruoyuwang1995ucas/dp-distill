# Command guide

Various tasks can be performed through the command line interface of PFD-kit. Here is a thorough introduction to the availiable commands.

## Submitting workflow

To submit a workflow, navigate to the working directory and run the `submit` command:

```bash
pfd submit input.json
```

`input.json` is the input file which contains workflow definitions, and the corresponding workflow (either fine-tune or distillation) would be submitted based on the input file. Upon successful submission, the workflow id would be printed out to the console.

## Restarting from checkpoint

Occasionally it might be neccessary to restart from, for example, a failed workflow with modified input parameters, then the `resubmit` command comes in handy.  

```bash
pfd resubmit input.json old_workflow_id -u 0-100
```

This command submits a new workflow, but it reuses the results of the first 100 steps of an old workflow without repeating the same calculation. By adding the `-l` argument, completed steps of `old_workflow_id` can be shown with an index number for each step.

```bash
$ pfd resubmit input.json old_workflow_id -l
                   0 : init--pert-gen
                   1 : init--prep-fp
             2 -> 31 : init--run-fp-000000 -> init--run-fp-000029
                  32 : init--sample-aimd
                  ...
```

## Downloading results

To download the output model file, use the `download` command:

```bash
pfd download input.json workflow_id
```

This would download the model file if the workflow has successfully completed. For more advanced usage, output of a specific step can be downloaded using the `-k <step_key>` argument. Another advanced download option is to "download by definition". For example, the following command downloads the models of the `prep-run-train` step of the `iter-000` iteration:

```bash
pfd download input.json workflow_id -i 0 -d prep-run-train/input/models
```

The `-d prep-run-train/input/models` argument is exactly the "download definition". The `-l` argument would list the available download definition:

```bash
pfd download input.json workflow_id -l
```

## Details of PFD-kit command

Users can using the `-h` or `--help` options for each command to check the detailed information of PFD-kit command.
