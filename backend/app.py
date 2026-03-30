"""
Advanced Analytics Platform - Flask Backend
Demonstrates comprehensive Python concepts and modular architecture

Features:
- Form validation with regex
- Statistical analysis with Pandas/NumPy (mean, median, std)
- Matplotlib chart generation
- JSON storage
- Threading and Multiprocessing
- Advanced OOP (abstract classes, multiple inheritance, MRO, operator overloading, mixins)
- Decorators, Generators, Iterators, Closures
"""

import os
import sys
import uuid
import io

# Add backend directory to Python path to enable module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
import pandas as pd

# Import custom modules
from validators import FormValidator
from analytics import StatisticalAnalyzer
from visualization import ChartGenerator
from storage import JSONStorage
from models import EnhancedDataRecord
from utils import timing_decorator, cache_decorator, DataBatchIterator, data_generator
from processing import DataProcessor

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize components
json_storage = JSONStorage('storage/json_data')
chart_generator = ChartGenerator('storage/charts')
data_processor = DataProcessor(num_workers=4, use_processes=True)

# In-memory job tracking
active_jobs = {}


def _load_dataframe(file_path: str) -> pd.DataFrame:
    """Load a dataframe from a supported file type."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ('.xlsx', '.xls'):
        return pd.read_excel(file_path)
    if ext == '.json':
        return pd.read_json(file_path)
    return pd.read_csv(file_path)


# ==================== USER REGISTRATION ENDPOINT ====================
@app.route('/api/register', methods=['POST'])
def register_user():
    """
    Register new user with form validation using regex
    Validates: name, email, phone, password
    """
    try:
        data = request.get_json()

        # Validate form using regex validator
        validation_result = FormValidator.validate_form(data)

        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'errors': validation_result['errors']
            }), 400

        # Create enhanced data record (demonstrates OOP)
        user_record = EnhancedDataRecord(
            id=str(uuid.uuid4()),
            value=1.0,
            tags=['user', 'registered']
        )
        user_record.set_metadata('name', data.get('name'))
        user_record.set_metadata('email', data.get('email'))
        user_record.set_metadata('phone', data.get('phone'))
        user_record.set_metadata('registration_date', datetime.now().isoformat())

        # Save to JSON storage
        json_storage.save(f"user_{user_record.id}", {
            'user_id': user_record.id,
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'full_info': user_record.get_full_info()
        })

        return jsonify({
            'success': True,
            'data': {
                'user_id': user_record.id,
                'message': 'User registered successfully',
                'mro': EnhancedDataRecord.get_mro()  # Show MRO
            }
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/info', methods=['GET'])
def get_info():
    """Return API metadata for client diagnostics."""
    return jsonify({
        'success': True,
        'data': {
            'name': 'Advanced Analytics Platform API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
    }), 200


# ==================== FILE UPLOAD ENDPOINT ====================
@app.route('/api/upload', methods=['POST'])
@timing_decorator  # Demonstrates decorator usage
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        job_id = str(uuid.uuid4())

        # Create upload directory
        upload_dir = './storage/uploads'
        os.makedirs(upload_dir, exist_ok=True)

        # Save file
        filename = f"{job_id}_{file.filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        # Store job info in JSON
        json_storage.save(f"job_{job_id}", {
            'job_id': job_id,
            'filename': filename,
            'file_path': os.path.abspath(file_path),
            'status': 'uploaded',
            'upload_time': datetime.now().isoformat()
        })

        return jsonify({
            'success': True,
            'data': {
                'job_id': job_id,
                'filename': filename,
                'file_path': os.path.abspath(file_path)
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/validate', methods=['POST'])
def validate_file():
    """Validate uploaded file and return preview/statistics for frontend."""
    try:
        payload = request.get_json() or {}
        file_path = payload.get('file_path')

        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404

        df = _load_dataframe(file_path)

        total_records = int(len(df))
        total_columns = int(len(df.columns))
        missing_values = int(df.isna().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        issues = []
        if duplicate_rows > 0:
            issues.append({'type': 'duplicates', 'message': f'Found {duplicate_rows} duplicate rows'})
        if missing_values > 0:
            issues.append({'type': 'missing_values', 'message': f'Found {missing_values} missing values'})

        quality_penalty = duplicate_rows + (missing_values // max(1, total_columns))
        quality_score = max(0, min(100, 100 - quality_penalty))

        return jsonify({
            'success': True,
            'data': {
                'file_path': file_path,
                'is_valid': len(issues) == 0,
                'validation_status': 'passed' if len(issues) == 0 else 'warning',
                'issues': issues,
                'quality_score': quality_score,
                'statistics': {
                    'total_records': total_records,
                    'total_columns': total_columns,
                    'missing_values': missing_values,
                    'duplicate_rows': duplicate_rows
                },
                'preview': {
                    'data': df.head(10).fillna('').to_dict(orient='records'),
                    'columns': list(df.columns)
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== DATA PROCESSING ENDPOINT (with Threading/Multiprocessing) ====================
@app.route('/api/process', methods=['POST'])
@timing_decorator
def process_file():
    """
    Process uploaded file with parallel processing
    Demonstrates: Threading/Multiprocessing, Generators, Iterators
    """
    job_id = str(uuid.uuid4())
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        job_id = data.get('job_id') or str(uuid.uuid4())

        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404

        active_jobs[job_id] = {
            'job_id': job_id,
            'status': 'processing',
            'progress': 10,
            'updated_at': datetime.now().isoformat()
        }

        # Read data into DataFrame
        df = _load_dataframe(file_path)

        # Create statistical analyzer
        analyzer = StatisticalAnalyzer(df)

        # Compute statistics (mean, median, std)
        statistics = analyzer.compute_all_statistics()

        # Generate charts using Matplotlib
        charts = chart_generator.create_statistics_visualization(statistics, job_id)

        # Save processed data using JSON storage
        processed_data = {
            'job_id': job_id,
            'file_path': file_path,
            'statistics': statistics,
            'chart_paths': charts,
            'dataset_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns)
            },
            'processing_time': datetime.now().isoformat()
        }

        json_storage.save(f"processed_{job_id}", processed_data)

        # Update job status
        json_storage.update(f"job_{job_id}", {'status': 'completed'})
        active_jobs[job_id] = {
            'job_id': job_id,
            'status': 'completed',
            'progress': 100,
            'updated_at': datetime.now().isoformat()
        }

        return jsonify({
            'success': True,
            'data': {
                'job_id': job_id,
                'status': 'completed',
                'message': 'File processed successfully'
            }
        }), 200

    except Exception as e:
        active_jobs[job_id] = {
            'job_id': job_id,
            'status': 'failed',
            'progress': 100,
            'error': str(e),
            'updated_at': datetime.now().isoformat()
        }
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/async/job/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Return asynchronous job status for polling."""
    job_state = active_jobs.get(job_id)
    if not job_state:
        stored = json_storage.load(f"job_{job_id}")
        if not stored:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        stored_data = stored.get('data', {})
        status = stored_data.get('status', 'completed')
        progress = 100 if status == 'completed' else 0
        job_state = {
            'job_id': job_id,
            'status': status,
            'progress': progress,
            'updated_at': stored.get('timestamp')
        }

    return jsonify({'success': True, 'data': job_state}), 200


