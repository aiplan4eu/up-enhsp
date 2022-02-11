# ENHSP Unified Planning integrator 

## Installation
After cloning this repository run ```pip install up-enhsp/```. 

ENHSP will be downloaded and compiled directory from the public repository of ENHSP.
ENHSP, and therefore this integrator requires openjdk 17 installed on your machine.

The installation has been tested in Ubuntu 20.04.3 LTS and in MACOS Monterey 12.1

### Features:
- One shot planning
- Default configuration: Greedy Best First Search as search algorithm + Mrp heuristic with/without helpful actions/transitions


## Unified Planning Integration
At the moment the integration with the Unified Planning Framework is obtained through manually adding to the environment factory of the unified planning framework the class implemented by this integrator. 
For example the following piece of code is to be invoked before any use of the ENHSP planner.

```
from unified_planning.environment import get_env
env = get_env()
env.factory.add_solver('enhsp', 'up_enhsp', 'ENHSPsolver')
```

