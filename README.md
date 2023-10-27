# ENHSP Unified Planning integrator 
This is the ENHSP UP integrator. ENHSP is an expressive numeric planner supporting planning problems involving Boolean and numeric state variables, actions, processes and events as those that can be expressed using the PDDL+ language. A distinctive feature of ENHSP is the ability to reason over problems with a prevalent numeric structure, which may involve linear and non-linear numeric conditions. ENHSP favors the capability of modeling expressive problems; indeed it handles disjunctive preconditions and conditional effects without compiling them away through potentially expensive compilations (e.g., exponential conversion into DNF). ENHSP can be used as a satisficing or optimal planner, yet optimality is only guaranteed for fragments of PDDL+, in particular so called [simple numeric planning problems](https://www.jair.org/index.php/jair/article/download/11875/26598/). ENHSP is written completely in JAVA. In the context of the UP, ENHSP can be used to solve numeric planning problems without processes and events.
ENHSP has been firstly presented [here](https://ebooks.iospress.nl/pdf/doi/10.3233/978-1-61499-672-9-655), yet it contains many features studied in several other papers from the AI Planning literature.
Look at ENHSP's website for more information on its strengths, weaknesess and parameters [here](https://sites.google.com/view/enhsp/).

## Installation
After cloning this repository, run ```pip install up-enhsp```. up-enhsp can also be installed through the unified-planning framework with the command ```pip install unified-planning[enhsp]```. 
ENHSP will be downloaded and compiled directory from the public repository of ENHSP.
ENHSP, and therefore this integrator requires the openjdk 17 installed on your machine.

## Planning approaches of UP supported
Numeric Planning

## Configuration
ENHSP is a highly configurable planner. Its parameters can be accessed through the parameters field when calling the planner. By default, the satisficing version of the planner calls Greedy Best First Search as search algorithm with the $h_{add}$ heuristic. The optimal version (class ENHSPOptEngine) calls $A^*$ with the $h_{rmax}$ heuristic. You can also access a fully blind version of the algorithm through class ENHSPOptBlindEngine. Where indeed the ENHSPOptEngine is guaranteed to find optimal solutions for simple numeric problems only, the blind version has no limits in the expressivness supported (conditional effects, non-linear planning and so forth).

## Operative modes of UP currently supported
Oneshot planning [UP Documentation](https://unified-planning.readthedocs.io/en/latest/operation_modes.html#oneshotplanner)
Anytime planning [UP Documentation](https://unified-planning.readthedocs.io/en/latest/operation_modes.html#anytimeplanner)

## Acknowledgments

<img src="https://www.aiplan4eu-project.eu/wp-content/uploads/2021/07/euflag.png" width="60" height="40">

This library is being developed for the AIPlan4EU H2020 project (https://aiplan4eu-project.eu) that is funded by the European Commission under grant agreement number 101016442.
