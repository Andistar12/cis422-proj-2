# Builds the Docker container to package the app
# To build this container for a development environment, run the following:
# 
#   docker build -t <tag> --target dev .
#
# For production, run the following:
# 
#   docker build -t <tag> --target prod .

# Init the containter and update it
FROM python:3.8 AS dev
FROM node:latest
RUN apt -y update && apt -y upgrade && apt install npm -y && apt clean

# Install necessary libraries
COPY package*.json /app
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
RUN npm install
RUN npm ci --only=production
RUN npm run build

# Run app
CMD ["python3", "server.py"]

# Setup production environment
FROM dev AS prod
COPY . /app
