from .db import check_api_key
from flask import Flask, request, jsonify, render_template
import flask
import shap
import pickle
from werkzeug.exceptions import HTTPException
import os
from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, BooleanField, HiddenField, SelectField, SubmitField
from wtforms.validators import InputRequired, NumberRange
import requests
from flask_wtf.csrf import CSRFProtect

# REST API-friendly exception class
class CustomException(HTTPException):
    code = 400  # HTTP status code for the exception

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.code = status_code
        self.payload = payload

    def get_response(self, environ=None):
        response = dict(self.payload or ())
        response['message'] = self.message
        response['status_code'] = self.code
        return jsonify(response), self.code

class InputForm(FlaskForm):
    # features: 'cp', 'ca', 'thal', 'oldpeak', 'thalach', 'exang', 'age', 'slope', 'sex'
    ANGINA_CHOICES = [(None, 'Unknown'), (0, 'No'), (1, 'Yes')]
    GENDER_CHOICES = [(None, 'Unknown'), (0, 'Female'), (1, 'Male')]

    cp = IntegerField('Chest pain type (0-3)', validators=[NumberRange(min=0, max=3)])
    ca = IntegerField('Number of major vessels (0-3)', validators=[NumberRange(min=0, max=3)])
    thal = IntegerField('Heart defect type (1-3)', validators=[NumberRange(min=1, max=3)])
    oldpeak = FloatField('ST depression induced by exercise', validators=[NumberRange(min=0)])
    thalach = IntegerField('Maximum heart rate achieved', validators=[NumberRange(min=1)])
    exang = SelectField('Exercise induced angina', choices=ANGINA_CHOICES)
    age = IntegerField('Age', validators=[NumberRange(min=1,max=150)])
    slope = IntegerField('Slope of peak ST segment', validators=[NumberRange(min=0)])
    sex = SelectField('Sex', choices=GENDER_CHOICES)

    submit = SubmitField('Submit')

app = Flask(__name__)

# app.config['SECRET_KEY'] = os.environ["SECRET_KEY"]  # replace with a strong secret key
app.config['SECRET_KEY'] = 'your_secret_key_here'
csrf = CSRFProtect(app)

# register error handler
@app.errorhandler(CustomException)
def handle_custom_exception(error):
    return error.get_response()

# load the trained model and SHAP explainer
model_path = os.path.join(os.path.dirname(__file__), "data/gbt_model.pkl")
with open(model_path, "rb") as model_file:
    model = pickle.load(model_file)

explainer = shap.Explainer(model)

def is_single_list(l):
    return isinstance(l, list) and all(not isinstance(item, list) for item in l)

