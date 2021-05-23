# Base image.
FROM python:3.9-slim

# Install Pipenv.
RUN python -m pip install pipenv

# Set working directory within the container.
WORKDIR ryan/

# Insert Pipfiles & install dependencies from lockfile.
COPY Pipfile* ./
RUN pipenv sync

# Insert the application.
COPY ryan ryan

# Define build argument & store value as environment variable.
ARG GIT_SHA="Development"
ENV REVISION=$GIT_SHA

# Set container entrypoint ~ this defines what happens when the container starts.
ENTRYPOINT ["pipenv", "run", "ryan"]
