# Command guide

Various tasks can be performed through the command line interface of PFD-kit. Here is a guide to the available commands.

## Submitting a Workflow

To submit a workflow, navigate to the working directory and run:

```bash
pfd submit input.json
```

`input.json` contains workflow definitions. The workflow ID will be printed upon successful submission.

## Restarting from a Checkpoint

To restart a workflow with modified input parameters, use:

```bash
pfd resubmit input.json old_workflow_id -u 0-100
```

This reuses the results of the first 100 steps of an old workflow. To list completed steps:

```bash
pfd resubmit input.json old_workflow_id -l
```

## Downloading Results

To download the output model file, use:

```bash
pfd download input.json workflow_id
```

For advanced usage, download a specific step's output:

```bash
pfd download input.json workflow_id -i 0 -d prep-run-train/input/models
```

List available download definitions:

```bash
pfd download input.json workflow_id -l
```

## PFD-kit Command Arguments

> Note: Use `-h` or `--help` to list all possible arguments for PFD-kit subcommands.

### Subcommand: `submit`
Usage:
```bash
pfd submit [-h] [-m] CONFIG
```
Arguments:

- `CONFIG`: Path to the configuration script in `json` format.
- `-m, --monitoring`: Monitor workflow progress and auto-download the output model upon successful completion.

### Subcommand: `resubmit`
Usage:
```bash
pfd resubmit [-h] [-m] CONFIG ID
```
Arguments:

- `CONFIG`: Path to the configuration script in `json` format.
- `ID`: Workflow ID of an existing PFD workflow.
- `-l, --list`: List completed steps of an existing workflow.
- `-u, --reuse REUSE`: Reuse completed steps from an existing workflow.
- `-f, --fold`: Reuse complex steps as a whole.
- `-m, --monitoring`: Monitor workflow progress and auto-download the output model upon successful completion.

### Subcommand: `download`
Usage:
```bash
pfd download [-h] [-l] [-k KEYS] [-i ITERATIONS] [-d STEP_DEFINITIONS] [-p PREFIX] [-n] CONFIG ID
```
Arguments:

- `CONFIG`: Path to the configuration script in `json` format.
- `ID`: Workflow ID of an existing PFD workflow.
- `-k, --keys KEYS`: Download artifacts by step key(s).
- `-d, --step-definitions STEP_DEFINITIONS`: Download artifacts by *step definitions*.
- `-l, --list-supported`: List all supported step definitions.
- `-i, --iterations ITERATIONS`: Specify steps from which iterations are to be downloaded. Used in conjuntion with `-d STEP_DEFINITIONS`.
- `-p, --prefix PREFIX`: Prefix for the download path.
