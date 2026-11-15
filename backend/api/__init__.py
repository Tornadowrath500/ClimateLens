"""HTTP routers. One module per feature area so teams can work without merge conflicts."""

from backend.api import applicants, byom, data, evaluation, experiment, fairness_tools, system

routers = [system.router, data.router, evaluation.router, experiment.router, applicants.router,
           fairness_tools.router, byom.router]
