# Get the python 3.11 image as the base image
From python:3.11

# Set the working directory in the container
WORKDIR /code

# Create the directory for the credentials
RUN mkdir -p /tmp/keys
RUN chmod 777 /tmp/keys  

# Copy the requirements file into the container at /code
COPY ./requirements.txt /code/requirements.txt

# Install the dependencies
# --no-cache-dir to avoid caching the installation, helpful to cache during development
# --upgrade to upgrade the dependencies if they are already installed (## TODO: check if this is necessary)
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the application code into the container at /code/app/
COPY ./app /code/app

# Copy firebase private key json file
COPY ./keys/firebase_private_key.json /tmp/keys/firebase_private_key.json

# Copy the configuration files
COPY ./configs /tmp/configs

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]