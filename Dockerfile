# Use the official Python image as a base image
FROM python:3.11.4

# Set the working directory within the container
WORKDIR /app

# Import the public key used by the package management system
RUN curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor

# Create a list file for MongoDB
RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Reload local package database
RUN apt-get update

# Install libssl (mongodb-org dependency)
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1-1ubuntu2.1~18.04.23_amd64.deb
RUN dpkg -i libssl1.1_1.1.1-1ubuntu2.1~18.04.23_amd64.deb

# Install the MongoDB version specified earlier
RUN apt-get install -y mongodb-org

# Create the default data directory
RUN mkdir -p /data/db

# Copy files to container
COPY . /app
COPY requirements.txt .

# Install the Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for web app
EXPOSE 5000

# production flask server
RUN pip install gunicorn

# run web app
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:5000"]