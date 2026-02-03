from dash import html, dcc
import dash_bootstrap_components as dbc

def get_message(msg, idx):
    content = [html.Div(msg['text'])]
    
    proposal_svg = msg.get('proposal_svg')
    if proposal_svg:
        content.append(dcc.Store(id={'type': 'proposal-preview-data', 'index': idx}, data=proposal_svg))
        content.append(
            html.Div(
                html.Img(
                    src=proposal_svg,
                    style={
                        'width': '100%',
                        'height': 'auto',
                        'display': 'block'
                    }
                ),
                style={
                    'marginTop': '10px',
                    'padding': '6px',
                    'border': '1px solid #d0d0d0',
                    'borderRadius': '8px',
                    'backgroundColor': '#ffffff'
                }
            )
        )
        content.append(
            dbc.Button(
                "Full screen",
                id={'type': 'proposal-preview-btn', 'index': idx},
                color="secondary",
                size="sm",
                style={'marginTop': '6px'}
            )
        )
    
    if msg.get('is_proposal'):
        content.append(html.Div([
            dbc.Button(
                "Accept",
                id={"type": "proposal-action", "action": "accept", "index": "single"},
                color="success",
                size="sm",
                className="me-2",
            ),
            dbc.Button(
                "Reject",
                id={"type": "proposal-action", "action": "reject", "index": "single"},
                color="danger",
                size="sm",
            )
        ], style={'marginTop': '10px'}))

    return html.Div(
        content,
        style={
            'alignSelf': 'flex-end' if msg['type'] == 'user' else 'flex-start',
            'backgroundColor': '#d1e7dd' if msg['type'] == 'user' else '#e2e3e5',
            'padding': '8px 12px',
            'borderRadius': '12px',
            'maxWidth': '75%',
            'marginBottom': '10px'
        }
    )
