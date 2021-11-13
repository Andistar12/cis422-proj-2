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
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# Setup production environment
FROM dev AS prod

# Install tailwind in production mode
RUN pip install -r requirements.txt
RUN npm ci --only=production
RUN npm run build