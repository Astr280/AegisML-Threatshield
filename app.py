from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'malware_detection_secret_key_2024')

# ── Global state ──────────────────────────────────────────────────────
extra_trees_model = None
logistic_model = None
random_forest_model = None
scaler = None
X_train = None
X_test = None
y_train = None
y_test = None
feature_names = None
top_features = None          # Top N features for prediction UI
feature_importances = None   # Feature importance dict from ExtraTrees
dataset = None
model_scores = {}            # Stores computed accuracy for each model

# Number of features to show in the prediction UI
TOP_N_FEATURES = 25

# ── Dataset path ──────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DREBIN_CSV = os.path.join(DATA_DIR, "drebin215.csv")


def get_class_column(df):
    """Detect the class/label column in the dataset."""
    # Common column names for the target
    candidates = ['class', 'Class', 'CLASS', 'label', 'Label', 'LABEL', 'malware', 'target']
    for c in candidates:
        if c in df.columns:
            return c
    # Fallback: last column
    return df.columns[-1]


def encode_labels(series):
    """Encode class labels to binary (1=malware, 0=benign).
    
    DREBIN-215 uses: 'S' = malware (5,560 samples from DREBIN project)
                     'B' = benign  (9,476 benign apps)
    """
    def _map(x):
        val = str(x).strip().upper()
        if val in ['1', 'S', 'MALWARE', 'M', 'MAL']:
            return 1
        elif val in ['0', 'B', 'BENIGN', 'SAFE', 'GOODWARE']:
            return 0
        else:
            try:
                return int(float(val))
            except ValueError:
                return 0
    return series.map(_map)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Static login (admin/admin)
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('upload'))
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', error='No file uploaded')

        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error='No file selected')

        if file and file.filename.endswith('.csv'):
            global dataset
            dataset = pd.read_csv(file, low_memory=False)
            session['dataset_uploaded'] = True
            return redirect(url_for('preview'))
        else:
            return render_template('upload.html', error='Please upload a CSV file')

    # Check if DREBIN dataset exists for auto-load option
    drebin_exists = os.path.exists(DREBIN_CSV) and os.path.getsize(DREBIN_CSV) > 1000
    return render_template('upload.html', drebin_exists=drebin_exists)


