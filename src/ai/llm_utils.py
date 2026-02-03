import json
import os
import re
from pathlib import Path

import requests
from langchain_openai import ChatOpenAI
try:
    from langchain_anthropic import ChatAnthropic
except ImportError:  # pragma: no cover - optional dependency
    ChatAnthropic = None
from src.ai.prompt import define_role, examples_bpmn
from src.utils.check_syntax import check_bpmn_syntax

CHAT_MEMORY = {}

# Load instruction files
_AI_DIR = Path(__file__).parent
_LLM_INSTRUCTIONS = None
_DESIGN_TEMPLATE = None

def _load_instruction_files():
    """Load the LLM system instructions and process design template."""
    global _LLM_INSTRUCTIONS, _DESIGN_TEMPLATE
    
    if _LLM_INSTRUCTIONS is None:
        instructions_path = _AI_DIR / "llm_system_instructions.md"
        if instructions_path.exists():
            _LLM_INSTRUCTIONS = instructions_path.read_text(encoding='utf-8')
        else:
            _LLM_INSTRUCTIONS = ""
    
    if _DESIGN_TEMPLATE is None:
        template_path = _AI_DIR / "process_design_template.md"
        if template_path.exists():
            _DESIGN_TEMPLATE = template_path.read_text(encoding='utf-8')
        else:
            _DESIGN_TEMPLATE = ""
    
    return _LLM_INSTRUCTIONS, _DESIGN_TEMPLATE


def _get_env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


LM_STUDIO_API_BASE = (os.getenv("LM_STUDIO_API_BASE") or "http://localhost:1234/v1").strip().rstrip("/")
DEFAULT_LM_STUDIO_MODEL = (os.getenv("LM_STUDIO_MODEL") or "deepseek-r1-distill-llama-8b").strip()
DEFAULT_OPENAI_MODEL = (os.getenv("OPENAI_MODEL") or "gpt-4o-mini").strip()
DEFAULT_ANTHROPIC_MODEL = (os.getenv("ANTHROPIC_MODEL") or "claude-3-5-sonnet-20241022").strip()
DEFAULT_GEMINI_MODEL = (os.getenv("GEMINI_MODEL") or "gemini-2.5-flash-lite").strip()
DEFAULT_OPENROUTER_MODEL = (os.getenv("OPENROUTER_MODEL") or "openai/gpt-4o-mini").strip()
GEMINI_API_BASE = (
    os.getenv("GEMINI_API_BASE") or "https://generativelanguage.googleapis.com/v1beta/models"
).strip().rstrip("/")
GEMINI_TIMEOUT = _get_env_int("GEMINI_TIMEOUT", 180)
OPENROUTER_API_BASE = (os.getenv("OPENROUTER_API_BASE") or "https://openrouter.ai/api/v1").strip().rstrip("/")
OPENROUTER_HTTP_REFERER = (os.getenv("OPENROUTER_HTTP_REFERER") or "").strip()
OPENROUTER_APP_TITLE = (os.getenv("OPENROUTER_APP_TITLE") or "").strip()

PROVIDER_ALIASES = {
    "lmstudio": "lmstudio",
    "lm-studio": "lmstudio",
    "local": "lmstudio",
    "openai": "openai",
    "gpt": "openai",
    "openrouter": "openrouter",
    "open-router": "openrouter",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "gemini": "gemini",
    "google": "gemini",
}


def _normalize_provider(provider: str | None) -> str:
    if not provider:
        return "lmstudio"
    return PROVIDER_ALIASES.get(provider.strip().lower(), provider.strip().lower())


def _resolve_model(provider: str, model: str | None) -> str:
    if model:
        return model.strip()
    if provider == "openai":
        return DEFAULT_OPENAI_MODEL
    if provider == "anthropic":
        return DEFAULT_ANTHROPIC_MODEL
    if provider == "gemini":
        return DEFAULT_GEMINI_MODEL
    if provider == "openrouter":
        return DEFAULT_OPENROUTER_MODEL
    return DEFAULT_LM_STUDIO_MODEL


def _require_user_key(api_key: str | None, provider_label: str) -> str:
    key = (api_key or "").strip()
    if not key:
        raise RuntimeError(f"{provider_label} API key missing. Enter it in the UI.")
    return key


