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

# Install necessary libraries (omit tailwind install for speed)
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Run app
CMD ["python3", "server.py"]

# Setup production environment
FROM nikolaik/python-nodejs:python3.8-nodejs17 AS prod
RUN apt -y update && apt -y upgrade && apt clean

# Bring in project files
COPY . /app
WORKDIR /app

# Install necessary libraries (install tailwind in production mode)
RUN pip install -r requirements.txt
RUN npm ci --only=production
RUN npm run build