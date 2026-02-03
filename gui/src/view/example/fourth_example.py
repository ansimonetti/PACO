import dash_bootstrap_components as dbc
from dash import html
from gui.src.env import IMPACTS_NAMES
from gui.src.view.example.standard_layout import get_download_layout, get_description, get_render_example

prompt_use_case = '''
We're designing an operational workflow for a marine container terminal that handles incoming vessels, container unloading, storage management, and outbound transportation via train or truck. The process needs to balance operational costs, processing time, and resource utilization while maintaining service quality.
The process begins when a vessel arrives at the terminal. At this initial stage, we face a decision about whether the incoming vessel is a priority vessel or not. This determination typically takes about 5 minutes and influences the entire subsequent workflow.
If the vessel is not designated as priority (which happens 85% of the times), it goes into a vessel lying phase where it waits at anchor or in a holding area. This lying period can take anywhere from 30 minutes to 2 hours, costs around \$200 in harbor fees and fuel, and consumes minimal energy at about 10 kWh. Following this waiting period, we proceed with the standard container unloading operation, which takes between 2 to 4 hours, costs approximately \$800, and uses 150 kWh of energy to operate the cranes and handling equipment.
However, if the vessel is identified as a priority vessel, we immediately proceed with tug vessel operations to bring it directly to the berth. The tugging operation takes 20 to 45 minutes, costs \$500 for the tug service, and consumes 40 kWh. Once berthed, we perform priority container unloading, which is an expedited process taking only 1 to 2 hours but costing \$1200 due to the premium service and additional labor, while consuming 200 kWh for intensive crane operations.
After either unloading path converges, we move to the container transfer phase where containers are moved from the quayside to the storage yard. This transfer operation takes 1 to 3 hours, costs \$400 for the transport equipment and operators, and uses 80 kWh of energy.
Once containers arrive at the storage area, we take a critical decision whether they're in accessible positions for future retrieval. If containers are in accessible positions, they go into short storage, which is a quick holding process taking just 15 to 30 minutes and costing \$50 with minimal 5 kWh energy consumption. If positions are not immediately accessible, containers go into regular storage, which involves more complex stacking and takes 1 to 2 hours, costs \$150, and uses 30 kWh for the additional handling.
After the storage phase is completed, the process reaches its first parallel gateway. At this point, the workflow splits into two parallel branches that are executed simultaneously. The purpose of this parallel gateway is to retrieve and prepare different container categories at the same time in order to reduce total processing time.
In the first parallel branch, the system focuses on big container retrieval. The process begins by locating the big containers, which takes between 30 minutes and 1 hour, costs \$100, and consumes 20 kWh. There is a 15% probability that the big containers cannot be found in their expected positions. If the containers are successfully located, the Rail Mounted Gantry (RMG) crane is moved to the container location. This crane movement takes 15 to 30 minutes, costs \$80, and consumes 25 kWh. If the containers are not successfully located, administration is notified, which takes 10 to 20 minutes and costs \$30. A new container position is then established, taking an additional 20 to 40 minutes at a cost of \$50, after which the process continues.
Once the RMG crane is positioned, containers are loaded using the crane. This loading operation takes between 45 minutes and 1.5 hours, costs $200, and consumes 50 kWh. After loading, a decision is made regarding whether container consolidation is required. This evaluation takes approximately 10 minutes. If consolidation is required, container consolidation is performed, taking 30 to 60 minutes, costing \$150, and consuming 35 kWh, after which the containers proceed to pickup. If consolidation is not required, the process skips directly to pickup. Pickup takes 45 to 60 minutes, costs \$70, and consumes 20 kWh. After pickup, the containers are moved within the terminal, a process that takes 20 to 45 minutes, costs \$100, and consumes 30 kWh.
Simultaneously, in the second parallel branch, the system handles small container retrieval. This branch starts by locating small containers, which takes 20 to 40 minutes, costs \$80, and consumes 15 kWh. There is a 20\% probability that the small containers cannot be located initially. If the containers are successfully located, a trailer is moved to the container site. This movement takes 10 to 25 minutes, costs \$60, and consumes 15 kWh. If the containers cannot be located, administration is notified (10 to 20 minutes at \$30), a new container position is established (15 to 30 minutes at \$40), and then the trailer is moved to the site.
Once the trailer is positioned, we have to pickup them that takes 15 to 30 minutes, costs \$50, and consumes 10 kWh. After the pickup, the small containers are transported to the outbound area. This transportation takes 30 minutes to 1 hour, costs \$120, and consumes 40 kWh.
After both parallel container retrieval branches are completed, the process synchronizes and continues with outbound transportation preparation. At this stage, the workflow splits again into two parallel tracks: train loading and truck loading.
At this point, the process splits into two parallel tracks for outbound transportation—one for train loading and one for truck loading. Both tracks begin with availability checks happening simultaneously.
On the train track, we check train availability, which takes 5 to 15 minutes and costs \$20. Based on the schedule and capacity, there's about a 70\% probability that train loading is available. If a train is available, we proceed with train loading, which takes 1 to 2 hours, costs \$600, and uses 100 kWh for the loading equipment. If no train is available, we must reschedule the loading operation, which takes 30 to 60 minutes and costs \$80 in administrative overhead.
Simultaneously on the truck track, we check truck availability, taking 5 to 10 minutes at \$15. There's approximately an 80\% probability that truck loading is available. If trucks are available, we load them in an operation taking 30 minutes to 1 hour, costing \$300, and using 50 kWh. If trucks aren't available, we reschedule this loading as well, taking 20 to 40 minutes and costing \$60.
Both outbound paths eventually converge, and we perform a final checkout operation where we complete documentation, verify loads, and authorize departure. This checkout takes 15 to 30 minutes, costs \$50, and uses 10 kWh for the gate systems and documentation processing.
Our operational constraints are fairly strict: we have a maximum budget of \$5000 per vessel operation to remain profitable, we cannot exceed 12 hours of total processing time to maintain berth efficiency and meet schedule commitments, and we're limited to 800 kWh of total energy consumption due to our power supply capacity and environmental commitments. The goal is to find the optimal strategy for the two main decision points—whether to perform container consolidation and how to handle the priority vessel routing—that minimizes our expected total operational cost while ensuring we stay within all three resource bounds, accounting for the various probabilistic outcomes in container location success rates and transportation availability.
'''
def get_fourth_example(id, bpmn, bpmn_dot, example_key=None):
	return dbc.Card([
		dbc.CardHeader("Use case BPMN+CPI"),
		dbc.CardBody([
			dbc.Container([
				dbc.Row([
					dbc.Col([
						html.Div([
							get_description(bpmn, '''The BPMN diagram (shown in figure) represents a container terminal harbor process used as a use case in the tool paper. 
							It models vessel unloading operations, container handling with different equipment (MRG for large containers, trailers for small ones), 
							storage decisions, and final transportation via train or truck.''', impacts=True)
						], style={'width': '100%', 'textAlign': 'left'}, className="mb-3"),
						html.Div([
							html.H5("Use Case Description", className="mb-2"),
							html.P([
								"This is the complete use case description used in the tool paper. This prompt was used to automatically generate the BPMN diagram shown below. ",
								"The process has been inspired/expanded by the use case in Termini, M.G., Palumbo, F., Vaglini, G., Ferro, E., Celandroni, N., La Rosa, D.: ",
								"Evaluating the impact of smart technologies on harbor's logistics via BPMN modeling and simulation. ",
								"Information Technology and Management 18(3), 223–239 (2017). ",
								html.A("Read the paper", href="https://dl.acm.org/doi/abs/10.1007/s10799-016-0266-4", target="_blank", className="text-primary")
							], className="text-muted mb-2"),
							html.Div(prompt_use_case, style={
								'maxHeight': '400px',
								'overflowY': 'auto',
								'padding': '15px',
								'backgroundColor': '#f8f9fa',
								'borderRadius': '5px',
								'fontSize': '0.9rem',
								'whiteSpace': 'pre-wrap'
							})
						], className="mb-3"),
						get_download_layout(id + "-download",
											f'''Now it's your turn!
								Download the BPMN JSON file and try to find a winning strategy that respects the expected impact bounds [3144.8, 582.07],
								respectively for [{', '.join(bpmn[IMPACTS_NAMES])}].
							''',
						example_key=example_key)
					], width=4),
					dbc.Col(get_render_example(bpmn_dot, id, zoom_min=1.0, zoom_max=5.0), width=8)
				], class_name="mb-4")
			], fluid=True)
		])])