def _get_gemini_api_key(api_key: str | None, model: str | None = None) -> str:
    user_key = (api_key or "").strip()
    
    # If user provided a key, use it (overrides system key)
    if user_key:
        return user_key
    
    # No user key provided - use system key for gemini-2.5-flash-lite/flash only
    if model == "gemini-2.5-flash-lite" or model == "gemini-2.5-flash":
        system_key = os.getenv("GEN_AI_API_KEY", "").strip()
        if system_key:
            return system_key
    
    # No user key and no system key available
    raise RuntimeError("Gemini API key missing. Enter it in the UI.")


def _extract_gemini_text(response_data: dict) -> str:
    candidates = response_data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini response missing candidates.")
    content = candidates[0].get("content", {})
    parts = content.get("parts", [])
    if not parts:
        raise RuntimeError("Gemini response missing content parts.")
    text = parts[0].get("text", "")
    if not text:
        raise RuntimeError("Gemini response missing text.")
    return text


def _invoke_gemini(prompt: str, model: str, api_key: str | None) -> str:
    endpoint = f"{GEMINI_API_BASE}/{model}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7},
    }
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": _get_gemini_api_key(api_key, model),
    }
    response = requests.post(
        endpoint,
        json=payload,
        headers=headers,
        timeout=GEMINI_TIMEOUT,
    )
    response.raise_for_status()
    return _extract_gemini_text(response.json()).strip()


def build_few_shot_prompt(bpmn_dict: dict, message: str) -> str:
    """Build the initial prompt with system instructions, template, and examples."""
    llm_instructions, design_template = _load_instruction_files()
    
    examples = "\n".join([
        f"User: {ex['input'].strip()}\nTranslation: {ex['answer'].strip()}"
        for ex in examples_bpmn
    ])

    prompt_parts = []
    
    # Part 1: System Instructions (comprehensive guide)
    if llm_instructions:
        prompt_parts.append("=== SYSTEM INSTRUCTIONS ===")
        prompt_parts.append(llm_instructions)
        prompt_parts.append("\n")
    
    # Part 2: Process Design Template (structured approach)
    if design_template:
        prompt_parts.append("=== PROCESS DESIGN TEMPLATE ===")
        prompt_parts.append("When designing a process from natural language, follow this systematic template:")
        prompt_parts.append(design_template)
        prompt_parts.append("\n")
    
    # Part 3: Legacy role definition (backward compatibility)
    prompt_parts.append("=== CORE INSTRUCTIONS ===")
    prompt_parts.append(define_role)
    prompt_parts.append("\n")
    
    # Part 4: Examples
    prompt_parts.append("=== EXAMPLES ===")
    prompt_parts.append(examples)
    prompt_parts.append("\n")
    
    # Part 5: Output format requirements
    prompt_parts.append("=== OUTPUT FORMAT ===")
    prompt_parts.append("You MUST respond with a valid JSON object in this exact format:")
    prompt_parts.append('{ "bpmn": <updated_bpmn_dict>, "message": <explanation> }')
    prompt_parts.append("CRITICAL: Respond ONLY with JSON. No markdown code blocks. No comments. No text outside the JSON structure.")
    prompt_parts.append("\n")
    
    # Part 6: Current task
    prompt_parts.append("=== CURRENT TASK ===")
    prompt_parts.append(f"User Instruction: {message}")
    prompt_parts.append(f"Current BPMN State:\n{json.dumps(bpmn_dict, indent=2)}")
    
    return "\n".join(prompt_parts)


def build_followup_prompt(history: list, message: str, bpmn_dict: dict) -> str:
    """Build follow-up prompt with conversation history and current BPMN state."""
    llm_instructions, _ = _load_instruction_files()
    
    prompt_parts = []
    
    # Include condensed system instructions for context
    prompt_parts.append("=== SYSTEM CONTEXT ===")
    prompt_parts.append("You are a BPMN+CPI process design assistant. Key syntax:")
    prompt_parts.append("- Sequential: (A, B)  |  Parallel: (A || B)")
    prompt_parts.append("- Choice: (A /[C1] B) with delays  |  Nature: (A ^[N1] B) with probabilities")
    prompt_parts.append("- Loop: <[L1] Task> with loop_probability and loop_round")
    prompt_parts.append("- All impacts must be positive. Durations: [min, max] where min ≤ max")
    prompt_parts.append("")
    
    # Include conversation history
    prompt_parts.append("=== CONVERSATION HISTORY ===")
    for msg in history:
        prompt_parts.append(f"User: {msg['user']}")
        prompt_parts.append(f"Assistant: {msg['assistant']['message']}")
        if 'bpmn' in msg['assistant']:
            prompt_parts.append(f"Generated Expression: {msg['assistant']['bpmn'].get('expression', 'N/A')}")
    prompt_parts.append("")
    
    # Current state and new request
    prompt_parts.append("=== CURRENT STATE ===")
    prompt_parts.append(f"Current BPMN:\n{json.dumps(bpmn_dict, indent=2)}")
    prompt_parts.append("")
    prompt_parts.append("=== NEW REQUEST ===")
    prompt_parts.append(f"User: {message}")
    prompt_parts.append("")
    prompt_parts.append("=== OUTPUT FORMAT ===")
    prompt_parts.append("Respond with valid JSON only:")
    prompt_parts.append('{ "bpmn": <updated_bpmn_dict>, "message": <explanation> }')
    
    return "\n".join(prompt_parts)


