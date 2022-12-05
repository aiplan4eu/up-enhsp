import pkg_resources # type: ignore
import unified_planning as up
from unified_planning.engines.results import PlanGenerationResultStatus
from unified_planning.model import ProblemKind
from unified_planning.engines import PDDLPlanner, Credits, LogMessage
from typing import Optional, List, Union


credits = Credits('ENHSP',
                  'Enrico Scala',
                  'enricos83@gmail.com',
                  'https://sites.google.com/view/enhsp/',
                  'GPL',
                  'Expressive Numeric Heuristic Search Planner.',
                  'ENHSP is a planner supporting (sub)optimal classical and numeric planning with linear and non-linear expressions.')

class ENHSPEngine(PDDLPlanner):

    def __init__(self, search_algorithm: Optional[str] = None, heuristic: Optional[str] = None):
        super().__init__(needs_requirements=False)
        self.search_algorithm = search_algorithm
        self.heuristic = heuristic

    @property
    def name(self) -> str:
        return 'enhsp'

    def _manage_parameters(self, command):
        if self.search_algorithm is not None:
            command += ['-s', self.search_algorithm]
        if self.heuristic is not None:
            command += ['-h', self.heuristic]
        return command

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        base_command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'), '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename]
        return self._manage_parameters(base_command)

    def _result_status(
        self,
        problem: 'up.model.Problem',
        plan: Optional['up.plans.Plan'],
        retval: int = 0,
        log_messages: Optional[List['LogMessage']] = None,
    ) -> 'PlanGenerationResultStatus':
        if retval != 0:
            return PlanGenerationResultStatus.INTERNAL_ERROR
        elif plan is None:
            return PlanGenerationResultStatus.UNSOLVABLE_PROVEN
        else:
            return PlanGenerationResultStatus.SOLVED_SATISFICING

    @staticmethod
    def supported_kind() -> 'ProblemKind':
        supported_kind = ProblemKind()
        supported_kind.set_problem_class('ACTION_BASED')  # type: ignore
        supported_kind.set_numbers('CONTINUOUS_NUMBERS')  # type: ignore
        supported_kind.set_numbers('DISCRETE_NUMBERS')  # type: ignore
        supported_kind.set_typing('FLAT_TYPING')  # type: ignore
        supported_kind.set_typing('HIERARCHICAL_TYPING')  # type: ignore
        supported_kind.set_fluents_type('NUMERIC_FLUENTS')  # type: ignore
        supported_kind.set_conditions_kind('NEGATIVE_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('DISJUNCTIVE_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('EXISTENTIAL_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('UNIVERSAL_CONDITIONS')  # type: ignore
        supported_kind.set_conditions_kind('EQUALITY')  # type: ignore
        supported_kind.set_problem_type('SIMPLE_NUMERIC_PLANNING')  # type: ignore
        supported_kind.set_problem_type('GENERAL_NUMERIC_PLANNING')  # type: ignore
        supported_kind.set_effects_kind('INCREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('DECREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('CONDITIONAL_EFFECTS')  # type: ignore
        supported_kind.set_quality_metrics("ACTIONS_COST")
        supported_kind.set_quality_metrics("PLAN_LENGTH")
        supported_kind.set_quality_metrics("FINAL_VALUE")
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        return problem_kind <= ENHSPEngine.supported_kind()

    @staticmethod
    def get_credits(**kwargs) -> Optional['Credits']:
        return credits


class ENHSPSatEngine(ENHSPEngine):

    @property
    def name(self) -> str:
        return 'SAT-enhsp'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'),
                   '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,
                   '-s','gbfs','-h','hadd']
        return command


class ENHSPOptEngine(ENHSPEngine):

    @property
    def name(self) -> str:
        return 'OPT-enhsp'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'),
                   '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,
                   '-s','WAStar','-h','hrmax']
        return command

    @staticmethod
    def supported_kind() -> 'ProblemKind':
        supported_kind = ENHSPEngine.supported_kind()
        supported_kind.unset_problem_type('GENERAL_NUMERIC_PLANNING')
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        return problem_kind <= ENHSPOptEngine.supported_kind()

    @staticmethod
    def satisfies(optimality_guarantee: 'up.engines.engine.OptimalityGuarantee') -> bool:
        return True

    def _result_status(
        self,
        problem: 'up.model.Problem',
        plan: Optional['up.plans.Plan'],
        retval: int = 0,
        log_messages: Optional[List['LogMessage']] = None,
    ) -> 'PlanGenerationResultStatus':
        if retval != 0:
            return PlanGenerationResultStatus.INTERNAL_ERROR
        elif plan is None:
            return PlanGenerationResultStatus.UNSOLVABLE_PROVEN
        else:
            if not problem.quality_metrics:
                return PlanGenerationResultStatus.SOLVED_SATISFICING
            return PlanGenerationResultStatus.SOLVED_OPTIMALLY