@app.route('/api/async/stats', methods=['GET'])
def get_async_stats():
    """Return async worker and job counts."""
    statuses = [job.get('status') for job in active_jobs.values()]
    return jsonify({
        'success': True,
        'data': {
            'active_jobs': sum(1 for s in statuses if s == 'processing'),
            'completed_jobs': sum(1 for s in statuses if s == 'completed'),
            'failed_jobs': sum(1 for s in statuses if s == 'failed')
        }
    }), 200


@app.route('/api/async/queue', methods=['GET'])
def get_async_queue():
    """Return queue/worker status payload expected by frontend."""
    queue_length = sum(1 for job in active_jobs.values() if job.get('status') == 'processing')
    return jsonify({
        'success': True,
        'data': {
            'stats': {
                'active_workers': data_processor.num_workers,
                'queue_length': queue_length,
                'total_processed': sum(1 for job in active_jobs.values() if job.get('status') == 'completed')
            }
        }
    }), 200


# ==================== ANALYTICS ENDPOINT ====================
@app.route('/api/analytics/<job_id>', methods=['GET'])
def get_analytics(job_id):
    """
    Get analytics for processed job
    Demonstrates: Decorator, JSON storage retrieval
    """
    try:
        # Load processed data from JSON storage
        processed_data = json_storage.load(f"processed_{job_id}")

        if not processed_data:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        data = processed_data.get('data', {})
        statistics = data.get('statistics', {})

        dataset_info = data.get('dataset_info', {})
        total_records = int(dataset_info.get('rows', 0))
        total_columns = int(dataset_info.get('columns', 0))

        file_path = data.get('file_path')
        distribution = {}
        correlations = {}
        missing_analysis = {}
        duplicate_rows = 0

        # Recompute chart-friendly analytics from source file, but never fail the endpoint.
        if file_path and os.path.exists(file_path):
            try:
                df = _load_dataframe(file_path)

                total_records = int(len(df))
                total_columns = int(len(df.columns))
                duplicate_rows = int(df.duplicated().sum())

                for col in df.columns:
                    missing_analysis[col] = int(df[col].isna().sum())

                numeric_df = df.select_dtypes(include='number')
                for col in numeric_df.columns:
                    mean_val = numeric_df[col].mean()
                    if not pd.isna(mean_val):
                        distribution[col] = round(float(mean_val), 4)

                if len(numeric_df.columns) > 1:
                    corr_matrix = numeric_df.corr()
                    for col in corr_matrix.columns:
                        others = corr_matrix[col].drop(col)
                        avg_corr = others.abs().mean()
                        if not pd.isna(avg_corr):
                            correlations[col] = round(float(avg_corr), 4)
                elif len(numeric_df.columns) == 1:
                    correlations[numeric_df.columns[0]] = 1.0
            except Exception as calc_err:
                print(f"Analytics computation warning for {job_id}: {calc_err}")

        missing_total = int(sum(missing_analysis.values())) if missing_analysis else 0
        quality_score = max(0, min(100, 100 - (missing_total // max(1, len(missing_analysis)))))

        return jsonify({
            'success': True,
            'data': {
                'job_id': job_id,
                'statistics': {
                    'total_records': total_records,
                    'total_columns': total_columns,
                    'missing_values': missing_total,
                    'duplicate_rows': duplicate_rows
                },
                'distribution': distribution,
                'correlations': correlations,
                'missing_analysis': missing_analysis,
                'quality_score': quality_score,
                'charts_available': bool(data.get('chart_paths')),
                'raw_statistics': statistics
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/results/<job_id>', methods=['GET'])
def get_results(job_id):
    """Return processing results payload consumed by frontend."""
    try:
        processed_data = json_storage.load(f"processed_{job_id}")
        if not processed_data:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        data = processed_data.get('data', {})
        dataset_info = data.get('dataset_info', {})

        total_records = int(dataset_info.get('rows', 0))
        total_columns = int(dataset_info.get('columns', 0))
        missing_values = 0
        duplicate_rows = 0

        file_path = data.get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                df = _load_dataframe(file_path)
                missing_values = int(df.isna().sum().sum())
                duplicate_rows = int(df.duplicated().sum())
            except Exception as calc_err:
                print(f"Results overview warning for {job_id}: {calc_err}")

        return jsonify({
            'success': True,
            'data': {
                'job_id': job_id,
                'status': 'completed',
                'summary': f'Processed {total_records} records across {total_columns} columns.',
                'insights': [
                    f'Total rows analyzed: {total_records}',
                    f'Total columns analyzed: {total_columns}'
                ],
                'statistics': data.get('statistics', {}),
                'statistics_overview': {
                    'total_records': total_records,
                    'total_columns': total_columns,
                    'missing_values': missing_values,
                    'duplicate_rows': duplicate_rows
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/results/<job_id>/download', methods=['GET'])
def download_results(job_id):
    """Download summarized results as CSV."""
    try:
        processed_data = json_storage.load(f"processed_{job_id}")
        if not processed_data:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        data = processed_data.get('data', {})
        stats = data.get('statistics', {})
        dataset_info = data.get('dataset_info', {})

        output = io.StringIO()
        output.write('metric,value\n')
        output.write(f"job_id,{job_id}\n")
        output.write(f"rows,{dataset_info.get('rows', 0)}\n")
        output.write(f"columns,{dataset_info.get('columns', 0)}\n")
        for key, value in stats.items():
            output.write(f"{key},{value}\n")

        download_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        download_bytes.seek(0)
        return send_file(
            download_bytes,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"results_{job_id}.csv"
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/results/<job_id>/dashboard-pdf', methods=['GET'])
def download_dashboard_pdf(job_id):
    """Generate and download a simple dashboard summary PDF for a processed job."""
    try:
        processed_data = json_storage.load(f"processed_{job_id}")
        if not processed_data:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        data = processed_data.get('data', {})
        dataset_info = data.get('dataset_info', {})
        stats = data.get('statistics', {})

        rows = int(dataset_info.get('rows', 0))
        columns = int(dataset_info.get('columns', 0))

        # Compute lightweight quality indicators from source file when available.
        missing_values = 0
        duplicate_rows = 0
        file_path = data.get('file_path')
        if file_path and os.path.exists(file_path):
            try:
                df = _load_dataframe(file_path)
                missing_values = int(df.isna().sum().sum())
                duplicate_rows = int(df.duplicated().sum())
            except Exception as calc_err:
                print(f"PDF metrics warning for {job_id}: {calc_err}")

        quality_score = max(0, min(100, int(round(
            100 - (missing_values / max(rows * max(columns, 1), 1)) * 100 - duplicate_rows * 0.5
        ))))

        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch

        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        styles = getSampleStyleSheet()
        elements = [
            Paragraph('Analytics Dashboard Report', styles['Title']),
            Spacer(1, 0.2 * inch),
            Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']),
            Spacer(1, 0.2 * inch),
            Paragraph('Overview', styles['Heading2'])
        ]

        overview_table = Table([
            ['Metric', 'Value'],
            ['Job ID', job_id],
            ['Rows', str(rows)],
            ['Columns', str(columns)],
            ['Missing Values', str(missing_values)],
            ['Duplicate Rows', str(duplicate_rows)],
            ['Quality Score', f'{quality_score}%']
        ], colWidths=[2.2 * inch, 3.8 * inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f6fb')])
        ]))
        elements.append(overview_table)

        if stats:
            elements.extend([
                Spacer(1, 0.25 * inch),
                Paragraph('Statistics', styles['Heading2'])
            ])
            stat_rows = [['Metric', 'Value']]
            for key, value in stats.items():
                stat_rows.append([str(key), str(value)])
            stat_table = Table(stat_rows, colWidths=[2.2 * inch, 3.8 * inch])
            stat_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef7ef')])
            ]))
            elements.append(stat_table)

        doc.build(elements)
        pdf_buffer.seek(0)

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"dashboard_{job_id}.pdf"
        )

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== CHART RETRIEVAL ENDPOINT ====================
@app.route('/api/charts/<job_id>/<chart_type>', methods=['GET'])
def get_chart(job_id, chart_type):
    """
    Retrieve generated Matplotlib chart
    """
    try:
        # Load processed data
        processed_data = json_storage.load(f"processed_{job_id}")

        if not processed_data:
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        data = processed_data.get('data', {})
        charts = data.get('chart_paths', {})

        if chart_type not in charts:
            return jsonify({'success': False, 'error': 'Chart not found'}), 404

        chart_path = charts[chart_type]

        if not os.path.exists(chart_path):
            return jsonify({'success': False, 'error': 'Chart file not found'}), 404

        return send_file(chart_path, mimetype='image/png')

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== BATCH PROCESSING WITH GENERATOR ====================
@app.route('/api/batch-process', methods=['POST'])
def batch_process():
    """
    Batch process using generator (demonstrates generator usage)
    """
    try:
        data = request.get_json()
        items = data.get('items', [])

        if not items:
            return jsonify({'success': False, 'error': 'No items provided'}), 400

        # Use generator for memory-efficient processing
        processed_items = []

        for batch in data_generator(items, chunk_size=10):
            # Process each batch
            for item in batch:
                processed_items.append({
                    'original': item,
                    'processed': item.upper() if isinstance(item, str) else item * 2
                })

        return jsonify({
            'success': True,
            'data': {
                'processed_count': len(processed_items),
                'items': processed_items
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ITERATOR DEMONSTRATION ENDPOINT ====================
@app.route('/api/iterator-demo', methods=['GET'])
def iterator_demo():
    """
    Demonstrate custom iterator usage
    """
    try:
        # Create sample data
        data = list(range(1, 51))  # 1 to 50

        # Use custom iterator
        batch_iterator = DataBatchIterator(data, batch_size=10)

        batches = []
        for batch in batch_iterator:
            batches.append(batch)

        return jsonify({
            'success': True,
            'data': {
                'total_items': len(data),
                'batch_count': len(batches),
                'batches': batches
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== STORAGE STATS ENDPOINT ====================
@app.route('/api/storage/stats', methods=['GET'])
def get_storage_stats():
    """Get storage statistics"""
    try:
        stats = json_storage.get_statistics()
        all_keys = json_storage.list_all_keys()

        return jsonify({
            'success': True,
            'stats': stats,
            'total_items': len(all_keys),
            'keys': all_keys[:10]  # First 10 keys
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== HEALTH CHECK ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'data': {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'modules_loaded': [
                'validators', 'analytics', 'visualization',
                'storage', 'models', 'utils', 'processing'
            ]
        }
    }), 200


# ==================== FRONTEND ROUTES ====================
@app.route('/')
def serve_index():
    """Serve frontend"""
    return app.send_static_file('index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    try:
        return app.send_static_file(path)
    except:
        return app.send_static_file('index.html')


# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 60)
    print("Advanced Analytics Platform - Backend Server")
    print("=" * 60)
    print("Features:")
    print("  [+] Form validation with regex")
    print("  [+] Statistical analysis (mean, median, std)")
    print("  [+] Matplotlib chart generation")
    print("  [+] JSON storage system")
    print("  [+] Threading & Multiprocessing")
    print("  [+] Decorators, Generators, Iterators")
    print("  [+] Advanced OOP (ABC, Multiple Inheritance, Operator Overloading)")
    print("=" * 60)
    print(f"Server running on http://localhost:5000")
    print("=" * 60)

    # Create necessary directories
    os.makedirs('storage/uploads', exist_ok=True)
    os.makedirs('storage/charts', exist_ok=True)
    os.makedirs('storage/json_data', exist_ok=True)
    os.makedirs('storage/logs', exist_ok=True)

    app.run(host='0.0.0.0', port=5000, debug=True)
