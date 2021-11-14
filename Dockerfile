# Builds the Docker container to package the app
# To build this container for a development environment, run the following:
# 
#   docker build -t <tag> --target dev .
#
# For production, run the following:
# 
#   docker build -t <tag> --target prod .

# Init the containter and update it
FROM nikolaik/python-nodejs:python3.8-nodejs17 AS dev
RUN apt -y update && apt -y upgrade && apt clean

# Install pip requirements
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Setup production environment
FROM dev AS prod

COPY . /app

# Install tailwind in production mode
RUN npm ci --only=production
RUN npm run build