@app.route('/load_drebin')
def load_drebin():
    """Auto-load the DREBIN-215 dataset without manual upload."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    global dataset
    if os.path.exists(DREBIN_CSV) and os.path.getsize(DREBIN_CSV) > 1000:
        dataset = pd.read_csv(DREBIN_CSV, low_memory=False)
        session['dataset_uploaded'] = True
        return redirect(url_for('preview'))
    else:
        return render_template('upload.html',
                               error='DREBIN dataset not found. Run: python generate_dataset.py',
                               drebin_exists=False)


@app.route('/preview')
def preview():
    if not session.get('logged_in') or not session.get('dataset_uploaded'):
        return redirect(url_for('login'))

    global dataset
    # Show first 10 rows for preview
    preview_data = dataset.head(10).to_html(classes='table table-striped', index=False)
    total_records = len(dataset)
    total_features = len(dataset.columns) - 1  # Exclude class column

    # Class distribution
    class_col = get_class_column(dataset)
    class_dist = dataset[class_col].value_counts().to_dict()

    return render_template('preview.html',
                           preview_data=preview_data,
                           total_records=total_records,
                           total_features=total_features,
                           class_dist=class_dist)


@app.route('/train')
def train():
    if not session.get('logged_in') or not session.get('dataset_uploaded'):
        return redirect(url_for('login'))

    global extra_trees_model, logistic_model, random_forest_model
    global X_train, X_test, y_train, y_test
    global feature_names, top_features, feature_importances
    global dataset, model_scores, scaler

    try:
        # ── Prepare data ──────────────────────────────────────────────
        class_col = get_class_column(dataset)

        # All columns except class column are features
        feature_cols = [c for c in dataset.columns if c != class_col]
        X = dataset[feature_cols].copy()

        # Handle any non-numeric columns
        for col in X.columns:
            X[col] = pd.to_numeric(X[col], errors='coerce')
        X = X.fillna(0)

        # Encode target
        y = encode_labels(dataset[class_col])

        feature_names = list(X.columns)

        # ── Split ─────────────────────────────────────────────────────
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )

        # ── Train Extra Trees Classifier ──────────────────────────────
        extra_trees_model = ExtraTreesClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )
        extra_trees_model.fit(X_train, y_train)

        # ── Train Random Forest ───────────────────────────────────────
        random_forest_model = RandomForestClassifier(
            n_estimators=200,
            random_state=42,
            n_jobs=-1
        )
        random_forest_model.fit(X_train, y_train)

        # ── Train Logistic Regression (with scaling) ──────────────────
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        logistic_model = LogisticRegression(
            max_iter=2000,
            random_state=42,
            C=1.0,
            solver='lbfgs'
        )
        logistic_model.fit(X_train_scaled, y_train)

        # ── Compute scores ────────────────────────────────────────────
        model_scores = {
            'et_train': round(accuracy_score(y_train, extra_trees_model.predict(X_train)) * 100, 2),
            'et_test': round(accuracy_score(y_test, extra_trees_model.predict(X_test)) * 100, 2),
            'rf_train': round(accuracy_score(y_train, random_forest_model.predict(X_train)) * 100, 2),
            'rf_test': round(accuracy_score(y_test, random_forest_model.predict(X_test)) * 100, 2),
            'lr_train': round(accuracy_score(y_train, logistic_model.predict(X_train_scaled)) * 100, 2),
            'lr_test': round(accuracy_score(y_test, logistic_model.predict(X_test_scaled)) * 100, 2),
        }

        # ── Feature importance (from Extra Trees) ─────────────────────
        importances = extra_trees_model.feature_importances_
        importance_pairs = sorted(
            zip(feature_names, importances),
            key=lambda x: x[1],
            reverse=True
        )
        feature_importances = {name: float(imp) for name, imp in importance_pairs}
        top_features = [name for name, _ in importance_pairs[:TOP_N_FEATURES]]

        session['models_trained'] = True

        return redirect(url_for('predict_page'))

    except Exception as e:
        import traceback
        return f"Error during training: {str(e)}<br><pre>{traceback.format_exc()}</pre>"


@app.route('/predict_page')
def predict_page():
    if not session.get('logged_in') or not session.get('models_trained'):
        return redirect(url_for('login'))

    return render_template('predict.html',
                           features=top_features,
                           all_features=feature_names,
                           model_scores=model_scores,
                           feature_importances=feature_importances)


@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('logged_in') or not session.get('models_trained'):
        return redirect(url_for('login'))

    global extra_trees_model, logistic_model, random_forest_model, scaler

    # Get form data
    model_type = request.form.get('model_type')

    # Collect feature values — build a full feature vector
    feature_values = []
    input_data = {}
    for feature in feature_names:
        value = request.form.get(feature, 'no')
        binary_value = 1 if value == 'yes' else 0
        feature_values.append(binary_value)
        # Only record features shown in UI for the report
        if feature in top_features:
            input_data[feature] = value

    # Make prediction
    input_array = np.array(feature_values).reshape(1, -1)

    if model_type == 'extra_trees':
        prediction = extra_trees_model.predict(input_array)[0]
        proba = extra_trees_model.predict_proba(input_array)[0]
        model_name = 'Extra Trees Classifier'
    elif model_type == 'random_forest':
        prediction = random_forest_model.predict(input_array)[0]
        proba = random_forest_model.predict_proba(input_array)[0]
        model_name = 'Random Forest'
    else:
        input_scaled = scaler.transform(input_array)
        prediction = logistic_model.predict(input_scaled)[0]
        proba = logistic_model.predict_proba(input_scaled)[0]
        model_name = 'Logistic Regression'

    result = 'Malware' if prediction == 1 else 'Benign'
    confidence = round(float(max(proba)) * 100, 1)

    # Store prediction result in session for PDF generation
    session['last_prediction'] = {
        'input_data': input_data,
        'model': model_name,
        'result': result,
        'confidence': confidence,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return render_template('result.html',
                           input_data=input_data,
                           model=model_name,
                           result=result,
                           confidence=confidence)


@app.route('/download_pdf')
def download_pdf():
    if not session.get('last_prediction'):
        return redirect(url_for('predict_page'))

    pred_data = session['last_prediction']

    # Create PDF
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "AegisML ThreatShield - Prediction Report")

    # Subtitle
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, "Trained on DREBIN-215 Android Malware Dataset (Yerima & Sezer, 2018)")

    # Timestamp
    c.drawString(50, height - 85, f"Generated: {pred_data['timestamp']}")

    # Model used
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 115, f"Model: {pred_data['model']}")

    # Prediction result
    c.setFont("Helvetica-Bold", 14)
    result_color = colors.red if pred_data['result'] == 'Malware' else colors.green
    c.setFillColor(result_color)
    c.drawString(50, height - 145, f"Prediction: {pred_data['result']} ({pred_data.get('confidence', 'N/A')}% confidence)")
    c.setFillColor(colors.black)

    # Input features
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 175, "Active Permissions / Features:")

    c.setFont("Helvetica", 10)
    y_position = height - 195
    for feature, value in pred_data['input_data'].items():
        if value == 'yes':
            c.drawString(70, y_position, f"• {feature}")
            y_position -= 15
            if y_position < 50:
                c.showPage()
                y_position = height - 50

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name='prediction_report.pdf', mimetype='application/pdf')


@app.route('/performance')
def performance():
    if not session.get('logged_in') or not session.get('models_trained'):
        return redirect(url_for('login'))

    global extra_trees_model, logistic_model, random_forest_model
    global X_train, X_test, y_train, y_test, scaler

    # Extra Trees metrics
    et_test_pred = extra_trees_model.predict(X_test)
    et_cm = confusion_matrix(y_test, et_test_pred)
    et_report = classification_report(y_test, et_test_pred, output_dict=True, zero_division=0)

    # Random Forest metrics
    rf_test_pred = random_forest_model.predict(X_test)
    rf_cm = confusion_matrix(y_test, rf_test_pred)
    rf_report = classification_report(y_test, rf_test_pred, output_dict=True, zero_division=0)

    # Logistic Regression metrics (with scaling)
    X_test_scaled = scaler.transform(X_test)
    lr_test_pred = logistic_model.predict(X_test_scaled)
    lr_cm = confusion_matrix(y_test, lr_test_pred)
    lr_report = classification_report(y_test, lr_test_pred, output_dict=True, zero_division=0)

    return render_template('performance.html',
                           et_train_score=model_scores['et_train'],
                           et_test_score=model_scores['et_test'],
                           et_cm=et_cm.tolist(),
                           et_report=et_report,
                           rf_train_score=model_scores['rf_train'],
                           rf_test_score=model_scores['rf_test'],
                           rf_cm=rf_cm.tolist(),
                           rf_report=rf_report,
                           lr_train_score=model_scores['lr_train'],
                           lr_test_score=model_scores['lr_test'],
                           lr_cm=lr_cm.tolist(),
                           lr_report=lr_report,
                           dataset_name='DREBIN-215',
                           n_samples=len(X_train) + len(X_test),
                           n_features=len(feature_names))


@app.route('/charts')
def charts():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Pass real data to the template
    chart_data = {}
    if session.get('models_trained') and model_scores:
        # Class distribution from dataset
        class_col = get_class_column(dataset)
        y_encoded = encode_labels(dataset[class_col])
        n_malware = int(y_encoded.sum())
        n_benign = int(len(y_encoded) - n_malware)

        # Top 15 feature importances
        top_15 = list(feature_importances.items())[:15] if feature_importances else []

        chart_data = {
            'et_test': model_scores.get('et_test', 0),
            'rf_test': model_scores.get('rf_test', 0),
            'lr_test': model_scores.get('lr_test', 0),
            'et_train': model_scores.get('et_train', 0),
            'rf_train': model_scores.get('rf_train', 0),
            'lr_train': model_scores.get('lr_train', 0),
            'n_malware': n_malware,
            'n_benign': n_benign,
            'top_features': [name for name, _ in top_15],
            'top_importances': [round(imp * 100, 2) for _, imp in top_15],
        }

    return render_template('charts.html', chart_data=chart_data)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
