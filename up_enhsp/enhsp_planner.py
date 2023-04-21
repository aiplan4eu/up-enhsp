import pkg_resources 
import unified_planning as up
from unified_planning.engines import PlanGenerationResult, PlanGenerationResultStatus
from unified_planning.model import ProblemKind
from unified_planning.engines import PDDLPlanner, Credits, LogMessage
from unified_planning.engines.mixins import AnytimePlannerMixin
from typing import Optional, List, Union, Iterator, IO


credits = Credits('ENHSP',
                  'Enrico Scala',
                  'enricos83@gmail.com',
                  'https://sites.google.com/view/enhsp/',
                  'GPL',
                  'Expressive Numeric Heuristic Search Planner.',
                  'ENHSP is a planner supporting (sub)optimal classical and numeric planning with linear and non-linear expressions.')

class ENHSPEngine(PDDLPlanner):

    def __init__(self, search_algorithm: Optional[str] = None, heuristic: Optional[str] = None):
        super().__init__(needs_requirements=False, rewrite_bool_assignments = True)
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
        supported_kind.set_conditions_kind('EQUALITIES')  # type: ignore
        supported_kind.set_problem_type('SIMPLE_NUMERIC_PLANNING')  # type: ignore
        supported_kind.set_problem_type('GENERAL_NUMERIC_PLANNING')  # type: ignore
        supported_kind.set_effects_kind('INCREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('DECREASE_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('CONDITIONAL_EFFECTS')  # type: ignore
        supported_kind.set_effects_kind('STATIC_FLUENTS_IN_BOOLEAN_ASSIGNMENTS')  # type: ignore
        supported_kind.set_effects_kind('STATIC_FLUENTS_IN_NUMERIC_ASSIGNMENTS')  # type: ignore
        supported_kind.set_effects_kind('FLUENTS_IN_BOOLEAN_ASSIGNMENTS')  # type: ignore
        supported_kind.set_effects_kind('FLUENTS_IN_NUMERIC_ASSIGNMENTS')  # type: ignore
        supported_kind.set_quality_metrics("ACTIONS_COST") # type: ignore
        supported_kind.set_quality_metrics("PLAN_LENGTH") # type: ignore
        supported_kind.set_quality_metrics("FINAL_VALUE") # type: ignore
        return supported_kind

    @staticmethod
    def supports(problem_kind: 'ProblemKind') -> bool:
        return problem_kind <= ENHSPEngine.supported_kind()

    @staticmethod
    def get_credits(**kwargs) -> Optional['Credits']:
        return credits

class ENHSPAnytimeEngine(ENHSPEngine,AnytimePlannerMixin):
    @property
    def name(self) -> str:
        return 'OPT-enhsp'

    def _get_cmd(self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        command = ['java', '-jar', pkg_resources.resource_filename(__name__, 'ENHSP/enhsp.jar'),
                   '-o', domain_filename, '-f', problem_filename, '-sp', plan_filename,
                   '-s','gbfs','-h','hadd','-anytime']
        return command 
    @staticmethod
    def ensures(anytime_guarantee: up.engines.AnytimeGuarantee) -> bool:
        if anytime_guarantee == up.engines.AnytimeGuarantee.INCREASING_QUALITY:
            return True
        return False
    
    def _get_solutions(
        self,
        problem: "up.model.AbstractProblem",
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> Iterator["up.engines.results.PlanGenerationResult"]:
        import threading
        import queue

        q: queue.Queue = queue.Queue()

        class Writer(up.AnyBaseClass):
            def __init__(self, os, q, engine):
                self._os = os
                self._q = q
                self._engine = engine
                self._plan = []
                self._storing = False

            def write(self, txt: str):
                if self._os is not None:
                    self._os.write(txt)
                for l in txt.splitlines():
                    if "Found Plan:" in l:
                        self._storing = True
                    elif "Plan-Length:" in l:
                        plan_str = "\n".join(self._plan)
                        plan = self._engine._plan_from_str(
                            problem, plan_str, self._engine._writer.get_item_named
                        )
                        res = PlanGenerationResult(
                            PlanGenerationResultStatus.INTERMEDIATE,
                            plan=plan,
                            engine_name=self._engine.name,
                        )
                        self._q.put(res)
                        self._plan = []
                        self._storing = False
                    elif self._storing and l:
                        self._plan.append(l.split(":")[1])

        def run():
            writer: IO[str] = Writer(output_stream, q, self)
            res = self._solve(problem, output_stream=writer)
            q.put(res)

        try:
            t = threading.Thread(target=run, daemon=True)
            t.start()
            status = PlanGenerationResultStatus.INTERMEDIATE
            while status == PlanGenerationResultStatus.INTERMEDIATE:
                res = q.get()
                status = res.status
                yield res
        finally:
            if self._process is not None:
                try:
                    self._process.kill()
                except OSError:
                    pass  # This can happen if the process is already terminated
            t.join()

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