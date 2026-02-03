from dash import dcc, html

from gui.src.env import (
    LLM_DEFAULT_MODEL_BY_PROVIDER,
    LLM_DEFAULT_PROVIDER,
    LLM_MODEL_OPTIONS_BY_PROVIDER,
    LLM_PROVIDER_OPTIONS,
)


def get_model_selector():
    return html.Div(
        [
            html.Div(
                [
                    html.P(
                        [
                            html.Strong("Note: "),
                            "The system currently includes a working ",
                            html.Strong("Gemini 2.5-flash-lite or Gemini 2.5-flash"),
                            " model. To use other models, please add your API key and select your preferred option.",
                            html.Br(),
                            html.Strong("Important: the model may make mistakes; use with caution."),
                        ],
                        style={
                            "backgroundColor": "#e3f2fd",
                            "padding": "10px",
                            "borderRadius": "4px",
                            "border": "1px solid #90caf9",
                            "marginBottom": "12px",
                            "fontSize": "0.9em",
                            "color": "#1565c0",
                        },
                    ),
                ],
            ),
            html.Label(
                "Provider",
                htmlFor="llm-provider",
                style={"display": "block", "marginBottom": "6px"},
            ),
            dcc.Dropdown(
                id="llm-provider",
                options=LLM_PROVIDER_OPTIONS,
                value=LLM_DEFAULT_PROVIDER,
                clearable=False,
                searchable=True,
                persistence=True,
                persistence_type="session",
            ),
            html.Label(
                "Model",
                htmlFor="llm-model",
                style={"display": "block", "marginTop": "10px", "marginBottom": "6px"},
            ),
            dcc.Dropdown(
                id="llm-model",
                options=LLM_MODEL_OPTIONS_BY_PROVIDER[LLM_DEFAULT_PROVIDER],
                value=LLM_DEFAULT_MODEL_BY_PROVIDER[LLM_DEFAULT_PROVIDER],
                clearable=False,
                searchable=True,
                persistence=True,
                persistence_type="session",
            ),
            html.Label(
                "Custom model",
                htmlFor="llm-model-custom",
                style={"display": "block", "marginTop": "10px", "marginBottom": "6px"},
            ),
            dcc.Input(
                id="llm-model-custom",
                type="text",
                placeholder="Optional model override (e.g. llama3.1, openai/gpt-4o-mini)",
                style={
                    "width": "100%",
                    "padding": "6px 8px",
                    "borderRadius": "4px",
                    "border": "1px solid #ccc",
                },
            ),
            html.Div(
                [
                    html.Label(
                        "API key",
                        htmlFor="llm-api-key",
                        style={"display": "block", "marginTop": "10px", "marginBottom": "6px"},
                    ),
                    dcc.Input(
                        id="llm-api-key",
                        type="password",
                        placeholder="Required (provided for Gemini 2.5-flash-lite or Gemini 2.5-flash only, use your own key for others)",
                        style={
                            "width": "100%",
                            "padding": "6px 8px",
                            "borderRadius": "4px",
                            "border": "1px solid #ccc",
                        },
                    ),
                ],
                id="llm-api-key-container",
                style={"display": "none"},
            ),
        ],
        style={"marginBottom": "12px"},
    )
