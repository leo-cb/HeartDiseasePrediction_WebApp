# HeartDiseasePrediction_WebApp
Flask app that predicts the risk of heart disease based on a Gradient-boosted Tree ML model, and shows the confidence in the prediction as well as the factors behind the prediction (explainability).

# Installation
To install and run this web app, follow these steps:

1. Clone this repository to your local machine:
   ```shell
   git clone https://github.com/leo-cb/HeartDiseasePrediction_WebApp.git
2. Start the docker-compose service:
   ```shell
   docker-compose up -d

# Usage
Once the docker-compose container is running, you can access the application by opening a web browser and navigating to http://localhost:5000. From there, you can enter patient data and receive a prediction of their likelihood of developing heart disease, as well as the confidence in that prediction and the each factor weight behind it.


# Heart Disease Prediction Web App

Flask app that predicts the risk of heart disease based on a Gradient-boosted Tree ML model, and shows the confidence in the prediction as well as the factors behind the prediction (explainability).

## Getting Started

### Dependencies

**Install Docker:**

**Linux:**
To install Docker on Linux, follow the instructions for your specific distribution on the [Docker website](https://docs.docker.com/engine/install/).

**Windows:**
If you're using Windows, you can install Docker Desktop by downloading it from the [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) page.

**Install Docker Compose:**

**Linux:**
To install Docker Compose on Linux, follow the instructions on the [Docker Compose website](https://docs.docker.com/compose/install/).

**Windows:**
Docker Desktop for Windows includes Docker Compose. You don't need to install it separately.

### Installing

To install this application, follow these steps:

1. Clone this repository to your local machine:
   ```shell
   git clone https://github.com/leo-cb/HeartDiseasePrediction_WebApp.git
2. Start the docker-compose service:
   ```shell
   docker-compose up -d

### Executing program

Once the docker-compose container is running, you can access the application by opening a web browser and navigating to http://localhost:5000. From there, you can enter patient data and receive a prediction of their likelihood of developing heart disease, as well as the confidence in that prediction and the each factor weight behind it.

## Description

1. Loads the GBT model from a pickle file.
2. 
