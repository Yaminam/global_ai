# 🎓 Advanced Analytics Platform - Assignment Implementation

> **Full-Stack Data Analytics Application Demonstrating Advanced Python Concepts**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Assignment Compliance Checklist

This project fully implements all required assignment components:

### ✅ **Python Concepts Implemented**

- [x] **Regular Expressions (Regex)** - Form validation (`backend/validators/`)
- [x] **Pandas & NumPy** - Mean, median, std calculations (`backend/analytics/`)
- [x] **Matplotlib** - Backend chart generation (`backend/visualization/`)
- [x] **JSON Serialization** - Data storage with dump/load (`backend/storage/`)
- [x] **Abstract Base Classes** - ABC pattern (`backend/models/`)
- [x] **Multiple Inheritance** - 3+ parent classes (`backend/models/`)
- [x] **Method Resolution Order** - Demonstrated MRO (`backend/models/`)
- [x] **Operator Overloading** - `__add__`, `__eq__`, `__lt__` (`backend/models/`)
- [x] **Mixins** - Reusable TimestampMixin, MetadataMixin (`backend/models/`)
- [x] **Custom Decorators** - 2 decorators (timing, caching) (`backend/utils/`)
- [x] **Closures** - Factory functions with state (`backend/utils/`)
- [x] **Custom Iterator** - `__iter__` and `__next__` (`backend/utils/`)
- [x] **Generators** - `yield` keyword usage (`backend/utils/`)
- [x] **Multithreading** - Real threading implementation (`backend/processing/`)
- [x] **Multiprocessing** - Real multiprocessing (`backend/processing/`)

### ✅ **Project Structure**

- [x] **Modular Architecture** - Separate modules for each concern
- [x] **User Registration Form** - Name, email, phone, password with regex validation
- [x] **Backend API** - Flask REST API integrating all modules
- [x] **Frontend UI** - HTML/CSS/JavaScript interface
- [x] **Documentation** - README, CONCEPTS.md, code comments
- [x] **Dependencies** - requirements.txt provided

---

## 🗂️ Project Structure

```
sadul_globalai/
├── backend/                        # Python backend (modular)
│   ├── __init__.py
│   ├── app.py                      # Main Flask application
│   │
│   ├── validators/                 # Regex form validation
│   │   ├── __init__.py
│   │   └── form_validators.py      # Name, email, phone, password validation
│   │
│   ├── analytics/                  # Statistical analysis
│   │   ├── __init__.py
│   │   └── statistics.py           # Pandas/NumPy: mean, median, std
│   │
│   ├── visualization/              # Chart generation
│   │   ├── __init__.py
│   │   └── charts.py               # Matplotlib chart creation
│   │
│   ├── storage/                    # Data persistence
│   │   ├── __init__.py
│   │   └── json_storage.py         # JSON dump/load operations
│   │
│   ├── models/                     # Advanced OOP concepts
│   │   ├── __init__.py
│   │   └── data_models.py          # ABC, multiple inheritance, MRO, operators, mixins
│   │
│   ├── utils/                      # Python advanced concepts
│   │   ├── __init__.py
│   │   ├── decorators.py           # 2 custom decorators + closures
│   │   ├── iterators.py            # Custom iterators
│   │   └── generators.py           # Generator functions
│   │
│   └── processing/                 # Concurrency
│       ├── __init__.py
│       └── async_processor.py      # Threading & multiprocessing
│
├── frontend/                       # Frontend UI
│   ├── index.html                  # Main HTML with registration form
│   ├── css/
│   │   └── style.css               # Styles
│   └── js/
│       ├── app.js                  # Application logic
│       └── api.js                  # API client
│
├── storage/                        # Data storage
│   ├── uploads/                    # User uploads
│   ├── charts/                     # Generated Matplotlib charts
│   ├── json_data/                  # JSON storage files
│   └── logs/                       # Application logs
│
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── CONCEPTS.md                     # Detailed concept explanations
└── run_backend.py                  # Legacy backend (deprecated)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sadul_globalai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   cd backend
   python app.py
   ```

5. **Access the application**
   - Open browser: http://localhost:5000
   - The frontend is served from the backend

---

## 📚 Features

### 1. User Registration (Regex Validation)

Register users with comprehensive form validation:

**Fields**:
- **Name**: Letters and spaces only (2-50 characters)
- **Email**: Valid email format
- **Phone**: 10-15 digits, optional + prefix
- **Password**: Min 8 chars with uppercase, lowercase, digit, special char

**Validation** (`backend/validators/form_validators.py`):
```python
PATTERNS = {
    'name': r'^[A-Za-z\s]{2,50}$',
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^\+?[1-9]\d{9,14}$',
    'password': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
}
```

### 2. Data Upload & Processing

**Supported Formats**: CSV, JSON, XLSX, XLS

**Pipeline**:
1. Upload → Validate → Process → Analyze
2. Statistical analysis with Pandas/NumPy
3. Chart generation with Matplotlib
4. Results storage in JSON

### 3. Statistical Analysis

Using Pandas and NumPy (`backend/analytics/statistics.py`):

