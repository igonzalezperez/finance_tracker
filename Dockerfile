# BASE
FROM python:3.11-slim AS base

# Update the package lists from the repositories
RUN apt-get update \
    # Install the 'gcc' package without its recommended packages
    && apt-get -y install --no-install-recommends gcc \
    # Clean up the package cache to reduce image size
    && apt-get clean \
    # Remove the downloaded package lists to further reduce image size
    && rm -rf /var/lib/apt/lists/*

# DEVELOPMENT
FROM base AS development
ENV \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/.venv 
ENV \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=1.6.1

# install poetry 
RUN pip install "poetry==$POETRY_VERSION"
# copy requirements
COPY poetry.lock pyproject.toml ./

# add venv to path 
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python packages
RUN python -m venv "$VIRTUAL_ENV" \
    && . "$VIRTUAL_ENV"/bin/activate \
    && poetry install --no-root
# Run Application
CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


# BUILDER
FROM development AS builder
WORKDIR /app
COPY . . 
RUN poetry install --without dev
ENV DJANGO_SECRET_KEY=WQIOEUFJHWQILUVH
# Collect static files
RUN python manage.py collectstatic --noinput
# export build
RUN poetry build --format wheel


# PRODUCTION
FROM builder AS production
WORKDIR /app
# export build
# COPY --from=builder /app/dist/*.whl ./
# RUN pip install ./*.whl
# RUN rm ./*.whl

# Run Application
COPY . .
RUN poetry install --no-dev
CMD ["gunicorn", "finance_tracker.wsgi:application", "--bind", "0.0.0.0:8000"]