def run_llm_on_bpmn(
    bpmn_dict: dict,
    message: str,
    session_id: str,
    max_attempts: int,
    provider: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> dict:
    provider = _normalize_provider(provider)
    model = _resolve_model(provider, model)

    if provider == "lmstudio":
        try:
            response = requests.get(f"{LM_STUDIO_API_BASE}/models", timeout=max_attempts)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return {
                "bpmn": bpmn_dict,
                "message": "I'm offline"
            }

    if session_id not in CHAT_MEMORY:
        CHAT_MEMORY[session_id] = []

    is_first_message = len(CHAT_MEMORY[session_id]) == 0
    prompt = build_few_shot_prompt(bpmn_dict, message) if is_first_message else build_followup_prompt(CHAT_MEMORY[session_id], message, bpmn_dict)

    llm = None
    if provider == "lmstudio":
        llm = ChatOpenAI(
            openai_api_base=LM_STUDIO_API_BASE,
            openai_api_key=os.getenv("LM_STUDIO_API_KEY", "lm-studio"),
            model=model,
            temperature=0.7,
            verbose=False
        )
    elif provider == "openai":
        user_key = _require_user_key(api_key, "OpenAI")
        llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            verbose=False,
            api_key=user_key,
        )
    elif provider == "anthropic":
        if ChatAnthropic is None:
            raise RuntimeError("langchain-anthropic is not installed.")
        user_key = _require_user_key(api_key, "Anthropic")
        os.environ["ANTHROPIC_API_KEY"] = user_key
        try:
            llm = ChatAnthropic(
                model=model,
                temperature=0.7,
                api_key=user_key,
            )
        except TypeError:
            llm = ChatAnthropic(
                model=model,
                temperature=0.7,
            )
    elif provider == "openrouter":
        user_key = _require_user_key(api_key, "OpenRouter")
        headers = {}
        if OPENROUTER_HTTP_REFERER:
            headers["HTTP-Referer"] = OPENROUTER_HTTP_REFERER
        if OPENROUTER_APP_TITLE:
            headers["X-Title"] = OPENROUTER_APP_TITLE
        llm = ChatOpenAI(
            base_url=OPENROUTER_API_BASE,
            api_key=user_key,
            model=model,
            temperature=0.7,
            verbose=False,
            default_headers=headers or None,
        )
    elif provider != "gemini":
        raise RuntimeError(f"Unsupported LLM provider: {provider}")

    for attempt in range(max_attempts):
        try:
            if provider == "gemini":
                text = _invoke_gemini(prompt, model, api_key)
            else:
                response = llm.invoke(prompt)
                text = response.content.strip()

            # Clean known formatting problems
            text = re.sub(r"```json|```", "", text)
            text = re.sub(r"(const|let|var)\s+\w+\s*=\s*", "", text)
            text = re.sub(r"^[^{]*", "", text)
            text = re.sub(r"[^}]*$", "", text)

            parsed = json.loads(text)

            if "bpmn" not in parsed or "message" not in parsed:
                raise ValueError("Missing keys in LLM response")

            check_bpmn_syntax(parsed["bpmn"])

            CHAT_MEMORY[session_id].append({
                "user": message,
                "assistant": parsed
            })

            return parsed

        except Exception as e:
            if attempt == max_attempts - 1:
                raise RuntimeError(f"LLM failed to produce valid BPMN after {max_attempts} attempts: {e}")
            continue
