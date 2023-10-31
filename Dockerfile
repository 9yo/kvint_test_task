# Use an official Python runtime as a base image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY pyproject.toml /app/pyproject.toml

# Install poetry
RUN pip install poetry

# Install the dependencies using poetry
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev
