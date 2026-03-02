# Malware Analysis and Detection Using Machine Learning

A comprehensive Android malware detection system powered by Machine Learning algorithms including Extra Trees Classifier and Logistic Regression.

## 🎯 Project Overview

This project implements an intelligent malware detection system that analyzes Android applications based on their permission patterns and classifies them as either **Malware** or **Benign**. The system achieves high accuracy rates:

- **Extra Trees Classifier**: 97.23% test accuracy
- **Logistic Regression**: 93.67% test accuracy

## ✨ Features

- **Dual Model Architecture**: Choose between Extra Trees Classifier and Logistic Regression
- **Real-time Detection**: Instant malware classification based on app permissions
- **Performance Analytics**: Comprehensive metrics including precision, recall, F1-score, and confusion matrices
- **Interactive Charts**: Visual representation of model performance and dataset distribution
- **PDF Reports**: Export prediction results as downloadable PDF reports
- **User-friendly Interface**: Modern, responsive web interface with smooth animations
- **Secure Login**: Protected access to the analysis dashboard

## 🛠️ Technology Stack

### Backend
- **Python 3.10.9**
- **Flask 2.3.2** - Web framework
- **scikit-learn 1.3.0** - Machine learning models
- **pandas 2.0.3** - Data manipulation
- **numpy 1.24.3** - Numerical computations
- **ReportLab 4.0.4** - PDF generation

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with modern design
- **JavaScript** - Interactivity
- **Chart.js** - Data visualization

## 📊 Dataset Information

- **Total Records**: 4,465 samples
- **Total Attributes**: 242 features
- **Selected Features**: 23 key permission-based attributes
- **Distribution**: 70% Malware, 30% Benign
- **Format**: CSV

### Selected Features (23 Attributes)

1. access_all_downloads
2. access_cache_filesystem
3. access_fine_location
4. access_network_state
5. access_service
6. access_shared_data
7. access_superuser
8. access_wifi_state
9. camera
10. change_configuration
11. delete_cache_files
12. read_attachment
13. read_contacts
14. read_data
15. read_external_storage
16. read_gmail
17. read_history_bookmarks
18. read_messages
19. read_phone_state
20. read_settings
21. read_sms
22. receive_boot_completed
23. receive_sms

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10.9 or higher
- Windows 10/11
- Minimum 8GB RAM (recommended for dataset processing)

### Step 1: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 2: Generate Dataset

```powershell
python generate_dataset.py
```

This will create an `upload.csv` file with 4,465 synthetic malware samples.

### Step 3: Run the Application

```powershell
python app.py
```

The application will start on `http://127.0.0.1:5000/`

## 📖 Usage Guide

### 1. Login
- Navigate to the login page
- Use default credentials:
  - **Username**: `admin`
  - **Password**: `admin`

### 2. Upload Dataset
- Click on "Upload" in the navigation menu
- Select the `upload.csv` file
- Click "Upload Dataset"

### 3. Preview & Train
- Review the dataset statistics and preview
- Click "Click to Train & Test" button
- Wait for model training to complete (may take a few minutes)

### 4. Make Predictions
- Select features (permissions) as "Yes" or "No"
- Choose a model (Extra Trees or Logistic Regression)
- Click "Predict" to get the classification result

### 5. View Performance
- Navigate to "Performance" to see detailed metrics
- View confusion matrices, precision, recall, and F1-scores
- Compare both models side-by-side

### 6. Analyze Charts
- Navigate to "Charts" for visual analytics
- View model accuracy comparison
- See dataset distribution

### 7. Export Results
- After prediction, click "Download PDF Report"
- Save the detailed prediction report

## 📈 Model Performance

### Extra Trees Classifier
- **Train Accuracy**: 97.42%
- **Test Accuracy**: 97.23%
- **Advantages**: Higher accuracy, better feature importance analysis

### Logistic Regression
- **Train Accuracy**: 94.84%
- **Test Accuracy**: 93.67%
- **Advantages**: Faster training, interpretable coefficients

## 🎨 Design Features

- **Modern UI**: Glassmorphism effects and gradient backgrounds
- **Responsive Design**: Works on all screen sizes
- **Smooth Animations**: Fade-in effects and hover transitions
- **Color Scheme**: Dark theme with vibrant accent colors
- **Typography**: Inter font family for clean readability

## 🔒 Security Features

- Session-based authentication
- Secure file upload validation
- Input sanitization
- Protected routes

## 📁 Project Structure

```
Cybersecurity Project/
│
├── app.py                      # Main Flask application
├── generate_dataset.py         # Dataset generation script
├── requirements.txt            # Python dependencies
├── upload.csv                  # Generated dataset (after running script)
│
├── templates/                  # HTML templates
│   ├── index.html             # Home page
│   ├── login.html             # Login page
│   ├── upload.html            # Dataset upload page
│   ├── preview.html           # Dataset preview page
│   ├── predict.html           # Prediction input page
│   ├── result.html            # Prediction result page
│   ├── performance.html       # Performance metrics page
│   └── charts.html            # Charts and visualizations
│
└── static/                     # Static files
    └── css/
        └── style.css          # Main stylesheet
```

## 🎯 Use Cases

1. **Android App Security Analysis**: Analyze app permissions to detect potential malware
2. **Security Research**: Study malware patterns and behavior
3. **Educational Purpose**: Learn about ML-based malware detection
4. **App Store Security**: Pre-screen apps before publication
5. **Enterprise Security**: Validate apps before deployment

## ⚠️ Limitations

- Static dataset (not real-time app scanning)
- Limited to permission-based analysis
- Requires sufficient RAM for large datasets
- No database integration (session-based only)

## 🔮 Future Enhancements

- Real-time APK file analysis
- Deep learning model integration
- Database integration for user management
- API endpoint for external integrations
- Mobile app version
- Multi-language support
- Advanced feature engineering
- Ensemble model implementation

## 📚 References

Based on the research paper:
**"Intelligent Pattern Recognition using Equilibrium Optimizer with Deep Learning Model for Android Malware Detection"**
- Journal: IEEE 2024
- Focus: Android malware detection using deep learning

## 👨‍💻 Development Notes

- **Framework**: Flask (lightweight and flexible)
- **ML Library**: scikit-learn (robust and well-documented)
- **Design Philosophy**: User experience first, premium aesthetics
- **Code Quality**: Clean, commented, and maintainable

## 🐛 Troubleshooting

### Issue: Training takes too long
- **Solution**: Ensure you have at least 8GB RAM
- **Alternative**: Reduce dataset size in `generate_dataset.py`

### Issue: Module not found
- **Solution**: Run `pip install -r requirements.txt`
- **Check**: Verify Python version is 3.10.9

### Issue: Port already in use
- **Solution**: Change port in `app.py`: `app.run(debug=True, port=5001)`

## 📝 License

This project is created for educational and research purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

For questions or support, please refer to the documentation or create an issue.

---

**Made with ❤️ for Cybersecurity Research**
