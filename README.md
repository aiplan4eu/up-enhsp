# ENHSP Unified Planning integrator 

## Installation
After cloning this repository run ```pip install up-enhsp/```. 

ENHSP and the openjdk-17 will be downloaded and packaged together.

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