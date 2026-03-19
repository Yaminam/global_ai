# API Testing Examples

## Health Check

```bash
curl -X GET http://localhost:5000/api/health
```

---

## File Upload

### Upload Single File with Description
```bash
curl -X POST \
  -F "file=@data.csv" \
  -F "description=Sales Data Q1" \
  -F "category=finance" \
  http://localhost:5000/api/upload
```

### Upload Multiple Files
```bash
curl -X POST \
  -F "files=@file1.csv" \
  -F "files=@file2.json" \
  -F "files=@file3.xlsx" \
  http://localhost:5000/api/upload/multiple
```

---

## Validation

### Get Sample Validation Rules
```bash
curl -X GET http://localhost:5000/api/validate/sample-rules
```

### Validate Data with Rules
```bash
curl -X POST http://localhost:5000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/data.csv",
    "rules": {
      "email": "email",
      "phone": "phone",
      "date_of_birth": "date"
    }
  }'
```

### Custom Regex Validation
```bash
curl -X POST http://localhost:5000/api/validate/rules \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/customers.csv",
    "column_rules": {
      "customer_email": "email",
      "phone_number": "phone",
      "registration_date": "date",
      "website": "url"
    }
  }'
```

### Get Data Profile
```bash
curl -X POST http://localhost:5000/api/validate/profile \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/data.csv"
  }'
```

---

## Data Processing

### Get Sample Processing Configuration
```bash
curl -X GET http://localhost:5000/api/process/sample-config
```

### Get Available Operators
```bash
curl -X GET http://localhost:5000/api/process/operators
```

### Process Data with Filters
```bash
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/employees.csv",
    "dataset_id": "dataset-12345",
    "config": {
      "filters": {
        "age": {"$gte": 25},
        "department": "Engineering",
        "salary": {"$lte": 150000}
      }
    }
  }'
```

### Process Data with Transformations
```bash
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/sales.csv",
    "config": {
      "filters": {
        "status": "completed"
      },
      "transformations": [
        {
          "type": "normalize",
          "columns": ["amount", "discount"]
        },
        {
          "type": "drop_columns",
          "columns": ["internal_id", "temp_notes"]
        }
      ]
    }
  }'
```

### Process Data with Sorting
```bash
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/products.csv",
    "config": {
      "sorting": {
        "price": "desc",
        "category": "asc"
      }
    }
  }'
```

### Complex Processing Pipeline
```bash
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/transactions.csv",
    "config": {
      "filters": {
        "amount": {"$gt": 100},
        "date": {"$gte": "2024-01-01"},
        "status": {"$in": ["completed", "processing"]}
      },
      "transformations": [
        {
          "type": "normalize",
          "columns": ["amount", "fee"]
        },
        {
          "type": "drop_columns",
          "columns": ["api_key", "internal_notes"]
        }
      ],
      "sorting": {
        "amount": "desc",
        "date": "desc"
      }
    }
  }'
```

### Get Job Status
```bash
curl -X GET http://localhost:5000/api/process/job-abc-def-ghi
```

---

## Results

### Get Results for Completed Job
```bash
curl -X GET "http://localhost:5000/api/results/job-abc-def-ghi?nrows=20"
```

### Get Result Statistics
```bash
curl -X GET http://localhost:5000/api/results/job-abc-def-ghi/stats
```

### Download Results File
```bash
curl -X GET http://localhost:5000/api/results/job-abc-def-ghi/download \
  -o results.json
```

### List All Results
```bash
curl -X GET http://localhost:5000/api/results
```

---

## Analytics

### Perform Analytics
```bash
curl -X POST http://localhost:5000/api/analytics \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "uploads/data.csv",
    "job_id": "job-123",
    "dataset_id": "dataset-456"
  }'
```

### Get Analytics for Job
```bash
curl -X GET http://localhost:5000/api/analytics/job-abc-def-ghi
```

### Get Statistical Analysis
```bash
curl -X GET http://localhost:5000/api/analytics/stats/job-abc-def-ghi
```

### Get Detected Anomalies
```bash
curl -X GET "http://localhost:5000/api/analytics/anomalies/job-abc-def-ghi?type=outliers"
```

Supported types: `outliers`, `missing`, `duplicates`, `all`

### Get Trend Analysis
```bash
curl -X GET http://localhost:5000/api/analytics/trends/job-abc-def-ghi
```

### Get AI-Generated Insights
```bash
curl -X GET "http://localhost:5000/api/analytics/insights/job-abc-def-ghi?severity=high"
```

Supported severity levels: `low`, `medium`, `high`, `all`

---

## Testing with Python

### Using the requests library

```python
import requests
import json

# Upload file
files = {'file': open('data.csv', 'rb')}
data = {'description': 'My Data', 'category': 'test'}
response = requests.post('http://localhost:5000/api/upload', files=files, data=data)
print(response.json())

# Validate data
validation_data = {
    'file_path': 'uploads/data.csv',
    'rules': {
        'email': 'email',
        'phone': 'phone'
    }
}
response = requests.post('http://localhost:5000/api/validate',
                        json=validation_data)
print(response.json())

# Process data
process_data = {
    'file_path': 'uploads/data.csv',
    'config': {
        'filters': {'age': {'$gte': 18}}
    }
}
response = requests.post('http://localhost:5000/api/process',
                        json=process_data)
result = response.json()
job_id = result['data']['job_id']

# Get results
response = requests.get(f'http://localhost:5000/api/results/{job_id}')
print(response.json())
```

---

## Testing with Postman

1. **Import endpoints** in Postman
2. **Set variable** `base_url` to `http://localhost:5000`
3. **Create requests** using the examples above
4. **Save response** as test data

### Example Postman Collection Variable
```json
{
  "base_url": "http://localhost:5000",
  "job_id": "job-abc-def-ghi",
  "file_path": "uploads/data.csv"
}
```

---

## Common Response Formats

### Success Response (200)
```json
{
  "data": {
    "job_id": "job-123",
    "status": "completed",
    "results": {}
  },
  "message": "Operation completed successfully"
}
```

### Error Response (400/500)
```json
{
  "error": "Validation failed",
  "details": "File contains invalid email addresses",
  "error_code": "VALIDATION_FAILED",
  "status_code": 400
}
```

---

## Batch Testing Script

```bash
#!/bin/bash

# Test health endpoint
echo "Testing health endpoint..."
curl http://localhost:5000/api/health

# Test API info
echo -e "\nTesting API info..."
curl http://localhost:5000/api/info

# Test upload (assuming data.csv exists)
echo -e "\nTesting file upload..."
curl -F "file=@data.csv" http://localhost:5000/api/upload

# Test validation rules
echo -e "\nTesting sample rules..."
curl http://localhost:5000/api/validate/sample-rules

echo "All tests completed!"
```

Save as `test_api.sh` and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Performance Testing

### Load Test Upload
```bash
# Install Apache Bench (ab)
# Then test with multiple concurrent requests
ab -n 100 -c 10 -p upload_data.json -T application/json \
  http://localhost:5000/api/upload
```

### Test with Large File
```bash
# Test with a larger CSV file
curl -X POST \
  -F "file=@large_file.csv" \
  http://localhost:5000/api/upload
```

---

Last Updated: 2024
