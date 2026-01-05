from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import joblib
import json

from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import abort

# =========================
# APP CONFIG
# =========================
app = Flask(__name__)
app.secret_key = "cle_secrete_session"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = "login_register"
login_manager.init_app(app)

# =========================
# USER MODEL
# =========================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="staff") 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =========================
# LOAD MODELS & METRICS
# =========================
clv_pipeline = joblib.load("clv_pipeline.pkl")
cluster_pipeline = joblib.load("flight_cluster_pipeline.pkl")
plane_cluster_pipeline = joblib.load("cluster_pipeline.pkl")
pipeline = joblib.load("rul_pipeline.pkl")
features = joblib.load("features_all.pkl") 
feature_labels = {
    'setting1': 'Operating Setting 1',
    'setting2': 'Operating Setting 2',
    's2': 'Compressor Inlet Temperature',#
    's3': 'Fan Speed',#
    's4': 'Oil Pressure',#
    's6': 'Turbine Temperature',#
    's7': 'Fuel Flow Rate',
    's8': 'Vibration Sensor 1',
    's9': 'Vibration Sensor 2',
    's11': 'Exhaust Gas Temperature',#
    's12': 'Pressure Ratio',#
    's13': 'Throttle Position',
    's14': 'Intake Pressure',
    's15': 'Rotor Speed',
    's17': 'Cooling Airflow',
    's20': 'Oil Temperature',#
    's21': 'Vibration Sensor 3'
}
cluster_description = {
    0: "⚠️ Highly Degraded Engine (Critical – Immediate Maintenance)",
    1: "✅ Normal Operating Condition",
    2: "🟡 Progressive Degradation (Monitor Closely)",
    3: "🔴 Advanced Degradation (High Risk)"
}
print("🔹 Loading Churn pipeline...")
churn_model_package = joblib.load("churn_pipeline.pkl")
churn_pipeline = churn_model_package['pipeline']
churn_transformers = churn_model_package['transformers']
print("✅ Churn pipeline loaded.")



print("🔹 Loading Cluster Activity pipeline...")
cluster_activity_pipeline = joblib.load("cluster_activity_pipeline.pkl")
cluster_activity_info = joblib.load("cluster_activity_info.pkl")
print("✅ Cluster Activity pipeline loaded (k=3).")
with open("metrics.json", "r") as f:
    MODEL_METRICS = json.load(f)


churn_metrics_data = joblib.load("churn_metrics.pkl")
CHURN_METRICS = churn_metrics_data['all_models_comparison']
print("✅ Churn metrics loaded.")

print("✅ All models loaded successfully!")
# =========================
# LOGIN / REGISTER SINGLE PAGE
# =========================
from flask import send_from_directory
import os
@app.route('/assets/<path:filename>')
def custom_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'assets'), filename)
@app.route("/auth", methods=["GET", "POST"])
def login_register():
    error = None

    if request.method == "POST":

        # LOGIN
        if "login-submit" in request.form:
            email = request.form["email"]
            password = request.form["password"]

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                if user.role == "admin":
                    return redirect(url_for("admin"))
                return redirect(url_for("index"))
            error = "Invalid email or password"

        # REGISTER (STAFF ONLY)
        elif "register-submit" in request.form:
            nom = request.form["nom"]
            email = request.form["email"]
            password = generate_password_hash(request.form["password"])

            if User.query.filter_by(email=email).first():
                error = "Email already registered"
            else:
                user = User(
                    nom=nom,
                    email=email,
                    password=password,
                    role="staff"
                )
                db.session.add(user)
                db.session.commit()
                login_user(user)
                return redirect(url_for("index"))

    return render_template("login_register.html", error=error)
# =========================
# LOGOUT
# =========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_register"))

@app.route("/")
@login_required
def index():
    return render_template("index.html")
# =========================
# PREDICTION PAGE (BOTH)
# =========================

@app.route("/predict/rul", methods=["GET", "POST"])
@login_required
def predict_rul():
    prediction = None
    error_msg = None

    if request.method == "POST":
        try:
            # Collect numeric inputs from the form
            input_data = {}
            for f in features:
                value = request.form.get(f, None)
                if value is None or value.strip() == "":
                    raise ValueError(f"Missing input for {feature_labels[f]}")
                

                # Only pass the model features to the pipeline
                input_data = {f: float(request.form[f]) for f in features}
                X = pd.DataFrame([input_data], columns=features)
                prediction = pipeline.predict(X)[0]


        except Exception as e:
            error_msg = str(e)

    return render_template(
        "predict_rul.html",
        features=features,
        feature_labels=feature_labels,
        prediction=prediction,
        error_msg=error_msg
    )

@app.route("/predict/clv", methods=["GET", "POST"])
@login_required
def predict_clv():
    clv = None

    if request.method == "POST":
        X = pd.DataFrame([{
            "Salary": float(request.form["salary"]),
            "Enrollment Month": int(request.form["enroll_month"]),
            "Enrollment Year": int(request.form["enroll_year"]),
            "Education": request.form["education"],
            "Gender": request.form["gender"],
            "Marital Status": request.form["marital"],
            "Loyalty Card": request.form["loyalty_card"]
        }])

        y = clv_pipeline.predict(X)
        clv = float(np.expm1(y[0]))

    return render_template("predict_clv.html", clv=clv)

