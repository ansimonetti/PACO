import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.llm import register_api_llm
from src.api.paco import register_paco_api
import uvicorn

# Load .env file from project root
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")

def _get_env_int(name: str, default: int) -> int:
	value = os.getenv(name)
	if not value:
		return default
	try:
		return int(value)
	except ValueError:
		return default


def run(port: int | None = None):
	app = FastAPI()
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"]
	)

	@app.get("/")
	async def get():
		"""
		Root endpoint that returns a welcome message
		Returns:
			str: Welcome message
		"""
		return f"welcome to PACO server"

	register_paco_api(app)
	register_api_llm(app)

	api_host = os.getenv("PACO_API_HOST", "0.0.0.0")
	api_port = port if port is not None else _get_env_int("PACO_API_PORT", 8000)
	uvicorn.run(app, host=api_host, port=api_port)


if __name__ == "__main__":
	run()
