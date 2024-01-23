FROM python:2

# Install required Python packages
RUN pip install faker numpy pytz tzlocal

# Set the working directory
WORKDIR /app

# Copy necessary files
COPY apache-fake-log-gen.py /app/
COPY requirements.txt /app/
COPY LICENSE /app/
COPY output.log /app/

# Set the container name
ARG CONTAINER_NAME="my_fake_log_container"
LABEL container.name=$CONTAINER_NAME

# Set the entry point
ENTRYPOINT ["python", "/app/apache-fake-log-gen.py"]