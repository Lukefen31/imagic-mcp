FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "mcp>=1.2,<2"
COPY server.py tools.json ./
# Introspection-only stand-in: lists the real imagic tools; calls report that
# the imagic desktop app is required. See README.
ENTRYPOINT ["python", "/app/server.py"]
