FROM python:3.13-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --yes --no-install-recommends bash ca-certificates curl git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/codemeticulous
COPY pyproject.toml README.md ./
COPY codemeticulous ./codemeticulous
COPY schema ./schema
RUN python -m pip install --no-cache-dir .

RUN useradd --create-home --uid 10001 agent \
    && mkdir -p /workspace \
    && chown agent:agent /workspace

USER agent
WORKDIR /workspace
CMD ["sleep", "infinity"]
