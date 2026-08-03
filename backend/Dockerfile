# --- Base image ---
# Slim variant: full Python 3.11, but without extra OS packages/docs that a
# typical dev machine has (compilers, man pages, etc.) - smaller image,
# faster pulls, smaller attack surface. Matches the Python version already
# required in README ("Local setup" -> Python 3.11).
FROM python:3.11-slim

# --- Working directory ---
# All following instructions (COPY, RUN, CMD) run relative to /app inside
# the container. Creates the directory if it doesn't exist yet.
WORKDIR /app

# --- Install dependencies first, app code second (this order matters) ---
# Copy ONLY requirements.txt at this point - not the whole app yet.
# Docker caches each instruction as a "layer". As long as requirements.txt
# doesn't change, Docker reuses the cached "pip install" layer on every
# rebuild, instead of re-downloading every package each time you change a
# single line of application code.
COPY requirements.txt .

# --no-cache-dir: don't keep pip's own download cache inside the image -
# we're not going to run pip again in this container, so keeping it would
# only make the image bigger for no benefit.
RUN pip install --no-cache-dir -r requirements.txt

# --- Now copy the rest of the application code ---
# This layer changes on almost every commit, so it's placed AFTER the
# dependency installation layer above, to keep using the cached, unchanged
# dependency layer whenever only application code changes.
COPY . .

# --- Document the port the app listens on ---
# EXPOSE does not actually publish the port to the host by itself - it's
# metadata/documentation for anyone reading the Dockerfile or inspecting
# the image. The actual host<->container port mapping happens with
# `docker run -p`, shown in the README.
EXPOSE 8000

# --- Start command ---
# Runs when the container starts (not at build time, unlike RUN above).
# --host 0.0.0.0 is required: FastAPI/uvicorn defaults to 127.0.0.1, which
# only accepts connections from inside the container itself. Binding to
# 0.0.0.0 means "accept connections from any network interface", which is
# what allows the port mapping (-p 8000:8000) to actually reach the app
# from outside the container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]