import pkg_resources
import tempfile
import os
import re
import subprocess
from unified_planning.shortcuts import *
from unified_planning.io.pddl_writer import PDDLWriter
from unified_planning.exceptions import UPException
from typing import Optional, List


class ENHSPsolver(Solver):

    def destroy(self):
        pass

    DEFAULT_SAT_CONFIGURATION = 'sat-hmrp'
    DEFAULT_OPT_CONFIGURATION = 'opt-hmax'

    def __init__(self, search_algorithm: Optional[str] = None, heuristic: Optional[str] = None):
        super().__init__()
        self.search_algorithm = search_algorithm
        self.heuristic = heuristic
        self._needs_requirements = False

    @staticmethod
    def name() -> str:
        return 'enhsp'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        base_command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'), '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename]
        return self.manage_parameters(base_command)

    def manage_parameters(self, command):
        if self.search_algorithm is not None:
            command += ['-s', self.search_algorithm]
        if self.heuristic is not None:
            command += ['-h', self.heuristic]
        if self.search_algorithm is None and self.heuristic is None:
            command += ['-planner', self.DEFAULT_SAT_CONFIGURATION]
        return command

    def _plan_from_file(self, problem: 'unified_planning.model.Problem', plan_filename: str) -> 'unified_planning.plan.Plan':
        actions = []
        with open(plan_filename) as plan:
            for line in plan.readlines():
                if re.match(r'^\s*(;.*)?$', line):
                    continue
                res = re.match(r'^\s*\(\s*([\w?-]+)((\s+[\w?-]+)*)\s*\)\s*$', line)
                if res:
                    action = problem.action(res.group(1))
                    parameters = []
                    for p in res.group(2).split():
                        parameters.append(ObjectExp(problem.object(p)))
                    actions.append(unified_planning.plan.ActionInstance(action, tuple(parameters)))
                else:
                    raise UPException('Error parsing plan generated by ' + self.__class__.__name__)
        return unified_planning.plan.SequentialPlan(actions)

    def solve(self, problem: 'unified_planning.model.Problem') -> Optional['unified_planning.plan.Plan']:
        w = PDDLWriter(problem, self._needs_requirements)
        plan = None
        with tempfile.TemporaryDirectory() as tempdir:
            domain_filename = os.path.join(tempdir, 'domain.pddl')
            problem_filename = os.path.join(tempdir, 'problem.pddl')
            plan_filename = os.path.join(tempdir, 'plan.txt')
            w.write_domain(domain_filename)
            w.write_problem(problem_filename)

            cmd = self._get_cmd(domain_filename, problem_filename, plan_filename)
            res = subprocess.run(cmd, capture_output=True)

            if not os.path.isfile(plan_filename):
                print(res.stderr.decode())
            else:
                plan = self._plan_from_file(problem, plan_filename)

        return plan

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        supported_kind = ProblemKind()
        supported_kind.set_numbers('CONTINUOUS_NUMBERS')  # type: ignore
        supported_kind.set_numbers('DISCRETE_NUMBERS')  # type: ignore
        supported_kind.set_typing('FLAT_TYPING')  # type: ignore
        supported_kind.set_fluents_type('NUMERIC_FLUENTS')  # type: ignore
        supported_kind.set_conditions_kind('NEGATIVE_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('DISJUNCTIVE_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('EXISTENTIAL_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('UNIVERSAL_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('EQUALITY')  # type: ignore
        supported_kind.set_effects_kind('INCREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('DECREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('CONDITIONAL_EFFECTS')  # type: ignore
        return problem_kind <= supported_kind

    @staticmethod
    def is_grounder() -> bool:
        return False

    @staticmethod
    def is_plan_validator() -> bool:
        return False

    @staticmethod
    def is_oneshot_planner() -> bool:
        return True

