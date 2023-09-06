# HeartDiseasePrediction_WebApp
Flask app that predicts the risk of heart disease based on a GBT ML model, and shows the confidence in the prediction as well as the factors behind the prediction (explainability).

# Installation
To install and run this web app, follow these steps:

1. Clone this repository to your local machine.
2. Start the docker-compose service
   ```shell
   docker-compose up -d

# Usage
Once the web app is running, you can access it by opening a web browser and navigating to http://localhost:5000. From there, you can enter patient data and receive a prediction of their likelihood of developing heart disease, as well as the confidence in that prediction and the each factor weight behind it.
