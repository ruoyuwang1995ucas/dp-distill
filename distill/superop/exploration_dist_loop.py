import os
from copy import (
    deepcopy,
)
from pathlib import (
    Path,
)
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Type,
    Union,
)

from dflow import (
    InputArtifact,
    InputParameter,
    Inputs,
    OPTemplate,
    OutputArtifact,
    OutputParameter,
    Outputs,
    Step,
    Steps,
)
from dflow.python import (
    OP,
    PythonOPTemplate,
)

from dpgen2.utils.step_config import (
    init_executor
)
from distill.op import (
    ModelTestOP,
    EvalConv,
    IterCounter,
    StageScheduler,
    NextLoop
)

class ExplorationBlock(Steps):
    def __init__(
        self,
        name: str,
        expl_tasks_op:Type[OP],
        prep_run_explore_op: OPTemplate,
        collect_data_op: Type[OP],
        gen_lmp_step_config:dict,
        collect_data_step_config:dict,
        upload_python_packages: Optional[List[os.PathLike]] = None,
    ):
        self._input_parameters = {
            "block_id": InputParameter(),
            "expl_tasks":InputParameter(), 
            "explore_config": InputParameter(),
            "type_map":InputParameter(),
            "mass_map":InputParameter(),
        }
        self._input_artifacts = {
            "systems": InputArtifact(),
            "models": InputArtifact(),
            "additional_systems": InputArtifact(optional=True),
        }
        self._output_parameters = {
        }
        self._output_artifacts = {
            "expl_systems": OutputArtifact()
        }

        super().__init__(
            name=name,
            inputs=Inputs(
                parameters=self._input_parameters,
                artifacts=self._input_artifacts,
            ),
            outputs=Outputs(
                parameters=self._output_parameters,
                artifacts=self._output_artifacts,
            ),
        )
        # list of custom keys    
        self._my_keys = ["task-gen", "collect-data"]
        
        # key for the whole steps
        self._keys = (
            self._my_keys[:1]
            + prep_run_explore_op.keys
            + self._my_keys[1:2]
            #+ self._my_keys[2:3]
        )
        self.step_keys = {}
        for ii in self._my_keys:
            self.step_keys[ii] = "--".join(
                ["%s" % self.inputs.parameters["block_id"], ii]
            )

        self = _block_cl(
            self,
            self.step_keys,
            name,
            expl_tasks_op,
            prep_run_explore_op,
            collect_data_op,
            gen_lmp_step_config,
            collect_data_step_config,
            upload_python_packages=upload_python_packages,
        )
    @property
    def input_parameters(self):
        return self._input_parameters

    @property
    def input_artifacts(self):
        return self._input_artifacts

    @property
    def output_parameters(self):
        return self._output_parameters

    @property
    def output_artifacts(self):
        return self._output_artifacts

    @property
    def keys(self):
        return self._keys

def _block_cl(
    block_steps:Steps,
    step_keys: Dict[str, Any],
    name:str,
    expl_tasks_op: Type[OP],
    prep_run_explore_op: OPTemplate,
    collect_data_op: Type[OP],
    gen_lmp_step_config: dict,
    collect_data_step_config: dict,
    upload_python_packages: Optional[List[os.PathLike]] = None
):
    ## get step config dict (not task config!)
    gen_lmp_step_config = deepcopy(gen_lmp_step_config)
    collect_data_step_config = deepcopy(collect_data_step_config)
    gen_lmp_template_config = gen_lmp_step_config.pop("template_config")
    collect_data_template_config = collect_data_step_config.pop("template_config")
    gen_lmp_executor = init_executor(gen_lmp_step_config.pop("executor"))
    collect_data_executor = init_executor(collect_data_step_config.pop("executor"))

    gen_lmp_tasks = Step(
        name + "gen-lmp-tasks",
        template=PythonOPTemplate(
            expl_tasks_op,
            python_packages=upload_python_packages,
            **gen_lmp_template_config
        ),
        parameters={
            "expl_tasks": block_steps.inputs.parameters["expl_tasks"],
            "type_map": block_steps.inputs.parameters["type_map"],
            "mass_map": block_steps.inputs.parameters["mass_map"]
        },
        artifacts={
            "systems": block_steps.inputs.artifacts["systems"],
        },
        key="--".join(
            ["%s" %block_steps.inputs.parameters["block_id"], "gen-lmp"]
        ),
        executor=gen_lmp_executor,
        **gen_lmp_step_config
        
    )
    block_steps.add(gen_lmp_tasks)
    
    prep_run_lmp = Step(
        name+"prep-run-lmp",
        template=prep_run_explore_op,
        parameters={
            "block_id": block_steps.inputs.parameters["block_id"],
            "explore_config":block_steps.inputs.parameters["explore_config"],
            "type_map": block_steps.inputs.parameters["type_map"],
            "expl_task_grp": gen_lmp_tasks.outputs.parameters["lmp_task_grp"],
        },
        artifacts={
            "models":block_steps.inputs.artifacts["models"]
        },
        key="--".join(
            ["%s" %block_steps.inputs.parameters["block_id"], "prep-run-lmp"]
        )
    )
    block_steps.add(prep_run_lmp)
    
    collect_data = Step(
        name+"collect-data",
        template=PythonOPTemplate(
            collect_data_op,
            python_packages=upload_python_packages,
            **collect_data_template_config
        ),
        parameters={
            "type_map": block_steps.inputs.parameters["type_map"],
            "optional_parameters":{"labeled_data":False}
        },
        artifacts={
            "systems": prep_run_lmp.outputs.artifacts["trajs"],
            "additional_systems":block_steps.inputs.artifacts["additional_systems"]
        },
        key="--".join(
            ["%s" %block_steps.inputs.parameters["block_id"], "collect-data"]
        ),
        executor=collect_data_executor,
        **collect_data_step_config
    )
    block_steps.add(collect_data)
    block_steps.outputs.artifacts["expl_systems"]._from = collect_data.outputs.artifacts["systems"]
    return block_steps