# ---- CHURN ----
@app.route("/predict/churn", methods=["GET", "POST"])
@login_required
def predict_churn():
    churn = None
    score = None

    if request.method == "POST":
        X = pd.DataFrame([{
            'Total Flights': float(request.form["total_flights"]),
            'Distance': float(request.form["distance"]),
            'Points Accumulated': float(request.form["points_accumulated"]),
            'Points Redeemed': float(request.form["points_redeemed"]),
            'Dollar Cost Points Redeemed': float(request.form["dollar_cost"]),
            'Enrollment Year': int(request.form["enrollment_year"]),
            'Active_Years': int(request.form["active_years"]),
            'CLV': float(request.form["clv"]),
            'Month': int(request.form.get("month", 1)),
            'Education_encoded': int(request.form["education_encoded"]),
            'Gender_Female': int(request.form["gender_female"]),
            'Gender_Male': int(request.form["gender_male"]),
            'Marital Status_Single': int(request.form["marital_single"]),
            'Enrollment Type_Standard': int(request.form["enrollment_standard"]),
            'Enrollment Type_2018 Promotion': int(request.form["enrollment_promo"])
        }])

        raw = churn_pipeline.predict_proba(X)[:, 1][0]
        churn_threshold = churn_model_package.get("threshold", 0.5)
        score = min(raw * 15, 1.0)
        churn = int(score >= churn_threshold)

    return render_template("predict_churn.html", churn=churn, score=score)
@app.route("/predict/plane-cluster", methods=["GET", "POST"])
@login_required
def predict_plane_cluster():
    rul_prediction = None
    cluster = None
    description = None
    error_msg = None

    if request.method == "POST":
        try:
            # 1️⃣ Collect raw user inputs and convert to float
            input_data = {}
            for f in features:
                value = request.form.get(f)
                if value is None or value.strip() == "":
                    raise ValueError(f"Missing value for {feature_labels[f]}")
                input_data[f] = float(value)

            # 2️⃣ Create DataFrame with correct feature order
            X = pd.DataFrame([input_data], columns=features)

            # 3️⃣ Make predictions
            rul_prediction = float(pipeline.predict(X)[0])
            cluster = int(plane_cluster_pipeline.predict(X)[0])
            description = cluster_description.get(cluster, "Unknown engine state")

        except Exception as e:
            error_msg = str(e)
            print("Error in plane cluster prediction:", error_msg)  # 🔹 Print error to console

    # 4️⃣ Render template and pass error_msg to show in HTML
    return render_template(
        "predict_plane_cluster.html",
        features=features,
        feature_labels=feature_labels,
        rul_prediction=rul_prediction,
        cluster=cluster,
        description=description,
        error_msg=error_msg
    )

@app.route("/predict/flight-cluster", methods=["GET", "POST"])
@login_required
def predict_flight_cluster():
    cluster = None

    if request.method == "POST":
        X = pd.DataFrame([{
            "Airline": request.form["airline"],
            "Flight": int(request.form["flight"]),
            "AirportFrom": request.form["airport_from"],
            "AirportTo": request.form["airport_to"],
            "DayOfWeek": int(request.form["day"]),
            "Time": int(request.form["time"]),
            "Length": int(request.form["length"]),
            "Delay": int(request.form["delay"])
        }])

        cluster = int(cluster_pipeline.predict(X)[0])

    return render_template("predict_flight_cluster.html", cluster_flight=cluster)

# ---- CUSTOMER CLUSTER ----
@app.route("/predict/customer_cluster", methods=["GET", "POST"])
@login_required
def predict_customer_cluster():
    cluster = None
    name = None
    description = None

    if request.method == "POST":
        X = pd.DataFrame([{
            'Month': 6,
            'Total Flights': float(request.form["total_flights"]),
            'Distance': float(request.form["distance"]),
            'Points Accumulated': float(request.form["points_accumulated"]),
            'Points Redeemed': float(request.form["points_redeemed"]),
            'Dollar Cost Points Redeemed': float(request.form["dollar_cost"]),
            'Year': int(request.form["year"])
        }])

        cluster = int(cluster_activity_pipeline.predict(X)[0])
        name = cluster_activity_info["cluster_names"][cluster]
        description = {
            0: "Clients très engagés",
            1: "Grands voyageurs",
            2: "Clients peu actifs"
        }[cluster]

    return render_template(
        "predict_customer_cluster.html",
        cluster=cluster,
        name=name,
        description=description
    )

# =========================
# MODELS PAGE (ADMIN ONLY)
# =========================
@app.route("/models")
@login_required
def models():
    '''if current_user.role != "admin":
        return "Access Denied", 403'''
    selected_model = request.args.get("model", "RandomForest")
    metrics = MODEL_METRICS.get(selected_model, {})
    return render_template(
        "models.html",
        models=list(MODEL_METRICS.keys()),
        selected_model=selected_model,
        metrics=metrics
    )
@app.route("/models_churn", methods=["GET"])
def models_churn():
    selected_model = request.args.get("model", "Random Forest")
    metrics = {}
    if selected_model in CHURN_METRICS:
        model_metrics = CHURN_METRICS[selected_model]
        if 'Error' not in model_metrics:
            metrics = {
                'Accuracy': f"{model_metrics.get('Accuracy', 0):.4f}",
                'Precision': f"{model_metrics.get('Precision', 0):.4f}",
                'Recall': f"{model_metrics.get('Recall', 0):.4f}",
                'F1-Score': f"{model_metrics.get('F1-Score', 0):.4f}",
                'ROC-AUC': f"{model_metrics.get('ROC-AUC', 0):.4f}"
            }
        else:
            metrics = {'Error': model_metrics['Error']}
    return render_template(
        "models_churn.html",
        models=list(CHURN_METRICS.keys()),
        selected_model=selected_model,
        metrics=metrics
    )

# =========================
# POWER BI (ADMIN ONLY)
# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
@login_required
@admin_required
def admin():
    return render_template("bi_dashboard.html")

# =========================
# INIT DB
# =========================
with app.app_context():
    db.create_all()

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
