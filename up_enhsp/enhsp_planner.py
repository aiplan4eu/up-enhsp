import pkg_resources
import unified_planning as up
from unified_planning.engines import PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.model import ProblemKind
from unified_planning.engines import PDDLPlanner, PDDLAnytimePlanner, Credits, LogMessage
from typing import Optional, List, Union, Iterator, IO


credits = Credits('ENHSP',
                  'Enrico Scala',
                  'enricos83@gmail.com',
                  'https://sites.google.com/view/enhsp/',
                  'GPL',
                  'Expressive Numeric Heuristic Search Planner.',
                  'ENHSP is a planner supporting (sub)optimal classical and numeric planning with linear and non-linear expressions.')


class ENHSPEngine(PDDLPlanner):

    def __init__(self, params: Optional[str] = None):
        super().__init__(needs_requirements=False, rewrite_bool_assignments = True)
        self.params = params

    @property
    def name(self) -> str:
        return 'enhsp'

    def _manage_parameters(self, command):
        if self.params is not None:
            command += self.params.split()
        else:
            command += ['-h','hadd','-s','gbfs']
        return command

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        base_command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'), '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,'-npm']
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
        supported_kind = ProblemKind(version=2)
        supported_kind.set_problem_class('ACTION_BASED')
        supported_kind.set_typing('FLAT_TYPING')
        supported_kind.set_typing('HIERARCHICAL_TYPING')
        supported_kind.set_fluents_type("INT_FLUENTS")
        supported_kind.set_fluents_type("REAL_FLUENTS")
        supported_kind.set_conditions_kind('NEGATIVE_CONDITIONS')
        supported_kind.set_conditions_kind('DISJUNCTIVE_CONDITIONS')
        supported_kind.set_conditions_kind('EXISTENTIAL_CONDITIONS')
        supported_kind.set_conditions_kind('UNIVERSAL_CONDITIONS')
        supported_kind.set_conditions_kind('EQUALITIES')
        supported_kind.set_problem_type('SIMPLE_NUMERIC_PLANNING')
        supported_kind.set_problem_type('GENERAL_NUMERIC_PLANNING')
        supported_kind.set_effects_kind('INCREASE_EFFECTS')
        supported_kind.set_effects_kind('DECREASE_EFFECTS')
        supported_kind.set_effects_kind('FORALL_EFFECTS')
        supported_kind.set_effects_kind('CONDITIONAL_EFFECTS')
        supported_kind.set_effects_kind('STATIC_FLUENTS_IN_BOOLEAN_ASSIGNMENTS')
        supported_kind.set_effects_kind('STATIC_FLUENTS_IN_NUMERIC_ASSIGNMENTS')
        supported_kind.set_effects_kind('FLUENTS_IN_BOOLEAN_ASSIGNMENTS')
        supported_kind.set_effects_kind('FLUENTS_IN_NUMERIC_ASSIGNMENTS')
        supported_kind.set_quality_metrics("ACTIONS_COST")
        supported_kind.set_quality_metrics("PLAN_LENGTH")
        supported_kind.set_quality_metrics("FINAL_VALUE")
        supported_kind.set_actions_cost_kind("STATIC_FLUENTS_IN_ACTIONS_COST")
        supported_kind.set_actions_cost_kind("FLUENTS_IN_ACTIONS_COST")
        supported_kind.set_actions_cost_kind("INT_NUMBERS_IN_ACTIONS_COST")
        supported_kind.set_actions_cost_kind("REAL_NUMBERS_IN_ACTIONS_COST")
        supported_kind.set_time("PROCESSES")
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        return problem_kind <= ENHSPEngine.supported_kind()

    @staticmethod
    def get_credits(**kwargs) -> Optional['Credits']:
        return credits


class ENHSPAnytimeEngine(ENHSPEngine, PDDLAnytimePlanner):
    def __init__(self, params: Optional[str] = None):
        ENHSPEngine.__init__(self,params)
        PDDLAnytimePlanner.__init__(self)

    @property
    def name(self) -> str:
        return 'Anytime-enhsp'


    def _get_anytime_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'),
                   '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,'-anytime']
        return self._manage_parameters(command)

    @staticmethod
    def ensures(anytime_guarantee: up.engines.AnytimeGuarantee) -> bool:
        if anytime_guarantee == up.engines.AnytimeGuarantee.INCREASING_QUALITY:
            return True
        return False

    def _starting_plan_str(self) -> str:
        return "Found Plan:"

    def _ending_plan_str(self) -> str:
        return "Plan-Length:"

    def _parse_plan_line(self, plan_line: str) -> str:
        return plan_line.split(":")[1]




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
        supported_kind.unset_effects_kind('FLUENTS_IN_NUMERIC_ASSIGNMENTS')
        supported_kind.unset_actions_cost_kind("FLUENTS_IN_ACTIONS_COST")
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

class ENHSPOptBlindEngine(ENHSPOptEngine):

    @property
    def name(self) -> str:
        return 'BLIND-enhsp'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'),
                   '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,
                   '-s','WAStar','-h','blind','-ties','larger_g']
        return command

    @staticmethod
    def supported_kind() -> 'ProblemKind':
        supported_kind = ENHSPEngine.supported_kind()
        return supported_kind
