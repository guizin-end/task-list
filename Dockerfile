FROM python:3.14-slim
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
COPY . .

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

RUN chmod +x /app/entrypoint.sh
RUN addgroup --system app \
    && adduser --system --ingroup app --home /home/app app \
    && chown -R app:app /app /home/app

USER app

EXPOSE 8000