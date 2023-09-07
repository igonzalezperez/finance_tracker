# Use an official Python runtime as a base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /usr/src/app

# Install poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Copy the entire project
COPY . .

# Set the environment variables (adjust as necessary)
ENV DEBUG=True

# Run the application
CMD ["gunicorn", "finance_tracker.wsgi:application", "--bind", "0.0.0.0:8000", "--reload"]
