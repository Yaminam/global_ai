/**
 * Application Logic
 * Main app controller and UI management
 */

const App = (() => {
    // State
    let currentFile = null;
    let currentJobId = null;
    let validationData = null;
    let processingData = null;
    let charts = {};

    // DOM Elements
    const elements = {
        // Upload
        dropZone: document.getElementById('dropZone'),
        fileInput: document.getElementById('fileInput'),
        fileInfo: document.getElementById('fileInfo'),
        fileName: document.getElementById('fileName'),
        fileSize: document.getElementById('fileSize'),
        clearFileBtn: document.getElementById('clearFileBtn'),
        validateBtn: document.getElementById('validateBtn'),
        validateSpinner: document.getElementById('validateSpinner'),
        processBtn: document.getElementById('processBtn'),
        processSpinner: document.getElementById('processSpinner'),
        
        // Messages
        statusMessage: document.getElementById('statusMessage'),
        errorMessage: document.getElementById('errorMessage'),
        
        // Preview
        previewSection: document.getElementById('preview'),
        validationResults: document.getElementById('validationResults'),
        validationStatus: document.getElementById('validationStatus'),
        validationContent: document.getElementById('validationContent'),
        tableHeader: document.getElementById('tableHeader'),
        tableBody: document.getElementById('tableBody'),
        dataTable: document.getElementById('dataTable'),
        noDataMessage: document.getElementById('noDataMessage'),
        
        // Dashboard
        dashboardSection: document.getElementById('dashboard'),
        processingStatus: document.getElementById('processingStatus'),
        progressFill: document.getElementById('progressFill'),
        statusText: document.getElementById('statusText'),
        jobId: document.getElementById('jobId'),
        jobStatus: document.getElementById('jobStatus'),
        statsCards: document.getElementById('statsCards'),
        statRecords: document.getElementById('statRecords'),
        statColumns: document.getElementById('statColumns'),
        statMissing: document.getElementById('statMissing'),
        statDuplicates: document.getElementById('statDuplicates'),
        chartsSection: document.getElementById('chartsSection'),
        resultsSection: document.getElementById('resultsSection'),
        resultsContent: document.getElementById('resultsContent'),
        downloadBtn: document.getElementById('downloadBtn'),
        downloadDashboardBtn: document.getElementById('downloadDashboardBtn'),
        newAnalysisBtn: document.getElementById('newAnalysisBtn'),
        
        // API Status
        apiStatusBadge: document.getElementById('apiStatusBadge'),
        workersBadge: document.getElementById('workersBadge'),
        storageBadge: document.getElementById('storageBadge'),
        healthBtn: document.getElementById('healthBtn'),
        refreshStatusBtn: document.getElementById('refreshStatusBtn')
    };

    /**
     * Initialize the application
     */
    function init() {
        setupEventListeners();
        checkAPIHealth();
        setInterval(checkAPIHealth, 30000); // Check every 30 seconds
    }

    /**
     * Setup all event listeners
     */
    function setupEventListeners() {
        // Drag and drop
        elements.dropZone.addEventListener('dragover', handleDragOver);
        elements.dropZone.addEventListener('dragleave', handleDragLeave);
        elements.dropZone.addEventListener('drop', handleDrop);
        elements.dropZone.addEventListener('click', () => elements.fileInput.click());
        elements.fileInput.addEventListener('change', handleFileSelect);

        // File actions
        elements.clearFileBtn.addEventListener('click', clearFile);
        elements.validateBtn.addEventListener('click', validateData);
        elements.processBtn.addEventListener('click', processData);

        // Dashboard
        elements.downloadBtn.addEventListener('click', downloadResults);
        elements.downloadDashboardBtn.addEventListener('click', downloadDashboardPDF);
        elements.newAnalysisBtn.addEventListener('click', newAnalysis);

        // Health check
        elements.healthBtn.addEventListener('click', checkAPIHealth);
        elements.refreshStatusBtn.addEventListener('click', checkAPIHealth);
    }

    /**
     * Handle drag over
     */
    function handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        elements.dropZone.classList.add('dragover');
    }

    /**
     * Handle drag leave
     */
    function handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        elements.dropZone.classList.remove('dragover');
    }

    /**
     * Handle drop
     */
    function handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        elements.dropZone.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect({ target: { files } });
        }
    }

    /**
     * Handle file selection
     */
    async function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length === 0) return;

        const file = files[0];

        // Validate file type
        if (!API.isValidFileType(file)) {
            showError('Invalid file type. Please upload CSV, JSON, or Excel files.');
            return;
        }

        // Validate file size (max 100MB)
        const maxSize = 100 * 1024 * 1024;
        if (file.size > maxSize) {
            showError('File is too large. Maximum size is 100MB.');
            return;
        }

        currentFile = file;
        updateFileInfo();
        elements.validateBtn.disabled = false;
        showStatus(`File selected: ${file.name} (${API.formatFileSize(file.size)})`);
    }

    /**
     * Update file info display
     */
    function updateFileInfo() {
        elements.fileName.textContent = currentFile.name;
        elements.fileSize.textContent = API.formatFileSize(currentFile.size);
        elements.fileInfo.classList.remove('hidden');
    }

    /**
     * Clear selected file
     */
    function clearFile() {
        currentFile = null;
        validationData = null;
        elements.fileInput.value = '';
        elements.fileInfo.classList.add('hidden');
        elements.validateBtn.disabled = true;
        elements.processBtn.disabled = true;
        elements.previewSection.classList.add('hidden');
        clearMessages();
    }

    /**
     * Validate data
     */
    async function validateData() {
        if (!currentFile) {
            showError('No file selected');
            return;
        }

        try {
            setButtonLoading(elements.validateBtn, true);
            
            // Upload file first
            showStatus('Uploading file...');
            const uploadResult = await API.uploadFile(currentFile);
            
            console.log('Upload result:', uploadResult);
            
            if (!uploadResult.success) {
                throw new Error(uploadResult.error);
            }

            console.log('Response data:', uploadResult.data);
            console.log('Nested data:', uploadResult.data.data);
            
            const filePath = uploadResult.data.data?.file_path;
            
            if (!filePath) {
                throw new Error('File path not found in upload response. Response: ' + JSON.stringify(uploadResult.data));
            }
            
            showStatus('Validating data...');

            // Validate data
            const validateResult = await API.validateData(filePath);
            
            if (!validateResult.success) {
                throw new Error(validateResult.error);
            }

            validationData = validateResult.data.data;
            displayValidationResults();
            showStatus('Data validated successfully!');
            elements.processBtn.disabled = false;

        } catch (error) {
            showError(`Validation failed: ${error.message}`);
        } finally {
            setButtonLoading(elements.validateBtn, false);
        }
    }

    /**
     * Display validation results
     */
    function displayValidationResults() {
        const { is_valid, issues, statistics, preview } = validationData;

        // Show validation status
        elements.validationStatus.className = 'status-badge ' + (is_valid ? 'success' : 'warning');
        elements.validationStatus.textContent = is_valid ? 'Valid' : 'Has Issues';

        // Generate validation content
        let content = '<ul>';
        if (issues && issues.length > 0) {
            issues.forEach(issue => {
                content += `<li><strong>${issue.type}:</strong> ${issue.message}</li>`;
            });
        } else {
            content += '<li>No data quality issues detected</li>';
        }
        content += '</ul>';

        if (statistics) {
            content += `<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e2e8f0;">
                <strong>Statistics:</strong><br>
                Records: ${statistics.total_records || 0}<br>
                Columns: ${statistics.total_columns || 0}<br>
                Missing Values: ${statistics.missing_values || 0}<br>
                Duplicates: ${statistics.duplicate_rows || 0}
            </div>`;
        }

        elements.validationContent.innerHTML = content;
        elements.validationResults.classList.remove('hidden');

        // Display data preview
        if (preview && preview.data) {
            displayDataPreview(preview.data, preview.columns);
        }

        elements.previewSection.classList.remove('hidden');
    }

    /**
     * Display data preview table
     */
    function displayDataPreview(data, columns) {
        // Clear table
        elements.tableHeader.innerHTML = '';
        elements.tableBody.innerHTML = '';

        if (!columns || columns.length === 0) {
            elements.noDataMessage.style.display = 'block';
            return;
        }

        // Add header
        columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col;
            elements.tableHeader.appendChild(th);
        });

        // Add rows (limit to 10)
        const rowsToShow = Math.min(data.length, 10);
        for (let i = 0; i < rowsToShow; i++) {
            const row = data[i];
            const tr = document.createElement('tr');
            
            columns.forEach(col => {
                const td = document.createElement('td');
                const value = row[col];
                td.textContent = value !== null && value !== undefined ? value : '-';
                tr.appendChild(td);
            });
            
            elements.tableBody.appendChild(tr);
        }

        if (data.length > 10) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = columns.length;
            td.style.textAlign = 'center';
            td.style.color = '#64748b';
            td.textContent = `... and ${data.length - 10} more rows`;
            tr.appendChild(td);
            elements.tableBody.appendChild(tr);
        }

        elements.noDataMessage.style.display = 'none';
    }

    /**
     * Process data
     */
    async function processData() {
        if (!validationData) {
            showError('Please validate data first');
            return;
        }

        try {
            setButtonLoading(elements.processBtn, true);
            showStatus('Starting processing...');

            // Extract file path from validation data
            const filePath = validationData.file_path || validationData.preview?.file_path;
            
            if (!filePath) {
                throw new Error('File path not found');
            }

            // Start processing
            const processResult = await API.processData(filePath, {
                normalize: true,
                removeDuplicates: true,
                fillMissing: true
            });

            console.log('Process result:', processResult);

            if (!processResult.success) {
                throw new Error(processResult.error);
            }

            console.log('Process data:', processResult.data);
            console.log('Job ID value:', processResult.data.data?.job_id);
            
            currentJobId = processResult.data.data?.job_id;
            
            if (!currentJobId) {
                throw new Error('Job ID not returned from server. Response: ' + JSON.stringify(processResult));
            }
            
            // Update Job ID display
            elements.jobId.textContent = currentJobId;
            showDashboard();
            showStatus(`Processing started. Job ID: ${currentJobId}`);
            
            // Poll job status
            pollJobProgress();

        } catch (error) {
            showError(`Processing failed: ${error.message}`);
        } finally {
            setButtonLoading(elements.processBtn, false);
        }
    }

    /**
     * Poll job progress
     */
    async function pollJobProgress() {
        try {
            elements.processingStatus.classList.remove('hidden');
            let progress = 0;

            await API.pollJobStatus(currentJobId, (status) => {
                // Update progress
                progress = status.progress || 0;
                elements.progressFill.style.width = progress + '%';
                
                // Update status text
                elements.statusText.textContent = `${status.status} (${progress}%)`;
                elements.jobStatus.textContent = status.status.toUpperCase();
                elements.jobStatus.className = 'status-badge ' + getStatusClass(status.status);

                if (status.status === 'completed') {
                    showStatus('Processing completed successfully!');
                    displayResults(status);
                } else if (status.status === 'failed') {
                    showError(`Processing failed: ${status.error || 'Unknown error'}`);
                }
            });

        } catch (error) {
            showError(`Error polling job status: ${error.message}`);
        }
    }

    /**
     * Get status badge class
     */
    function getStatusClass(status) {
        const statusMap = {
            'queued': 'warning',
            'processing': 'warning',
            'completed': 'success',
            'failed': 'error'
        };
        return statusMap[status] || 'disconnected';
    }

    /**
     * Display processing results
     */
    async function displayResults(jobStatus) {
        try {
            // Get analytics data
            const analyticsResult = await API.getAnalytics(currentJobId);
            
            if (analyticsResult.success) {
                processingData = analyticsResult.data.data;
                displayStatistics();
                displayCharts();
            } else {
                showError(`Analytics unavailable: ${analyticsResult.error}`);
            }

            // Get results
            const resultsResult = await API.getResults(currentJobId);
            
            if (resultsResult.success) {
                displayResultsContent(resultsResult.data.data);
            }

            elements.statsCards.classList.remove('hidden');
            elements.resultsSection.classList.remove('hidden');

        } catch (error) {
            showError(`Error displaying results: ${error.message}`);
        }
    }

    /**
     * Display statistics
     */
    function displayStatistics() {
        if (!processingData) return;

        const stats = processingData.statistics || {};
        elements.statRecords.textContent = stats.total_records || 0;
        elements.statColumns.textContent = stats.total_columns || 0;
        elements.statMissing.textContent = stats.missing_values || 0;
        elements.statDuplicates.textContent = stats.duplicate_rows || 0;
    }

    /**
     * Display charts
     */
    function displayCharts() {
        if (!processingData) return;

        elements.chartsSection.classList.remove('hidden');

        // Distribution Chart
        try {
            const distData = processingData.distribution || {};
            createChart('distributionChart', 'bar', distData);
        } catch (e) {
            console.error('Error creating distribution chart:', e);
        }

        // Correlation Chart
        try {
            const corrData = processingData.correlations || {};
            createChart('correlationChart', 'scatter', corrData);
        } catch (e) {
            console.error('Error creating correlation chart:', e);
        }

        // Missing Values Chart
        try {
            const missingData = processingData.missing_analysis || {};
            createChart('missingChart', 'bar', missingData);
        } catch (e) {
            console.error('Error creating missing chart:', e);
        }

        // Quality Chart
        try {
            const qualityScore = processingData.quality_score || 0;
            createQualityChart('qualityChart', qualityScore);
        } catch (e) {
            console.error('Error creating quality chart:', e);
        }
    }

    /**
     * Create chart using Chart.js
     */
    function createChart(canvasId, type, data) {
        // Destroy existing chart if it exists
        if (charts[canvasId]) {
            charts[canvasId].destroy();
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const labels = Object.keys(data).slice(0, 10);
        const values = Object.values(data).slice(0, 10);

        const chartType = type === 'scatter' ? 'bar' : type;

        const chartConfig = {
            type: chartType,
            data: {
                labels: labels,
                datasets: [{
                    label: 'Data',
                    data: values,
                    backgroundColor: 'rgba(59, 130, 246, 0.6)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            font: { size: 12 }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        };

        charts[canvasId] = new Chart(ctx, chartConfig);
    }

    /**
     * Create quality score chart
     */
    function createQualityChart(canvasId, score) {
        if (charts[canvasId]) {
            charts[canvasId].destroy();
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const normalizedScore = Math.min(Math.max(score, 0), 100);

        charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Quality Score', 'Remaining'],
                datasets: [{
                    data: [normalizedScore, 100 - normalizedScore],
                    backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',
                        'rgba(226, 232, 240, 0.5)'
                    ],
                    borderColor: ['rgba(16, 185, 129, 1)', 'rgba(226, 232, 240, 1)'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                if (context.dataIndex === 0) {
                                    return `Quality: ${normalizedScore.toFixed(1)}%`;
                                }
                                return '';
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Display results content
     */
    function displayResultsContent(results) {
        let html = '';
        
        if (results.summary) {
            html += `
                <div class="results-item">
                    <h4>Processing Summary</h4>
                    <p>${results.summary}</p>
                </div>
            `;
        }

        if (results.insights) {
            html += `
                <div class="results-item">
                    <h4>Key Insights</h4>
                    <ul>
                        ${Array.isArray(results.insights) 
                            ? results.insights.map(i => `<li>${i}</li>`).join('') 
                            : `<li>${results.insights}</li>`
                        }
                    </ul>
                </div>
            `;
        }

        if (html) {
            elements.resultsContent.innerHTML = html;
        }
    }

    /**
     * Download results
     */
    async function downloadResults() {
        if (!currentJobId) {
            showError('No job to download');
            return;
        }

        try {
            showStatus('Downloading results...');
            await API.downloadResults(currentJobId, 'csv');
            showStatus('Results downloaded successfully!');
        } catch (error) {
            showError(`Download failed: ${error.message}`);
        }
    }

    /**
     * Download dashboard as PDF
     */
    async function downloadDashboardPDF() {
        if (!currentJobId) {
            showError('No dashboard to download');
            return;
        }

        try {
            showStatus('Generating dashboard PDF...');
            await API.downloadDashboardPDF(currentJobId);
            showStatus('Dashboard PDF downloaded successfully!');
        } catch (error) {
            showError(`PDF download failed: ${error.message}`);
        }
    }

    /**
     * Start new analysis
     */
    function newAnalysis() {
        clearFile();
        elements.dashboardSection.classList.add('hidden');
        elements.previewSection.classList.add('hidden');
        currentJobId = null;
        validationData = null;
        processingData = null;
        Object.values(charts).forEach(chart => chart?.destroy?.());
        charts = {};
        showStatus('Ready for new analysis');
    }

    /**
     * Show dashboard section
     */
    function showDashboard() {
        elements.dashboardSection.classList.remove('hidden');
    }

    /**
     * Check API health
     */
    async function checkAPIHealth() {
        try {
            const healthResult = await API.checkHealth();
            const queueResult = await API.getQueueStatus();
            const storageResult = await API.getStorageStats();

            if (healthResult.success) {
                elements.apiStatusBadge.className = 'status-badge success';
                elements.apiStatusBadge.textContent = 'Connected';
            } else {
                throw new Error('Health check failed');
            }

            if (queueResult.success) {
                const workers = queueResult.data.data?.stats?.active_workers || 0;
                elements.workersBadge.textContent = `${workers} active`;
                elements.workersBadge.className = 'status-badge ' + (workers > 0 ? 'success' : 'warning');
            }

            if (storageResult.success) {
                elements.storageBadge.textContent = 'OK';
                elements.storageBadge.className = 'status-badge success';
            }

        } catch (error) {
            elements.apiStatusBadge.className = 'status-badge disconnected';
            elements.apiStatusBadge.textContent = 'Disconnected';
            elements.workersBadge.textContent = '-';
            elements.storageBadge.textContent = '-';
        }
    }

    /**
     * Show status message
     */
    function showStatus(message) {
        elements.statusMessage.textContent = message;
        elements.statusMessage.classList.remove('hidden');
        elements.errorMessage.classList.add('hidden');
        setTimeout(() => {
            elements.statusMessage.classList.add('hidden');
        }, 5000);
    }

    /**
     * Show error message
     */
    function showError(message) {
        elements.errorMessage.textContent = message;
        elements.errorMessage.classList.remove('hidden');
        elements.statusMessage.classList.add('hidden');
        setTimeout(() => {
            elements.errorMessage.classList.add('hidden');
        }, 7000);
    }

    /**
     * Clear messages
     */
    function clearMessages() {
        elements.statusMessage.classList.add('hidden');
        elements.errorMessage.classList.add('hidden');
    }

    /**
     * Set button loading state
     */
    function setButtonLoading(button, isLoading) {
        const spinner = button.querySelector('.spinner');
        const text = button.querySelector('.btn-text');
        
        if (isLoading) {
            text.style.display = 'none';
            spinner.classList.remove('hidden');
            button.disabled = true;
        } else {
            text.style.display = 'inline';
            spinner.classList.add('hidden');
            button.disabled = false;
        }
    }

    /**
     * Public API
     */
    return {
        init
    };
})();

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', App.init);
