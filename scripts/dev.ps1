# Dev server for realtime-caption-assist
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