class ExplDistBlock(Steps):
    def __init__(
        self,
        name:str,
        gen_task_op: Type[OP],
        prep_run_explore_op:OPTemplate,
        prep_run_train_op: OPTemplate,
        collect_data_op: Type[OP],
        inference_op: Type[OP],
        gen_task_config:dict,
        inference_config: dict,
        collect_data_config: dict,
        upload_python_packages: Optional[List[os.PathLike]] = None
    ):
        self._input_parameters ={
            "block_id": InputParameter(),
            "type_map": InputParameter(),
            "mass_map": InputParameter(),
            "expl_tasks":InputParameter(),
            "numb_models": InputParameter(type=int),
            "template_script": InputParameter(),
            "train_config": InputParameter(),
            "explore_config": InputParameter(),
            "inference_config": InputParameter(),
            "converge_config": InputParameter(value={}),
            "collect_data_config":InputParameter(value={}),
            "type_map_train": InputParameter()
        }
        self._input_artifacts = {
            "systems": InputArtifact(),
            "teacher_model" : InputArtifact(),
            "init_data": InputArtifact(optional=True),
            "iter_data": InputArtifact(optional=True), # empty list
            "validation_data": InputArtifact(optional=True)
        }
        self._output_parameters ={
            "converged":OutputParameter()
        }
        self._output_artifacts = {
            "iter_data":OutputArtifact(),
            "dist_model": OutputArtifact(),
            "dp_test_report": OutputArtifact()
        }
        super().__init__(
            name=name,
            inputs=Inputs(
                parameters = self._input_parameters,
                artifacts = self._input_artifacts 
            ),
            outputs = Outputs(
                parameters=self._output_parameters,
                artifacts=self._output_artifacts,
            )
        )
        
        self = _expl_dist_cl(
            self,
            name,
            gen_task_op,
            prep_run_explore_op,
            prep_run_train_op,
            collect_data_op,
            inference_op,
            gen_task_config,
            inference_config,
            collect_data_config,
            upload_python_packages
        )
    @property
    def input_parameters(self):
        return self._input_parameters

    @property
    def input_artifacts(self):
        return self._input_artifacts

    @property
    def output_parameters(self):
        return self._output_parameters

    @property
    def output_artifacts(self):
        return self._output_artifacts
    pass


