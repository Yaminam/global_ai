/**
 * Application Logic
 * Main app controller and UI management
 */

const App = (() => {
    // State
    let isRegistered = false;
    let currentFile = null;
    let currentJobId = null;
    let validationData = null;
    let processingData = null;
    let charts = {};

    // DOM Elements
    const elements = {
        // Registration
        registerSection: document.getElementById('register'),
        registrationForm: document.getElementById('registrationForm'),
        regName: document.getElementById('regName'),
        regEmail: document.getElementById('regEmail'),
        regPhone: document.getElementById('regPhone'),
        regPassword: document.getElementById('regPassword'),
        registerBtn: document.getElementById('registerBtn'),
        registerSpinner: document.getElementById('registerSpinner'),
        clearFormBtn: document.getElementById('clearFormBtn'),
        registrationSuccess: document.getElementById('registrationSuccess'),
        regSuccessDetails: document.getElementById('regSuccessDetails'),
        nameError: document.getElementById('nameError'),
        emailError: document.getElementById('emailError'),
        phoneError: document.getElementById('phoneError'),
        passwordError: document.getElementById('passwordError'),

        // Upload
    uploadSection: document.getElementById('upload'),
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

        // Messages (toast)
        statusMessage: document.getElementById('statusMessage'),
        errorMessage: document.getElementById('errorMessage'),
        statusText2: document.getElementById('statusText2'),
        errorText2: document.getElementById('errorText2'),

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
        refreshStatusBtn: document.getElementById('refreshStatusBtn'),

        // Steps
        step1: document.getElementById('step1'),
        step2: document.getElementById('step2'),
        step3: document.getElementById('step3'),
        stepLines: document.querySelectorAll('.step-connector'),
    };

    /**
     * Initialize the application
     */
    function init() {
        isRegistered = false;
        applyRegistrationGate();
        setupEventListeners();
        checkAPIHealth();
        setInterval(checkAPIHealth, 30000); // Check every 30 seconds
    }

    function applyRegistrationGate() {
        if (!elements.registerSection || !elements.uploadSection) return;

        const navLinks = document.querySelectorAll('.nav-a');

        if (!isRegistered) {
            elements.registerSection.classList.remove('hidden');
            elements.uploadSection.classList.add('hidden');
            elements.previewSection.classList.add('hidden');
            elements.dashboardSection.classList.add('hidden');
            navLinks.forEach((link) => {
                const target = (link.getAttribute('href') || '').replace('#', '');
                if (target !== 'register') {
                    link.classList.add('nav-a-disabled');
                    link.setAttribute('aria-disabled', 'true');
                }
            });
            return;
        }

        elements.registerSection.classList.add('hidden');
        elements.uploadSection.classList.remove('hidden');
        navLinks.forEach((link) => {
            link.classList.remove('nav-a-disabled');
            link.removeAttribute('aria-disabled');
        });
    }

    /**
     * Setup all event listeners
     */
    function setupEventListeners() {
        // Registration form
        if (elements.registrationForm) {
            elements.registrationForm.addEventListener('submit', handleRegistration);
            elements.clearFormBtn.addEventListener('click', clearRegistrationForm);
        }

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
        const footerRefreshBtn = document.getElementById('footerRefreshBtn');
        if (footerRefreshBtn) footerRefreshBtn.addEventListener('click', (e) => { e.preventDefault(); checkAPIHealth(); });
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
        if (!isRegistered) {
            showError('Please complete registration first.');
            return;
        }

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
        setStep(1);
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
        if (!isRegistered) {
            showError('Please complete registration first.');
            return;
        }

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
            setStep(2);
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
        elements.validationStatus.className = 'badge ' + (is_valid ? 'badge-ok' : 'badge-warn');
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
        if (!isRegistered) {
            showError('Please complete registration first.');
            return;
        }

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
            setStep(3);
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
                elements.jobStatus.className = 'badge ' + getStatusClass(status.status);

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
            'queued':     'badge-warn',
            'processing': 'badge-warn',
            'completed':  'badge-ok',
            'failed':     'badge-err'
        };
        return statusMap[status] || 'badge-muted';
    }

    /**
     * Display processing results
     */
    async function displayResults(jobStatus) {
        try {
            // Get analytics data
            const analyticsResult = await API.getAnalytics(currentJobId);
            const resultsResult = await API.getResults(currentJobId);

            const overview = resultsResult.success
                ? (resultsResult.data.data?.statistics_overview || null)
                : null;
            
            if (analyticsResult.success) {
                processingData = analyticsResult.data.data;
            } else {
                showError(`Analytics unavailable: ${analyticsResult.error}`);
                processingData = {
                    statistics: overview || {
                        total_records: 0,
                        total_columns: 0,
                        missing_values: 0,
                        duplicate_rows: 0
                    },
                    distribution: {},
                    correlations: {},
                    missing_analysis: {},
                    quality_score: 0
                };
            }

            // Fill any missing analytics summary fields from results overview.
            if (processingData && overview) {
                processingData.statistics = {
                    total_records: processingData.statistics?.total_records ?? overview.total_records,
                    total_columns: processingData.statistics?.total_columns ?? overview.total_columns,
                    missing_values: processingData.statistics?.missing_values ?? overview.missing_values,
                    duplicate_rows: processingData.statistics?.duplicate_rows ?? overview.duplicate_rows
                };
            }

            // Final guard: if backend returned zeros, prefer known validation stats.
            if (processingData && validationData?.statistics) {
                const stats = processingData.statistics || {};
                const statsAreZero = Number(stats.total_records || 0) === 0 && Number(stats.total_columns || 0) === 0;
                const validationHasData = Number(validationData.statistics.total_records || 0) > 0;
                if (statsAreZero && validationHasData) {
                    processingData.statistics = {
                        total_records: validationData.statistics.total_records || 0,
                        total_columns: validationData.statistics.total_columns || 0,
                        missing_values: validationData.statistics.missing_values || 0,
                        duplicate_rows: validationData.statistics.duplicate_rows || 0
                    };
                    if (!processingData.quality_score || Number(processingData.quality_score) === 0) {
                        processingData.quality_score = validationData.quality_score || 0;
                    }
                }
            }

            displayStatistics();
            displayCharts();

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

        let stats = processingData.statistics || {};
        const hasDashboardStats = Number(stats.total_records || 0) > 0 || Number(stats.total_columns || 0) > 0;
        const hasValidationStats = Number(validationData?.statistics?.total_records || 0) > 0 || Number(validationData?.statistics?.total_columns || 0) > 0;

        if (!hasDashboardStats && hasValidationStats) {
            stats = validationData.statistics;
            processingData.statistics = stats;
        }

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
        const stats = processingData.statistics || {};

        // Distribution Chart — mean value per numeric column
        try {
            const distData = processingData.distribution || {};
            if (Object.keys(distData).length > 0) {
                createBarChart('distributionChart', distData, 'Mean Value', 'Column', 'Mean');
            } else {
                hideChart('distributionChart', 'No numeric columns found');
            }
        } catch (e) {
            console.error('Error creating distribution chart:', e);
        }

        // Correlation Chart — avg correlation per numeric column
        try {
            const corrData = processingData.correlations || {};
            if (Object.keys(corrData).length > 0) {
                createBarChart('correlationChart', corrData, 'Avg Correlation', 'Column', 'Correlation', 'rgba(139, 92, 246, 0.6)', 'rgba(139, 92, 246, 1)');
            } else {
                hideChart('correlationChart', 'No numeric columns for correlation');
            }
        } catch (e) {
            console.error('Error creating correlation chart:', e);
        }

        // Missing Values Chart — missing count per column
        try {
            let missingData = processingData.missing_analysis || {};
            if (Object.keys(missingData).length === 0 && Number(stats.missing_values || 0) > 0) {
                // Fallback when per-column breakdown is unavailable.
                missingData = { 'Total Missing Values': Number(stats.missing_values || 0) };
            }
            if (Object.keys(missingData).length > 0) {
                createBarChart('missingChart', missingData, 'Missing Values per Column', 'Column', 'Missing Count', 'rgba(239, 68, 68, 0.6)', 'rgba(239, 68, 68, 1)');
            } else {
                hideChart('missingChart', 'No missing value data');
            }
        } catch (e) {
            console.error('Error creating missing chart:', e);
        }

        // Quality Chart
        try {
            let qualityScore = Number(processingData.quality_score || 0);
            if ((!qualityScore || qualityScore <= 0) && (stats.total_records || stats.total_columns)) {
                const missing = Number(stats.missing_values || 0);
                const rows = Math.max(1, Number(stats.total_records || 1));
                const cols = Math.max(1, Number(stats.total_columns || 1));
                const density = missing / (rows * cols);
                qualityScore = Math.max(0, Math.min(100, Math.round((1 - density) * 100)));
            }
            createQualityChart('qualityChart', qualityScore);
        } catch (e) {
            console.error('Error creating quality chart:', e);
        }
    }

    /**
     * Create a bar chart with proper axis labels from actual data keys
     */
    function createBarChart(canvasId, data, title, xLabel, yLabel, bgColor, borderColor) {
        if (charts[canvasId]) {
            charts[canvasId].destroy();
        }

        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const container = canvas.parentElement;

        // Reset no-data placeholder state from previous runs.
        canvas.style.display = 'block';
        if (container) {
            container.querySelectorAll('.chart-empty-msg').forEach((el) => el.remove());
        }

        bgColor = bgColor || 'rgba(59, 130, 246, 0.6)';
        borderColor = borderColor || 'rgba(59, 130, 246, 1)';

        const labels = Object.keys(data);
        const values = Object.values(data);

        charts[canvasId] = new Chart(canvas.getContext('2d'), {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: yLabel || 'Value',
                    data: values,
                    backgroundColor: bgColor,
                    borderColor: borderColor,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true },
                    title: {
                        display: !!title,
                        text: title,
                        font: { size: 13 }
                    }
                },
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: xLabel || 'Column'
                        },
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0,
                            autoSkip: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: yLabel || 'Value'
                        }
                    }
                }
            }
        });
    }

    /**
     * Show a placeholder message when chart has no data
     */
    function hideChart(canvasId, message) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        const container = canvas.parentElement;
        canvas.style.display = 'none';
        if (container) {
            container.querySelectorAll('.chart-empty-msg').forEach((el) => el.remove());
        }
        const msg = document.createElement('p');
        msg.className = 'chart-empty-msg';
        msg.style.cssText = 'color:#94a3b8;text-align:center;padding:2rem;';
        msg.textContent = message;
        container.appendChild(msg);
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
        const container = canvas.parentElement;

        canvas.style.display = 'block';
        if (container) {
            container.querySelectorAll('.chart-empty-msg').forEach((el) => el.remove());
        }

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
        setStep(1);
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
                elements.apiStatusBadge.className = 'badge badge-ok';
                elements.apiStatusBadge.textContent = 'Connected';
            } else {
                throw new Error('Health check failed');
            }

            if (queueResult.success) {
                const workers = queueResult.data.data?.stats?.active_workers || 0;
                elements.workersBadge.textContent = `${workers} active`;
                elements.workersBadge.className = 'badge ' + (workers > 0 ? 'badge-ok' : 'badge-warn');
            }

            if (storageResult.success) {
                elements.storageBadge.textContent = 'OK';
                elements.storageBadge.className = 'badge badge-ok';
            }

        } catch (error) {
            elements.apiStatusBadge.className = 'badge badge-err';
            elements.apiStatusBadge.textContent = 'Disconnected';
            elements.workersBadge.textContent = '—';
            elements.storageBadge.textContent = '—';
        }
    }

    /**
     * Show status toast
     */
    function showStatus(message) {
        if (elements.statusText2) elements.statusText2.textContent = message;
        elements.statusMessage.classList.remove('hidden');
        elements.errorMessage.classList.add('hidden');
        setTimeout(() => elements.statusMessage.classList.add('hidden'), 5000);
    }

    /**
     * Show error toast
     */
    function showError(message) {
        if (elements.errorText2) elements.errorText2.textContent = message;
        elements.errorMessage.classList.remove('hidden');
        elements.statusMessage.classList.add('hidden');
        setTimeout(() => elements.errorMessage.classList.add('hidden'), 7000);
    }

    /**
     * Unified message helper used by registration flow
     */
    function showMessage(message, type = 'success') {
        if (type === 'error') {
            showError(message);
            return;
        }
        showStatus(message);
    }

    /**
     * Handle registration form submission
     */
    async function handleRegistration(e) {
        e.preventDefault();

        // Clear previous errors
        clearFormErrors();
        elements.registrationSuccess.classList.add('hidden');

        // Get form data
        const formData = {
            name: elements.regName.value.trim(),
            email: elements.regEmail.value.trim(),
            phone: elements.regPhone.value.trim(),
            password: elements.regPassword.value
        };

        // Set loading state
        setButtonLoading(elements.registerBtn, true);

        try {
            const response = await API.register(formData);

            if (response.success) {
                // Show success message
                elements.regSuccessDetails.textContent =
                    `User ID: ${response.data.user_id} | ${response.data.message}`;
                elements.registrationSuccess.classList.remove('hidden');

                // Clear form
                elements.registrationForm.reset();

                isRegistered = true;
                applyRegistrationGate();

                if (elements.uploadSection) {
                    elements.uploadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }

                // Show success toast
                showMessage(`Registration successful! Welcome, ${formData.name}`, 'success');
            } else {
                // Handle validation errors
                if (response.errors) {
                    Object.keys(response.errors).forEach(field => {
                        const errorElement = document.getElementById(`${field}Error`);
                        const inputElement = document.getElementById(`reg${field.charAt(0).toUpperCase() + field.slice(1)}`);

                        if (errorElement && inputElement) {
                            errorElement.textContent = response.errors[field];
                            inputElement.classList.add('error');
                        }
                    });
                }
                showMessage(response.error || 'Registration failed', 'error');
            }
        } catch (error) {
            showMessage('Registration failed: ' + error.message, 'error');
        } finally {
            setButtonLoading(elements.registerBtn, false);
        }
    }

    /**
     * Clear registration form
     */
    function clearRegistrationForm() {
        elements.registrationForm.reset();
        clearFormErrors();
        elements.registrationSuccess.classList.add('hidden');
    }

    /**
     * Clear form validation errors
     */
    function clearFormErrors() {
        ['nameError', 'emailError', 'phoneError', 'passwordError'].forEach(errorId => {
            const errorElement = document.getElementById(errorId);
            if (errorElement) {
                errorElement.textContent = '';
            }
        });

        ['regName', 'regEmail', 'regPhone', 'regPassword'].forEach(inputId => {
            const inputElement = document.getElementById(inputId);
            if (inputElement) {
                inputElement.classList.remove('error');
            }
        });
    }

    /**
     * Clear messages
     */
    function clearMessages() {
        elements.statusMessage.classList.add('hidden');
        elements.errorMessage.classList.add('hidden');
    }

    /**
     * Update step indicator
     */
    function setStep(n) {
        [elements.step1, elements.step2, elements.step3].forEach((el, i) => {
            if (!el) return;
            el.classList.toggle('active', i + 1 === n);
            el.classList.toggle('done', i + 1 < n);
        });
        elements.stepLines.forEach((line, i) => {
            line.classList.toggle('done', i + 1 < n);
        });
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