- **Mean**: `np.mean()` and `DataFrame.mean()`
- **Median**: `np.median()` and `DataFrame.median()`
- **Standard Deviation**: `np.std(ddof=1)` and `DataFrame.std()`
- **Correlation Matrix**: `DataFrame.corr()`
- **Distribution Analysis**: Quartiles, IQR, skewness, kurtosis

### 4. Visualization

Backend chart generation using Matplotlib (`backend/visualization/charts.py`):

**Chart Types**:
- Bar charts
- Line charts
- Histograms
- Scatter plots
- Pie charts

**Example**:
```python
generator = ChartGenerator()
chart_path = generator.create_bar_chart(
    data={'A': 100, 'B': 200},
    title='Sales by Product',
    xlabel='Products',
    ylabel='Sales',
    filename='sales.png'
)
```

### 5. Data Persistence

JSON-based storage (`backend/storage/json_storage.py`):

```python
storage = JSONStorage()

# Save
storage.save('key', data, metadata={'source': 'api'})

# Load
data = storage.load('key')

# Update
storage.update('key', {'field': 'new_value'})
```

---

## 🔌 API Endpoints

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user with validation |

### Data Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload dataset file |
| POST | `/api/process` | Process uploaded file |
| GET | `/api/analytics/<job_id>` | Get statistical analysis |
| GET | `/api/charts/<job_id>/<chart_type>` | Get generated chart |

### Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System health check |
| GET | `/api/storage/stats` | Storage statistics |
| POST | `/api/batch-process` | Batch processing with generators |
| GET | `/api/iterator-demo` | Iterator demonstration |

---

## 🧪 Testing the Concepts

### Test Validators
```bash
cd backend
python -c "from validators import FormValidator; print(FormValidator.validate_email('test@example.com'))"
```

### Test Analytics
```bash
python -c "import pandas as pd; from analytics import StatisticalAnalyzer; df = pd.DataFrame({'x': [1,2,3,4,5]}); a = StatisticalAnalyzer(df); print(a.compute_mean())"
```

### Test OOP Concepts
```bash
python -m models.data_models
```

### Test Decorators & Generators
```bash
python -m utils.decorators
python -m utils.generators
python -m utils.iterators
```

### Test Concurrent Processing
```bash
python -m processing.async_processor
```

---

## 📖 Documentation

- **CONCEPTS.md**: Comprehensive explanation of all Python concepts with examples
- **Code Comments**: Detailed inline documentation in all modules
- **Docstrings**: Google-style docstrings for all functions and classes

---

## 🛠️ Technology Stack

**Backend**:
- Python 3.8+
- Flask 2.3+ (Web framework)
- Pandas 2.0+ (Data analysis)
- NumPy 1.24+ (Numerical computing)
- Matplotlib 3.7+ (Visualization)

**Frontend**:
- HTML5
- CSS3 (Modern UI design)
- Vanilla JavaScript (ES6+)

**Data Storage**:
- JSON (File-based storage)
- File system for uploads and charts

---

## 📦 Dependencies

```txt
Flask>=2.3.0
Flask-CORS>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
openpyxl>=3.1.0
reportlab>=4.0.0
gunicorn>=21.2.0
```

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## 🚦 Running in Production

### Using Gunicorn

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Waitress (Windows)

```bash
pip install waitress
cd backend
waitress-serve --port=5000 app:app
```

---

## 📝 Assignment Deliverables

### ✅ Source Code
- Modular Python backend with 7+ modules
- Frontend with HTML/CSS/JS
- All concepts properly implemented

### ✅ Documentation
- **README.md**: Complete project overview
- **CONCEPTS.md**: Detailed concept explanations
- Inline code comments and docstrings

### ✅ Dependencies
- `requirements.txt` with all packages

### ✅ Demonstration
- Working application on http://localhost:5000
- Testable endpoints and features

---

## 🎓 Learning Outcomes

This project demonstrates mastery of:

1. **Python Fundamentals**: Regex, file I/O, data structures
2. **Data Analysis**: Pandas, NumPy statistical operations
3. **Visualization**: Matplotlib chart generation
4. **OOP**: ABC, inheritance, MRO, operator overloading, mixins
5. **Functional Programming**: Decorators, closures, generators, iterators
6. **Concurrency**: Threading and multiprocessing
7. **Web Development**: Flask REST API
8. **Software Architecture**: Modular design, separation of concerns
9. **Best Practices**: Code organization, documentation, error handling

---

## 🐛 Troubleshooting

### Issue: Module not found
**Solution**: Make sure you're in the `backend/` directory and have activated the virtual environment

### Issue: Charts not generating
**Solution**: Ensure `storage/charts/` directory exists
```bash
mkdir -p storage/charts
```

### Issue: JSON storage errors
**Solution**: Ensure `storage/json_data/` directory exists
```bash
mkdir -p storage/json_data
```

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Assignment requirements for guiding comprehensive Python concept implementation
- Flask and Python communities for excellent documentation
- Pandas, NumPy, and Matplotlib teams for powerful libraries

---

**Built with ❤️ demonstrating advanced Python concepts**
