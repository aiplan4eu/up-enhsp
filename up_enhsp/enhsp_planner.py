import pkg_resources # type: ignore
import unified_planning as up
from unified_planning.solvers.results import PlanGenerationResultStatus
from unified_planning.model import ProblemKind
from unified_planning.solvers import PDDLSolver
from typing import Optional, List, Union


class ENHSPsolver(PDDLSolver):

    def __init__(self, search_algorithm: Optional[str] = None, heuristic: Optional[str] = None):
        super().__init__(needs_requirements=False)
        self.search_algorithm = search_algorithm
        self.heuristic = heuristic

    def destroy(self):
        pass

    @property
    def name(self) -> str:
        return 'enhsp'

    @staticmethod
    def is_oneshot_planner() -> bool:
        return True

    def _manage_parameters(self, command):
        if self.search_algorithm is not None:
            command += ['-s', self.search_algorithm]
        if self.heuristic is not None:
            command += ['-h', self.heuristic]
        return command

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        base_command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'), '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename]
        return self._manage_parameters(base_command)

    def _result_status(self, problem: 'up.model.Problem', plan: Optional['up.plan.Plan']) -> 'PlanGenerationResultStatus':
        '''Takes a problem and a plan and returns the status that represents this plan.
        The possible status with their interpretation can be found in the up.plan file.'''
<<<<<<< HEAD
        return PlanGenerationResultStatus.UNSOLVABLE_PROVEN if plan is None else PlanGenerationResultStatus.SOLVED_SATISFICING
=======
        return unified_planning.solvers.results.PlanGenerationResultStatus.UNSOLVABLE_PROVEN if plan is None else unified_planning.solvers.results.PlanGenerationResultStatus.SOLVED_SATISFICING
>>>>>>> master

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


class ENHSPSatSolver(ENHSPsolver):

    @property
    def name(self) -> str:
        return 'SAT-enhsp'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'),
                   '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,
                   '-s gbfs','-h hmrp','-ht true']
        return command


class ENHSPOptSolver(ENHSPsolver):

    @property
    def name(self) -> str:
        return 'OPT-enhsp'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'),
                   '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,
                   '-s','WAStar','-h','hrmax']
        return command

    @staticmethod
    def satisfies(optimality_guarantee: Union['up.solvers.solver.OptimalityGuarantee', str]) -> bool:
        return True

    def _result_status(self, problem: 'up.model.Problem', plan: Optional['up.plan.Plan']) -> 'PlanGenerationResultStatus':
        '''Takes a problem and a plan and returns the status that represents this plan.
        The possible status with their interpretation can be found in the up.plan file.'''
        return PlanGenerationResultStatus.UNSOLVABLE_PROVEN if plan is None else up.solvers.results.PlanGenerationResultStatus.SOLVED_OPTIMALLY
