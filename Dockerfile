FROM python:3-slim as python

FROM python as poetry
RUN pip install poetry==1.6.1
COPY . /app
WORKDIR /app
RUN poetry install --no-interaction --no-ansi -vvv

FROM python as runtime
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=poetry /app /app
EXPOSE 2761

ENTRYPOINT [ "pydiecom" ]
