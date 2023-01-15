FROM python:3.11-alpine

COPY family_budget /app/family_budget

WORKDIR /app

RUN pip install poetry
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN poetry install --only main

EXPOSE 8000

#CMD ["python", "-m", "family_budget"]
ENTRYPOINT ["uvicorn", "family_budget.main:get_app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
