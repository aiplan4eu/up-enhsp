import unified_planning
from unified_planning.shortcuts import *
from unified_planning.io.pddl_reader import PDDLReader
import unified_planning.transformers
from unittest import TestCase
import pkg_resources


class ENHSPtest(TestCase):

    def test_enhsp(self):
        Location = UserType('Location')
        robot_at = unified_planning.model.Fluent('robot_at', BoolType(), [Location])
        connected = unified_planning.model.Fluent('connected', BoolType(), [Location, Location])
        move = unified_planning.model.InstantaneousAction('move', l_from=Location, l_to=Location)
        l_from = move.parameter('l_from')
        l_to = move.parameter('l_to')
        move.add_precondition(connected(l_from, l_to))
        move.add_precondition(robot_at(l_from))
        move.add_effect(robot_at(l_from), False)
        move.add_effect(robot_at(l_to), True)

        problem = unified_planning.model.Problem('robot')
        problem.add_fluent(robot_at, default_initial_value=False)
        problem.add_fluent(connected, default_initial_value=False)
        problem.add_action(move)

        NLOC = 10
        locations = [unified_planning.model.Object('l%s' % i, Location) for i in range(NLOC)]
        problem.add_objects(locations)

        problem.set_initial_value(robot_at(locations[0]), True)
        for i in range(NLOC - 1):
            problem.set_initial_value(connected(locations[i], locations[i + 1]), True)

        problem.add_goal(robot_at(locations[-1]))

        with OneshotPlanner(name='enhsp') as planner:
            plan = planner.solve(problem)
            print("%s returned: %s" % (planner.name(), plan))

    def test_enhsp_from_pddl(self):
        reader = PDDLReader()
        pddl_problem = reader.parse_problem(pkg_resources.resource_filename(__name__, 'PDDL/NumRover.pddl'), pkg_resources.resource_filename(__name__, 'PDDL/pfile1'))

        with OneshotPlanner(name='enhsp') as planner:
            plan = planner.solve(pddl_problem)
            print("%s returned: %s" % (planner.name(), plan))
