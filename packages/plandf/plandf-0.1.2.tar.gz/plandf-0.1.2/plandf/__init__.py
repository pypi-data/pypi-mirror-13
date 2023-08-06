from plan_maker import PlanMaker

def read(plan_tuples, conversion_rates=False):

    if not isinstance(conversion_rates, bool):
        try:
            p = PlanMaker(plan_tuples, conversion_rates)
        except:
            """ Could not retrieve currency conversion rates. """
            p = False

    else:
		p = PlanMaker(plan_tuples)

    if p:
        return p.get_scenarios()
    else:
		return "Could not read the plan_tuples."