class ExplDistLoop(Steps):
    def __init__(
        self,
        name:str,
        expl_dist_blk_op: OPTemplate,
        upload_python_packages: Optional[List[os.PathLike]] = None,
        
    ):        
        self._input_parameters = {
            "block_id": InputParameter(value=0),
            "type_map": InputParameter(),
            "mass_map": InputParameter(),
            #"init_expl_model": InputParameter(type=bool),
            "expl_stages":InputParameter(), # Total input parameter file: to be changed in the future
            "conf_selector":InputParameter(value={}),
            "numb_models": InputParameter(type=int),
            "template_script": InputParameter(), 
            "train_config": InputParameter(),
            "explore_config": InputParameter(),
            "idx_stage": InputParameter(value=0),
            "max_iter": InputParameter(),
            "converge_config": InputParameter(value={}),
            "inference_config": InputParameter(),
            "test_size":InputParameter(value=0.1),
            "type_map_train": InputParameter()
        }
        self._input_artifacts = {
            "systems": InputArtifact(), # starting systems for model deviation
            "teacher_model" : InputArtifact(), # model for exploration
            "init_data": InputArtifact(), # initial data for model finetune
            "iter_data": InputArtifact(optional=True), # datas collected during previous exploration
        }
        self._output_parameters ={
            "idx_stage": OutputParameter()
        }
        self._output_artifacts = {
            "dist_model": OutputArtifact(),
            #"dp_test_report": OutputArtifact(),
            #"dp_test_detail_files": OutputArtifact(),
            "iter_data": OutputArtifact() # data collected after exploration
        }
        
        super().__init__(
            name=name,
            inputs=Inputs(
                parameters = self._input_parameters,
                artifacts = self._input_artifacts 
            ),
            outputs = Outputs(
                parameters=self._output_parameters,
                artifacts=self._output_artifacts,
            )
        )
        self=_loop(
            self,
            name=name,
            expl_dist_blk_op=expl_dist_blk_op,
            upload_python_packages=upload_python_packages,
        )
    @property
    def input_parameters(self):
        return self._input_parameters

    @property
    def input_artifacts(self):
        return self._input_artifacts

    @property
    def output_parameters(self):
        return self._output_parameters

    @property
    def output_artifacts(self):
        return self._output_artifacts

