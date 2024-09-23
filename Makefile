run-app-local:
	uvicorn app.__main__:app --reload --host 127.0.0.1 --port 8000 --log-level error

run-app:
	uvicorn app.__main__:app --log-level error --host 0.0.0.0 --port 80
