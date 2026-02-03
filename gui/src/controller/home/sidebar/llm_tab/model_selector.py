from dash import Input, Output, State

from gui.src.env import LLM_DEFAULT_MODEL_BY_PROVIDER, LLM_MODEL_OPTIONS_BY_PROVIDER


def register_llm_model_selector_callbacks(callback):
	@callback(
		Output("llm-model", "options"),
		Output("llm-model", "value"),
		Output("llm-api-key-container", "style"),
		Output("llm-model-custom", "value"),
		Input("llm-provider", "value"),
		State("llm-model", "value"),
		prevent_initial_call=False,
	)
	def update_llm_models(provider, current_model):
		provider = provider or "lmstudio"
		options = LLM_MODEL_OPTIONS_BY_PROVIDER.get(provider, [])
		option_values = [option["value"] for option in options]
		default_model = LLM_DEFAULT_MODEL_BY_PROVIDER.get(provider)
		if current_model in option_values:
			value = current_model
		else:
			value = default_model or (option_values[0] if option_values else None)

		api_key_style = {"display": "none"} if provider == "lmstudio" else {"display": "block"}
		return options, value, api_key_style, ""
