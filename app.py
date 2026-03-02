from flask import Flask, render_template, request, redirect, url_for, session, send_file
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import pickle
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import io

app = Flask(__name__)
app.secret_key = 'malware_detection_secret_key_2024'

# Global variables to store models and data
extra_trees_model = None
logistic_model = None
X_train = None
X_test = None
y_train = None
y_test = None
feature_names = None
dataset = None

# Selected features (23 attributes)
SELECTED_FEATURES = [
    'access_all_downloads', 'access_cache_filesystem', 'access_fine_location',
    'access_network_state', 'access_service', 'access_shared_data',
    'access_superuser', 'access_wifi_state', 'camera', 'change_configuration',
    'delete_cache_files', 'read_attachment', 'read_contacts', 'read_data',
    'read_external_storage', 'read_gmail', 'read_history_bookmarks',
    'read_messages', 'read_phone_state', 'read_settings', 'read_sms',
    'receive_boot_completed', 'receive_sms'
]

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
            dataset = pd.read_csv(file)
            session['dataset_uploaded'] = True
            return redirect(url_for('preview'))
        else:
            return render_template('upload.html', error='Please upload a CSV file')
    
    return render_template('upload.html')

@app.route('/preview')
def preview():
    if not session.get('logged_in') or not session.get('dataset_uploaded'):
        return redirect(url_for('login'))
    
    global dataset
    # Show first 10 rows for preview
    preview_data = dataset.head(10).to_html(classes='table table-striped', index=False)
    total_records = len(dataset)
    total_features = len(dataset.columns)
    
    return render_template('preview.html', 
                         preview_data=preview_data,
                         total_records=total_records,
                         total_features=total_features)

@app.route('/train')
def train():
    if not session.get('logged_in') or not session.get('dataset_uploaded'):
        return redirect(url_for('login'))
    
    global extra_trees_model, logistic_model, X_train, X_test, y_train, y_test, feature_names, dataset
    
    try:
        # Prepare the dataset
        # Assuming the last column is the target (class)
        X = dataset[SELECTED_FEATURES]
        y = dataset.iloc[:, -1]  # Last column as target
        
        # Convert categorical to binary if needed
        # Map malware/benign or goodware to 1/0
        y = y.map(lambda x: 1 if str(x).lower() in ['malware', '1'] else 0)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        feature_names = SELECTED_FEATURES
        
        # Train Extra Trees Classifier
        extra_trees_model = ExtraTreesClassifier(n_estimators=100, random_state=42)
        extra_trees_model.fit(X_train, y_train)
        
        # Train Logistic Regression
        logistic_model = LogisticRegression(max_iter=1000, random_state=42)
        logistic_model.fit(X_train, y_train)
        
        session['models_trained'] = True
        
        return redirect(url_for('predict_page'))
    
    except Exception as e:
        return f"Error during training: {str(e)}"

@app.route('/predict_page')
def predict_page():
    if not session.get('logged_in') or not session.get('models_trained'):
        return redirect(url_for('login'))
    
    return render_template('predict.html', features=SELECTED_FEATURES)

@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('logged_in') or not session.get('models_trained'):
        return redirect(url_for('login'))
    
    global extra_trees_model, logistic_model
    
    # Get form data
    model_type = request.form.get('model_type')
    
    # Collect feature values
    feature_values = []
    input_data = {}
    for feature in SELECTED_FEATURES:
        value = request.form.get(feature)
        binary_value = 1 if value == 'yes' else 0
        feature_values.append(binary_value)
        input_data[feature] = value
    
    # Make prediction
    input_array = np.array(feature_values).reshape(1, -1)
    
    if model_type == 'extra_trees':
        prediction = extra_trees_model.predict(input_array)[0]
        model_name = 'Extra Trees Classifier'
    else:
        prediction = logistic_model.predict(input_array)[0]
        model_name = 'Logistic Regression'
    
    result = 'Malware' if prediction == 1 else 'Benign'
    
    # Store prediction result in session for PDF generation
    session['last_prediction'] = {
        'input_data': input_data,
        'model': model_name,
        'result': result,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return render_template('result.html', 
                         input_data=input_data,
                         model=model_name,
                         result=result)

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
    c.drawString(50, height - 50, "Malware Detection - Prediction Report")
    
    # Timestamp
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"Generated: {pred_data['timestamp']}")
    
    # Model used
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 100, f"Model: {pred_data['model']}")
    
    # Prediction result
    c.setFont("Helvetica-Bold", 14)
    result_color = colors.red if pred_data['result'] == 'Malware' else colors.green
    c.setFillColor(result_color)
    c.drawString(50, height - 130, f"Prediction: {pred_data['result']}")
    c.setFillColor(colors.black)
    
    # Input features
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 160, "Input Features:")
    
    c.setFont("Helvetica", 10)
    y_position = height - 180
    for feature, value in pred_data['input_data'].items():
        if value == 'yes':
            c.drawString(70, y_position, f"• {feature}: {value}")
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
    
    global extra_trees_model, logistic_model, X_train, X_test, y_train, y_test
    
    # Extra Trees metrics
    et_train_pred = extra_trees_model.predict(X_train)
    et_test_pred = extra_trees_model.predict(X_test)
    et_train_score = accuracy_score(y_train, et_train_pred) * 100
    et_test_score = accuracy_score(y_test, et_test_pred) * 100
    et_cm = confusion_matrix(y_test, et_test_pred)
    et_report = classification_report(y_test, et_test_pred, output_dict=True, zero_division=0)
    
    # Logistic Regression metrics
    lr_train_pred = logistic_model.predict(X_train)
    lr_test_pred = logistic_model.predict(X_test)
    lr_train_score = accuracy_score(y_train, lr_train_pred) * 100
    lr_test_score = accuracy_score(y_test, lr_test_pred) * 100
    lr_cm = confusion_matrix(y_test, lr_test_pred)
    lr_report = classification_report(y_test, lr_test_pred, output_dict=True, zero_division=0)
    
    return render_template('performance.html',
                         et_train_score=round(et_train_score, 2),
                         et_test_score=round(et_test_score, 2),
                         et_cm=et_cm.tolist(),
                         et_report=et_report,
                         lr_train_score=round(lr_train_score, 2),
                         lr_test_score=round(lr_test_score, 2),
                         lr_cm=lr_cm.tolist(),
                         lr_report=lr_report)

@app.route('/charts')
def charts():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    return render_template('charts.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
