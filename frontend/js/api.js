/**
 * API Integration Module
 * Handles all communication with the Flask backend
 */

const API = (() => {
    // API Configuration
    // Use same origin for API calls (works for both dev and production)
    const API_BASE_URL = window.location.origin + '/api';
    const POLL_INTERVAL = 2000; // 2 seconds
    const POLL_TIMEOUT = 300000; // 5 minutes

    // Helper function to make API requests
    async function request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, defaultOptions);
            
            // Handle non-JSON responses
            const contentType = response.headers.get('content-type');
            let data;
            
            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                throw new Error(data.error || data.message || `HTTP ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Check API health
     */
    async function checkHealth() {
        try {
            const response = await request('/health');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get API information
     */
    async function getInfo() {
        try {
            const response = await request('/info');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Upload file and get metadata
     */
    async function uploadFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: 'POST',
                body: formData
                // Important: Don't set Content-Type header for FormData
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || data.message || 'Upload failed');
            }

            console.log('Upload response:', data);

            return {
                success: true,
                data: data
            };
        } catch (error) {
            console.error('Upload Error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Validate uploaded data
     */
    async function validateData(filePath) {
        try {
            const response = await request('/validate', {
                method: 'POST',
                body: JSON.stringify({
                    file_path: filePath,
                    check_duplicates: true,
                    check_missing: true
                })
            });

            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Process data asynchronously
     */
    async function processData(filePath, options = {}) {
        try {
            const response = await request('/process', {
                method: 'POST',
                body: JSON.stringify({
                    file_path: filePath,
                    config: {
                        normalize: options.normalize !== false,
                        remove_duplicates: options.removeDuplicates !== false,
                        fill_missing: options.fillMissing !== false,
                        ...options
                    }
                })
            });

            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get async job status
     */
    async function getJobStatus(jobId) {
        try {
            const response = await request(`/async/job/${jobId}`);
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get async statistics
     */
    async function getAsyncStats() {
        try {
            const response = await request('/async/stats');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get queue status
     */
    async function getQueueStatus() {
        try {
            const response = await request('/async/queue');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get storage statistics
     */
    async function getStorageStats() {
        try {
            const response = await request('/storage/stats');
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Poll job status until completion
     */
    async function pollJobStatus(jobId, onUpdate = null) {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();
            let isResolved = false;

            const poll = async () => {
                try {
                    if (Date.now() - startTime > POLL_TIMEOUT) {
                        if (!isResolved) {
                            isResolved = true;
                            reject(new Error('Job polling timeout'));
                        }
                        return;
                    }

                    const result = await getJobStatus(jobId);

                    if (!result.success) {
                        throw new Error(result.error);
                    }

                    const status = result.data.data;

                    // Call update callback if provided
                    if (onUpdate) {
                        onUpdate(status);
                    }

                    // Check if job is complete
                    if (status.status === 'completed' || status.status === 'failed') {
                        if (!isResolved) {
                            isResolved = true;
                            resolve(status);
                        }
                        return;
                    }

                    // Continue polling
                    setTimeout(poll, POLL_INTERVAL);
                } catch (error) {
                    if (!isResolved) {
                        isResolved = true;
                        reject(error);
                    }
                }
            };

            poll();
        });
    }

    /**
     * Get processing results
     */
    async function getResults(jobId) {
        try {
            const response = await request(`/results/${jobId}`);
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Get analytics for a job
     */
    async function getAnalytics(jobId) {
        try {
            const response = await request(`/analytics/${jobId}`);
            return {
                success: true,
                data: response
            };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Download results as CSV
     */
    async function downloadResults(jobId, format = 'csv') {
        try {
            const url = `${API_BASE_URL}/results/${jobId}/download?format=${encodeURIComponent(format)}`;
            const response = await fetch(url, {
                method: 'GET'
            });

            if (!response.ok) {
                let errorMessage = `Download failed: HTTP ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorData.message || errorMessage;
                } catch (_) {
                    // Keep default message when body is not JSON.
                }
                throw new Error(errorMessage);
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `results_${jobId}.${format}`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Download dashboard as PDF
     */
    async function downloadDashboardPDF(jobId) {
        try {
            const url = `${API_BASE_URL}/results/${jobId}/dashboard-pdf`;
            const response = await fetch(url, {
                method: 'GET'
            });

            if (!response.ok) {
                let errorMessage = `PDF download failed: HTTP ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorData.message || errorMessage;
                } catch (_) {
                    // Keep default message when body is not JSON.
                }
                throw new Error(errorMessage);
            }

            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = `dashboard_${jobId}.pdf`;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.URL.revokeObjectURL(downloadUrl);
            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Validate file format
     */
    function isValidFileType(file) {
        const validTypes = ['text/csv', 'application/json', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        const validExtensions = ['.csv', '.json', '.xlsx', '.xls'];

        const hasValidType = validTypes.some(type => file.type === type);
        const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

        return hasValidType || hasValidExtension;
    }

    /**
     * Format file size for display
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }

    /**
     * Public API
     */
    return {
        checkHealth,
        getInfo,
        uploadFile,
        validateData,
        processData,
        getJobStatus,
        getAsyncStats,
        getQueueStatus,
        getStorageStats,
        pollJobStatus,
        getResults,
        getAnalytics,
        downloadResults,
        downloadDashboardPDF,
        isValidFileType,
        formatFileSize
    };
})();
