from typing import List, Dict
from dflow.python import OP, OPIO, Artifact, BigParameter, OPIOSign, Parameter
from pathlib import Path
from pfd.exploration.scheduler.sheduler import Scheduler
from pfd.exploration.task import ExplorationStage, BaseExplorationTaskGroup, task_group
from pfd.exploration.converge import ConvReport
from pfd.exploration import explore_styles


class StageScheduler(OP):
    def __init__(self):
        pass

    @classmethod
    def get_input_sign(cls):
        return OPIOSign(
            {
                "scheduler": Parameter(Scheduler),
                "systems": Artifact(List[Path]),
                "converged": Parameter(bool, value=False),
                "report": Parameter(ConvReport, value=None),
            }
        )

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "scheduler": Parameter(Scheduler),
                "task_grp": BigParameter(BaseExplorationTaskGroup, default=None),
                "iter_numb": Parameter(int),
                "iter_id": Parameter(str),
                "next_iter_id": Parameter(str),
                "converged": Parameter(bool),
            }
        )

    @OP.exec_sign_check
    def execute(
        self,
        ip: OPIO,
    ) -> OPIO:
        """
        Generate exploration tasks based on model and exploration styles
        """
        systems = ip["systems"]
        scheduler = ip["scheduler"]
        converged = ip["converged"]

        if report := ip["report"]:
            scheduler.add_report(report)

        # check convergence
        scheduler.set_convergence(convergence_stage=converged)

        ret = {}
        # if not converged
        if not scheduler.convergence:
            task_grp = scheduler.set_explore_tasks(systems)
            ret["task_grp"] = task_grp

        ret.update(
            {
                "scheduler": scheduler,
                "iter_numb": scheduler.iter_numb,
                "iter_id": "%03d" % scheduler.iter_numb,
                "next_iter_id": "%03d" % (scheduler.iter_numb + 1),
                "converged": scheduler.convergence,
            }
        )

        return OPIO(ret)
