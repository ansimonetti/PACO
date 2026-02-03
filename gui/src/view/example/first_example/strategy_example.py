import dash_bootstrap_components as dbc
from dash import html


def get_strategy_example():
	return dbc.Card([
		dbc.CardHeader("Objective"),
		dbc.CardBody([
			html.P('''
								Find a strategy that has the overall impact of the process in the limit of the expected impact.
								Here we explain the process in more details and next we will see which path brings us to the winning strategy.
								The numbers next to decision points indicate the probability of each path being chosen.
								For example, there’s a high probability (0.8) of the process moving from bending to light polishing and a low probability (0.2) of it moving to fine heavy polishing.
								Imagine in this example our expected impact is 𝑒𝑖 = [155, 7.5] and we have to find a strategy that guarantees the overall impact of the process does not exceed the expected impact.
								A strategy (𝑆) is a winning one for a BPMN+CPI and a vector bound (𝑒𝑖) if and only if ∑ 𝑝(𝑐)𝐼(𝑐) ≤ 𝑒𝑖 with (𝑐) being the final computation.
							''')
		])
	], class_name="mb-3")


def get_losing_strategy_example():
	return dbc.Card([
		dbc.CardHeader("Losing strategy example"),
		dbc.CardBody([
			html.P('''
								After cutting the metal piece we have two tasks after the parallel split node, so we do the bending and milling in parallel.
								Then after milling we have two options to choose from, here we choose fine deposition.
								After bending we have two options to choose from, we choose light polishing with the probability of 0.8. 
								Then, we have two final task to choose from that we select LPLS painting.
								Finally, we have 𝐼 = [115, 11] ∗ 0.2 + [135, 8] ∗ 0.8 = [131, 8.6] > 𝑒𝑖, so by exceeding the 𝑒𝑖 this strategy fails to keep the overall impact below the expected impact.
							''')
		])
	], class_name="mb-3")


def get_winning_strategy_example():
	return dbc.Card([
		dbc.CardHeader("Winning strategy example"),
		dbc.CardBody([
			html.P('''
								After cutting we perform milling in parallel with bending.
								We have two options that comes after milling, we choose fine deposition.
								We have two options to choose after bending, we choose light polishing with the probability of 0.8.
								Then we have two final task to choose from that we select HPHS painting this time.
								Finally we have 𝐼 = [135, 9] ∗ 0.2 + [155, 6] ∗ 0.8 = [151, 6.6] < 𝑒𝑖, so this strategy successfully kept the overall impact below the expected impact.
							''')
		])
	], class_name="mb-3")
