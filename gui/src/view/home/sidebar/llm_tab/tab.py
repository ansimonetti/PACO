from dash import dcc, html
import dash_bootstrap_components as dbc

from gui.src.view.home.sidebar.llm_tab.header import get_header
from gui.src.view.home.sidebar.llm_tab.input_bar import get_input_bar
from gui.src.view.home.sidebar.llm_tab.model_selector import get_model_selector


def get_llm_tab():
	return dcc.Tab(
		label='Copilot',
		value='tab-llm',
		style={'flex': 1, 'textAlign': 'center'},
		children=[
			html.Div([
				get_header(),
				get_model_selector(),

				html.Div(
					id='chat-output',
					style={
						'height': '380px',
						'overflowY': 'auto',
						'backgroundColor': '#f9f9f9',
						'padding': '10px',
						'border': '1px solid #ccc',
						'borderRadius': '10px',
						'display': 'flex',
						'flexDirection': 'column',
						'gap': '10px',
						'textAlign': 'left'
					}
				),

				get_input_bar(),

				dbc.Modal(
					[
						dbc.ModalHeader(dbc.ModalTitle("Proposal Preview")),
						dbc.ModalBody(
							html.Img(
								id='proposal-preview-img',
								style={
									'width': '100%',
									'height': 'auto',
									'display': 'block'
								}
							),
							style={'padding': '0.5rem'}
						),
						dbc.ModalFooter(
							dbc.Button("Close", id="proposal-preview-close", color="secondary")
						),
					],
					id='proposal-preview-modal',
					is_open=False,
					size="xl",
					fullscreen=True,
					scrollable=True
				),

				html.Div(id='dummy-output', style={'display': 'none'}),
			], style={'padding': '20px'})
		]
	)