# define a decorator for API key authentication
def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("Authorization")

        if check_api_key(api_key):
            return view_function(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401

    return decorated_function

@csrf.exempt
@app.route("/predict", methods=["POST"])
@require_api_key
def predict():
    data = request.json
    features = data["features"]
    features_names = data["features_names"]

    # check if inputs are single lists
    if not is_single_list(features):
        raise CustomException("Invalid request: 'features' is not a single list.")
    
    if not is_single_list(features_names):
        raise CustomException("Invalid request: 'features_names' is not a single list.")

    if len(features) != len(features_names):
        raise CustomException(f"Invalid request: features {len(features)} and features names lists' length {len(features_names)} do not match.")
    
    if model.n_features_in_ != len(features):
        raise CustomException(f"Invalid request: features {len(features)} and model's features length ({model.n_features_in_}) do not match.")
    
    # convert features to a pandas DataFrame
    import pandas as pd
    input_df = pd.DataFrame({features_names[i]:[features[i]] for i in range(len(features))})

    # calculate SHAP values for the input data
    shap_values = explainer(input_df.iloc[0])
    shap_values_list = shap_values.values.tolist()

    # perform prediction
    prediction = int(model.predict(input_df)[0])

    # get prediction confidence
    confidence = max(model.predict_proba(input_df)[0])

    return jsonify({"prediction": prediction, 
                    "confidence": confidence,
                    "shap_values": shap_values_list})

@app.route("/predict_http", methods=["POST"])
def predict_http():
    # get the values from the HTTP request
    features = [request.form.get("cp", default=None, type=int),
        request.form.get("ca", default=None, type=int),
        request.form.get("thal", default=None, type=int),
        request.form.get("oldpeak", default=None, type=float),
        request.form.get("thalach", default=None, type=int),
        request.form.get("exang", default=None, type=int),
        request.form.get("age", default=None, type=int),
        request.form.get("slope", default=None, type=float),
        request.form.get("sex", default=None, type=int) ]

    features_names = [
                'cp',
                'ca',
                'thal',
                'oldpeak',
                'thalach',
                'exang',
                'age',
                'slope',
                'sex'
                ]

    # check if inputs are single lists
    if not is_single_list(features):
        raise CustomException("Invalid request: 'features' is not a single list.")
    
    if not is_single_list(features_names):
        raise CustomException("Invalid request: 'features_names' is not a single list.")

    if len(features) != len(features_names):
        raise CustomException(f"Invalid request: features length ({len(features)}) and features names lists' length {len(features_names)} do not match.")
    
    if model.n_features_in_ != len(features):
        raise CustomException(f"Invalid request: features {len(features)} and model's features length ({model.n_features_in_}) do not match.")
    
    # convert features to a pandas DataFrame
    import pandas as pd
    input_df = pd.DataFrame({features_names[i]: [features[i]] for i in range(len(features))})

    # calculate SHAP values for the input data
    shap_values = explainer(input_df.iloc[0])
    shap_values_list = shap_values.values.tolist()

    # perform prediction
    prediction = int(model.predict(input_df)[0])

    # prediction to human-friendly form
    if prediction == 0:
        prediction = "None/low Heart Disease Risk"
    else:
        prediction = "High Heart Disease Risk"

    # shap to human-friendly form
    abs_shap_values = [abs(x) for x in shap_values_list]
    shap_total = sum(abs_shap_values)
    shap_list_human = [None]*len(shap_values_list)

    for i,s in enumerate(shap_values_list):
        sign = "+"
        if s < 0:
            sign = "-"

        shap_list_human[i] = f"{round(100*abs(s)/shap_total,1)}% ({sign})"

    # sort by importance
    features_names_full = [
        'Chest pain type',
        'Number of major vessels',
        'Heart defect type',
        'ST depression induced by exercise',
        'Maximum heart rate achieved',
        'Exercise induced angina',
        'Age',
        'Slope of peak ST segment',
        'Sex'
        ]   
    
    sorted_shap_pairs = sorted(
        zip(abs_shap_values, shap_list_human, features_names_full),
        key=lambda x: x[0],
        reverse=True
    )
    
    _,shap_list_human,features_names_full = zip(*sorted_shap_pairs)

    # get prediction confidence
    confidence = max(model.predict_proba(input_df)[0])

    # shap values to dict
    
    shap_values_dict = {}
    for i in range(len(features_names_full)):
        shap_values_dict[features_names_full[i]] = shap_list_human[i]

    # create an HTTP-friendly response
    response = {
        "prediction": prediction,
        "confidence": round(confidence * 100, 1),  # convert confidence to percentage
        "shap_values": shap_values_dict
    }

    return render_template("results.html", response=response)
    # return jsonify(response)

@app.route("/", methods=["GET"])
def home():
    form = InputForm()

    if request.method == 'POST' and form.validate_on_submit():
        data = {
            'features': [
                form.cp.data,
                form.ca.data,
                form.thal.data,
                form.oldpeak.data,
                form.thalach.data,
                form.exang.data,
                form.age.data,
                form.slope.data,
                form.sex.data
            ]
        }

        # make a POST request to /predict_http
        url = 'http://localhost:5000/predict_http'

        response = requests.post(url, data=data)

        if response.status_code == 200:
            # if the request is successful, parse and display the response
            prediction_data = response.json()
            prediction = prediction_data['prediction']
            confidence = prediction_data['confidence']
            shap_values = prediction_data['shap_values']
            return render_template("index.html", form=form, prediction_result={"prediction": prediction, "confidence": confidence, "shap_values": shap_values})
        else:
            # handle the case where the /predict request fails
            raise CustomException("Error: Unable to make prediction")
    
    return render_template("index.html", form=form, prediction_result=None)