def _expl_dist_cl(
    steps,
    name:str,
    gen_task_op: Type[OP],
    prep_run_explore_op:OPTemplate,
    prep_run_train_op: OPTemplate,
    collect_data_op: Type[OP],
    inference_op: Type[OP],
    gen_task_config:dict,
    inference_config: dict,
    collect_data_config: dict,
    upload_python_packages: Optional[List[os.PathLike]] = None
    ):
    
    gen_task_config = deepcopy(gen_task_config)
    gen_task_template_config = gen_task_config.pop("template_config")
    gen_task_executor = init_executor(gen_task_config.pop("executor"))
    
    inference_config = deepcopy(inference_config)
    inference_template_config = inference_config.pop("template_config")
    inference_executor = init_executor(inference_config.pop("executor"))
    
    collect_data_config = deepcopy(collect_data_config)
    collect_data_template_config = collect_data_config.pop("template_config")
    collect_data_executor = init_executor(collect_data_config.pop("executor"))

    gen_lmp_tasks = Step(
        name + "gen-lmp-tasks",
        template=PythonOPTemplate(
            gen_task_op,
            python_packages=upload_python_packages,
            **gen_task_template_config
        ),
        parameters={
            "expl_tasks": steps.inputs.parameters["expl_tasks"],
            "type_map": steps.inputs.parameters["type_map"],
            "mass_map": steps.inputs.parameters["mass_map"]
        },
        artifacts={
            "systems": steps.inputs.artifacts["systems"],
        },
        key="--".join(
            ["%s" %steps.inputs.parameters["block_id"], "gen-task"]
        ),
        executor=gen_task_executor,
        **gen_task_config)
    
    steps.add(gen_lmp_tasks)
    
    prep_run_explore = Step(
        name+"prep-run-explore",
        template=prep_run_explore_op,
        parameters={
            "block_id": steps.inputs.parameters["block_id"],
            "explore_config":steps.inputs.parameters["explore_config"],
            "type_map": steps.inputs.parameters["type_map"],
            "expl_task_grp": gen_lmp_tasks.outputs.parameters["lmp_task_grp"],
        },
        artifacts={
            "models":steps.inputs.artifacts["teacher_model"]
        },
        key="--".join(
            ["init", "prep-run-explore"]
        )
    )
    steps.add(prep_run_explore)
    
    collect_data = Step(
        name+"collect-data",
        template=PythonOPTemplate(
            collect_data_op,
            python_packages=upload_python_packages,
            **collect_data_template_config
        ),
        parameters={
            "type_map": steps.inputs.parameters["type_map"],
            "optional_parameters":steps.inputs.parameters["collect_data_config"]
        },
        artifacts={
            "systems": prep_run_explore.outputs.artifacts["trajs"],
            "additional_multi_systems":steps.inputs.artifacts["iter_data"]
        },
        key="--".join(
            ["%s" %steps.inputs.parameters["block_id"], "collect-data"]
        ),
        executor=collect_data_executor,
        **collect_data_config
    )
    steps.add(collect_data)
    
    inference_train = Step(
        name+ "-inference-train",
        template=PythonOPTemplate(
            inference_op,
            python_packages=upload_python_packages,
            **inference_template_config
        ),
        parameters={
            "inference_config": steps.inputs.parameters["inference_config"],
            "type_map": steps.inputs.parameters["type_map"]
        },
        artifacts={
            "systems": collect_data.outputs.artifacts["systems"],
            "model":steps.inputs.artifacts["teacher_model"][0]
        },
         key="--".join(
            ["%s" %steps.inputs.parameters["block_id"], "inference-train"]
        ),
         executor=inference_executor
    )
    
    inference_test = Step(
        name+ "-inference-test",
        template=PythonOPTemplate(
            inference_op,
            python_packages=upload_python_packages,
            **inference_template_config
        ),
        parameters={
            "inference_config": steps.inputs.parameters["inference_config"],
            "type_map": steps.inputs.parameters["type_map"]
        },
        artifacts={
            "systems": collect_data.outputs.artifacts["test_systems"],
            "model":steps.inputs.artifacts["teacher_model"][0]
        },
         key="--".join(
            ["%s" %steps.inputs.parameters["block_id"], "inference-test"]
        ),
         executor=inference_executor
    )
    steps.add([inference_train,inference_test])    
    
    prep_run_dp=Step(
        name+"-prep-run-dp",
        template=prep_run_train_op,
        parameters={
            "block_id": steps.inputs.parameters["block_id"],
            "train_config":steps.inputs.parameters["train_config"],
            "numb_models":steps.inputs.parameters["numb_models"],
            "template_script": steps.inputs.parameters["template_script"]
        },
        artifacts={
            "init_data":steps.inputs.artifacts["init_data"],
            "iter_data":inference_train.outputs.artifacts["root_labeled_systems"],
        },
        key="--".join(["%s" %steps.inputs.parameters["block_id"], "prep-run-train"]),
    )
    steps.add(prep_run_dp)
    
    # the exploration steps for validation
    dp_test = Step(
        name+ "-dp-test",
        template=PythonOPTemplate(
            ModelTestOP,
            python_packages=upload_python_packages,
            **inference_template_config
        ),
        parameters={
            "inference_config": {"model":"dp"},#ft_steps.inputs.parameters["inference_config"],
            "type_map": steps.inputs.parameters["type_map"]
        },
        artifacts={
            "systems": inference_test.outputs.artifacts["labeled_systems"],
            "model": prep_run_dp.outputs.artifacts["models"][0]
        },
        key="--".join(
            ["%s" %steps.inputs.parameters["block_id"], "validation-test"]
        ),
        executor=inference_executor
    )
    steps.add(dp_test)
    
    evaluate=Step(
        name="evaluate-converge", 
        template=PythonOPTemplate(
            EvalConv,
            python_packages=upload_python_packages,
            **collect_data_template_config,
            ), 
        parameters={
            "config": steps.inputs.parameters["converge_config"],
            "test_res":dp_test.outputs.parameters["test_res"]},
        key="--".join(
                ["%s"%steps.inputs.parameters["block_id"], 'evaluate-converge' ]
                ),
        **collect_data_config
    )
    steps.add(evaluate)
    steps.outputs.artifacts["iter_data"]._from = collect_data.outputs.artifacts["multi_systems"]
    steps.outputs.artifacts[
        "dist_model"
        ]._from = prep_run_dp.outputs.artifacts["models"][0]
    steps.outputs.artifacts[
        "dp_test_report"
        ]._from = dp_test.outputs.artifacts["test_report"]
    steps.outputs.parameters[
        "converged"].value_from_parameter = evaluate.outputs.parameters["converged"]
    return steps    

def _loop(
    loop, # the loop Steps
    name:str,
    expl_dist_blk_op: OPTemplate,
    upload_python_packages: Optional[List[os.PathLike]] = None,
    ):
    # we just need a counter which supplies the iteration
    blk_counter=Step(
        name="iter-counter", 
        template=PythonOPTemplate(
            IterCounter,
            image="registry.dp.tech/dptech/ubuntu:22.04-py3.10",
            python_packages=upload_python_packages
            ),
        parameters={
                 "iter_numb": loop.inputs.parameters["block_id"]},
        key="--".join(
                ["%s" % "iter-end","%s"%loop.inputs.parameters["block_id"] ]
                ))
    loop.add(blk_counter)
    
    # add a stage counter
    stage_scheduler=Step(
        name="stage-scheduler", 
        template=PythonOPTemplate(
            StageScheduler,
            image="registry.dp.tech/dptech/ubuntu:22.04-py3.10",
            python_packages=upload_python_packages
            ),
        parameters={
                 "stages": loop.inputs.parameters["expl_stages"],
                 "idx_stage": loop.inputs.parameters["idx_stage"],
                 },
        key="--".join(
                ["iter-%s"%blk_counter.outputs.parameters["iter_id"], "stage-schedule"]
                ))
    loop.add(stage_scheduler)
    
    expl_dist_blk= Step(
        name=name+'-exploration-dist',
        template=expl_dist_blk_op,
        parameters={
            "block_id": "iter-%s"% blk_counter.outputs.parameters["iter_id"],
            "type_map": loop.inputs.parameters["type_map"],
            "mass_map":loop.inputs.parameters["mass_map"],
            "expl_tasks":stage_scheduler.outputs.parameters["tasks"],
            "converge_config":loop.inputs.parameters["converge_config"],
            "numb_models": loop.inputs.parameters["numb_models"],
            "template_script": loop.inputs.parameters["template_script"], 
            "train_config": loop.inputs.parameters["train_config"],
            "explore_config": loop.inputs.parameters["explore_config"],
            "inference_config":loop.inputs.parameters["inference_config"],
            "type_map_train": loop.inputs.parameters["type_map_train"],
            "collect_data_config":{"labeled_data":False,
                                   "test_size":loop.inputs.parameters["test_size"],
                                    "multi_sys_name": blk_counter.outputs.parameters["iter_id"]}
            },
        artifacts={
            "systems": loop.inputs.artifacts["systems"], # starting systems for model deviation
            "teacher_model" : loop.inputs.artifacts["teacher_model"], # model for exploration
            "init_data": loop.inputs.artifacts["init_data"],
            "iter_data": loop.inputs.artifacts["iter_data"]
        },
        
        key="--".join(
                ["iter-%s"%blk_counter.outputs.parameters["iter_id"], "expl-ft-loop" ]
                ))
    loop.add(expl_dist_blk)
    
    # a evaluation step: to be added
    next_loop=Step(
        name="next-loop", 
        template=PythonOPTemplate(
            NextLoop,
            image="registry.dp.tech/dptech/ubuntu:22.04-py3.10",
            python_packages=upload_python_packages
            ), 
        parameters={
            "converged":expl_dist_blk.outputs.parameters["converged"],
            "iter_numb": blk_counter.outputs.parameters["next_iter_numb"],
            "max_iter": loop.inputs.parameters["max_iter"],
            "stages":loop.inputs.parameters["expl_stages"],
            "idx_stage":loop.inputs.parameters["idx_stage"]},
        key="--".join(
                ["iter-%s"%blk_counter.outputs.parameters["iter_id"], "next-loop" ]
                ))
    loop.add(next_loop)
    # next iteration
    next_parameters={
            "block_id": blk_counter.outputs.parameters["next_iter_numb"],
            "type_map": loop.inputs.parameters["type_map"],
            "mass_map":loop.inputs.parameters["mass_map"],
            "expl_stages":loop.inputs.parameters["expl_stages"], # Total input parameter file: to be changed in the future
            "idx_stage": next_loop.outputs.parameters["idx_stage"],
            "converge_config":loop.inputs.parameters["converge_config"], # Total input parameter file: to be changed in the future
            "numb_models": loop.inputs.parameters["numb_models"],
            "template_script": loop.inputs.parameters["template_script"], 
            "train_config": loop.inputs.parameters["train_config"],
            "max_iter": loop.inputs.parameters["max_iter"],
            "explore_config": loop.inputs.parameters["explore_config"],
            "inference_config":loop.inputs.parameters["inference_config"],
            "type_map_train": loop.inputs.parameters["type_map_train"]
            }
    next_step=Step(
        name=name+'-exploration-finetune-next',
        template=loop,
        parameters=next_parameters,
        artifacts={
            "systems":loop.inputs.artifacts["systems"],
            "teacher_model": loop.inputs.artifacts["teacher_model"],
            "iter_data": expl_dist_blk.outputs.artifacts["iter_data"],
            "init_data": loop.inputs.artifacts["init_data"],
        },        
        when="%s == false"%(
            next_loop.outputs.parameters["converged"],
        ),
        key="--".join(
                ["iter-%s" % blk_counter.outputs.parameters["next_iter_id"] ,"expl-ft-loop" ]
                )
    )
    loop.add(next_step)
    loop.outputs.parameters["idx_stage"
                            ].value_from_parameter= next_loop.outputs.parameters["idx_stage"]
    loop.outputs.artifacts["dist_model"
        ]._from = expl_dist_blk.outputs.artifacts["dist_model"]
    loop.outputs.artifacts[
        "iter_data"
        ]._from = expl_dist_blk.outputs.artifacts["iter_data"]
    return loop