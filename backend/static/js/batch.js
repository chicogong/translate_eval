class BatchDashboard {
    constructor() {
        this.sourceSelect = document.getElementById('source-lang');
        this.targetSelect = document.getElementById('target-lang');
        this.runSelect = document.getElementById('run-select');
        this.loadBtn = document.getElementById('load-results');
        this.resultsSection = document.getElementById('results-section');
        this.noDataAlert = document.getElementById('no-data');
        this.resultCountBadge = document.getElementById('result-count');
        this.resultsTableBody = document.querySelector('#results-table tbody');
        this.chartCanvas = document.getElementById('score-chart');
        this.scoreChart = null;

        // summary elements
        this.summarySection = document.getElementById('summary-section');
        this.avgScoreSpan = document.getElementById('avg-score');
        this.avgBleuSpan = document.getElementById('avg-bleu');

        this.availableRuns = {
            translation_runs: [],
            evaluation_runs: []
        };

        this.bindEvents();
        this.loadAvailableRuns();
    }

    bindEvents() {
        this.loadBtn.addEventListener('click', () => this.loadResults());

        // When source language changes, auto-set target to first different language
        this.sourceSelect.addEventListener('change', () => {
            if (this.sourceSelect.value === this.targetSelect.value) {
                const options = Array.from(this.targetSelect.options);
                const newOpt = options.find(opt => opt.value !== this.sourceSelect.value);
                if (newOpt) this.targetSelect.value = newOpt.value;
            }
        });

        // When target language changes, auto-set source to first different language
        this.targetSelect.addEventListener('change', () => {
            if (this.sourceSelect.value === this.targetSelect.value) {
                const options = Array.from(this.sourceSelect.options);
                const newOpt = options.find(opt => opt.value !== this.targetSelect.value);
                if (newOpt) this.sourceSelect.value = newOpt.value;
            }
        });
    }

    async loadAvailableRuns() {
        try {
            const resp = await fetch('/api/available-runs');
            const data = await resp.json();
            
            if (data.success) {
                this.availableRuns = data;
                this.updateRunSelect();
            } else {
                console.error('Failed to load available runs:', data.error);
                this.showSampleRunsInSelect();
            }
        } catch (error) {
            console.error('Error loading available runs:', error);
            this.showSampleRunsInSelect();
        }
    }

    updateRunSelect() {
        this.runSelect.innerHTML = '';
        
        if (this.availableRuns.evaluation_runs.length === 0) {
            this.runSelect.innerHTML = '<option value="">No evaluation runs found</option>';
            return;
        }

        // Add evaluation runs
        this.availableRuns.evaluation_runs.forEach(runId => {
            const option = document.createElement('option');
            option.value = runId;
            option.textContent = this.formatRunId(runId);
            this.runSelect.appendChild(option);
        });

        // Select the latest run by default
        if (this.availableRuns.evaluation_runs.length > 0) {
            this.runSelect.value = this.availableRuns.evaluation_runs[0];
        }
    }

    showSampleRunsInSelect() {
        // Show sample runs for demo purposes
        this.runSelect.innerHTML = `
            <option value="sample_20241226_1400">Sample Run - Dec 26, 14:00</option>
            <option value="sample_20241225_1030">Sample Run - Dec 25, 10:30</option>
            <option value="">No real runs available</option>
        `;
    }

    formatRunId(runId) {
        // Convert YYYYMMDD_HHMM to readable format
        if (runId.match(/^\d{8}_\d{4}$/)) {
            const date = runId.substring(0, 8);
            const time = runId.substring(9);
            const year = date.substring(0, 4);
            const month = date.substring(4, 6);
            const day = date.substring(6, 8);
            const hour = time.substring(0, 2);
            const minute = time.substring(2, 4);
            
            return `${year}-${month}-${day} ${hour}:${minute}`;
        }
        return runId;
    }

    async loadResults() {
        const sourceLang = this.sourceSelect.value;
        const targetLang = this.targetSelect.value;
        const runId = this.runSelect.value;

        if (sourceLang === targetLang) {
            alert('Please select two different languages.');
            return;
        }

        if (!runId) {
            alert('Please select an evaluation run.');
            return;
        }

        this.setLoading(true);

        try {
            // Handle sample data
            if (runId.startsWith('sample_')) {
                this.displaySampleResults();
                return;
            }

            const resp = await fetch(`/api/evaluation-results?eval_run_id=${runId}&source_lang=${sourceLang}&target_lang=${targetLang}`);
            const data = await resp.json();
            
            if (data.success) {
                this.displayResults(data.results, data.avg_score, data.avg_bleu);
            } else {
                alert(data.error || 'Failed to load results');
                this.displayResults([], null, null);
            }
        } catch (err) {
            console.error(err);
            alert('Network error while loading results.');
            this.displayResults([], null, null);
        } finally {
            this.setLoading(false);
        }
    }

    displaySampleResults() {
        // Create sample evaluation data
        const sampleResults = [
            {
                line_number: 1,
                evaluation_score: 8,
                bleu_score: 0.75,
                source_text: "The novel algorithm leverages a multi-head attention mechanism to process long-range dependencies in sequential data.",
                translation: "这种新颖的算法利用多头注意力机制来处理序列数据中的长距离依赖关系。",
                justification: "Translation accurately conveys the technical concepts with appropriate terminology."
            },
            {
                line_number: 2,
                evaluation_score: 9,
                bleu_score: 0.82,
                source_text: "Blockchain technology provides a decentralized and immutable ledger system.",
                translation: "区块链技术提供了一个去中心化且不可篡改的账本系统。",
                justification: "Excellent translation with precise technical terms and natural flow."
            },
            {
                line_number: 3,
                evaluation_score: 7,
                bleu_score: 0.68,
                source_text: "Quantum computing promises exponential speedup for certain computational problems.",
                translation: "量子计算承诺为某些计算问题提供指数级加速。",
                justification: "Good translation but could be more natural in target language."
            },
            {
                line_number: 4,
                evaluation_score: 8,
                bleu_score: 0.79,
                source_text: "Machine learning models require large datasets for effective training.",
                translation: "机器学习模型需要大量数据集进行有效训练。",
                justification: "Clear and accurate translation with good terminology choice."
            },
            {
                line_number: 5,
                evaluation_score: 9,
                bleu_score: 0.85,
                source_text: "Cybersecurity threats continue to evolve with advancing technology.",
                translation: "网络安全威胁随着技术进步而不断演变。",
                justification: "Excellent translation capturing both meaning and tone."
            }
        ];

        this.displayResults(sampleResults, 8.2, 0.78);
    }

    displayResults(results, avgScore, avgBleu) {
        // clear
        this.resultsTableBody.innerHTML = '';

        if (!results || results.length === 0) {
            this.resultsSection.style.display = 'none';
            this.noDataAlert.style.display = 'block';
            this.summarySection.style.display = 'none';
            return;
        }

        this.noDataAlert.style.display = 'none';
        this.resultsSection.style.display = 'block';
        this.summarySection.style.display = 'block';
        this.resultCountBadge.textContent = results.length;

        // Populate table and collect scores
        const scores = [];
        const lineLabels = [];

        results.forEach(res => {
            const row = document.createElement('tr');
            
            // Add color coding for scores
            let scoreClass = '';
            if (res.evaluation_score >= 8) scoreClass = 'text-success';
            else if (res.evaluation_score >= 6) scoreClass = 'text-warning';
            else if (res.evaluation_score < 6) scoreClass = 'text-danger';
            
            row.innerHTML = `
                <td><strong>${res.line_number}</strong></td>
                <td><span class="badge bg-primary ${scoreClass}">${res.evaluation_score}/10</span></td>
                <td>${res.bleu_score ? res.bleu_score.toFixed(3) : '-'}</td>
                <td class="text-truncate" style="max-width: 200px;" title="${this.escapeHtml(res.source_text)}">${this.escapeHtml(res.source_text).slice(0, 80)}...</td>
                <td class="text-truncate" style="max-width: 200px;" title="${this.escapeHtml(res.translation)}">${this.escapeHtml(res.translation).slice(0, 80)}...</td>
                <td class="text-truncate" style="max-width: 250px;" title="${this.escapeHtml(res.justification || '')}">${this.escapeHtml(res.justification || '').slice(0,80)}...</td>
            `;
            this.resultsTableBody.appendChild(row);

            if (!isNaN(res.evaluation_score)) {
                scores.push(res.evaluation_score);
                lineLabels.push(res.line_number);
            }
        });

        this.renderChart(lineLabels, scores);

        // Update summary elements
        this.avgScoreSpan.textContent = avgScore ? avgScore.toFixed(2) : '-';
        this.avgBleuSpan.textContent = avgBleu ? avgBleu.toFixed(3) : '-';
        document.getElementById('total-items').textContent = results.length;
    }

    renderChart(labels, data) {
        if (this.scoreChart) {
            this.scoreChart.destroy();
        }
        
        // Create color array based on scores
        const colors = data.map(score => {
            if (score >= 8) return '#28a745'; // green
            if (score >= 6) return '#ffc107'; // yellow
            return '#dc3545'; // red
        });

        this.scoreChart = new Chart(this.chartCanvas, {
            type: 'bar',
            data: {
                labels: labels.map(l => `Line ${l}`),
                datasets: [{
                    label: 'Evaluation Score',
                    data: data,
                    backgroundColor: colors,
                    borderColor: colors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        title: {
                            display: true,
                            text: 'Score (1-10)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Test Cases'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Translation Quality Scores'
                    }
                }
            }
        });
    }

    setLoading(isLoading) {
        this.loadBtn.disabled = isLoading;
        this.loadBtn.innerHTML = isLoading ? 
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...' : 
            '<i class="fas fa-database me-1"></i>Load Results';
    }

    escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

// Global functions for buttons
function loadSampleData() {
    const dashboard = window.batchDashboard;
    dashboard.runSelect.value = 'sample_20241226_1400';
    dashboard.loadResults();
}

function loadLatestRun() {
    const dashboard = window.batchDashboard;
    if (dashboard.availableRuns.evaluation_runs.length > 0) {
        dashboard.runSelect.value = dashboard.availableRuns.evaluation_runs[0];
        dashboard.loadResults();
    } else {
        alert('No evaluation runs available. Try the sample data instead.');
    }
}

function refreshRuns() {
    const dashboard = window.batchDashboard;
    dashboard.loadAvailableRuns();
}

async function startBatchTranslation() {
    const dashboard = window.batchDashboard;
    const sourceLang = dashboard.sourceSelect.value;
    const targetLang = dashboard.targetSelect.value;
    
    if (sourceLang === targetLang) {
        alert('Please select two different languages for translation.');
        return;
    }
    
    const confirmed = confirm(`Start batch translation from ${sourceLang.toUpperCase()} to ${targetLang.toUpperCase()}?\n\nThis will process all test cases and may take several minutes.`);
    if (!confirmed) return;
    
    try {
        // Show progress modal
        showProgressModal('Translation', 'Starting batch translation...');
        
        // Start batch translation via API
        const response = await fetch('/api/batch-translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                source_lang: sourceLang,
                target_lang: targetLang,
                lines: 15  // Process all test cases
            })
        });
        
        const result = await response.json();
        hideProgressModal();
        
        if (result.success) {
            alert(`Translation completed successfully!\nRun ID: ${result.run_id}\nProcessed: ${result.processed} items`);
            dashboard.loadAvailableRuns(); // Refresh available runs
        } else {
            alert(`Translation failed: ${result.error}`);
        }
    } catch (error) {
        hideProgressModal();
        alert(`Error starting translation: ${error.message}`);
    }
}

async function startBatchEvaluation() {
    const dashboard = window.batchDashboard;
    const sourceLang = dashboard.sourceSelect.value;
    const targetLang = dashboard.targetSelect.value;
    
    if (sourceLang === targetLang) {
        alert('Please select two different languages for evaluation.');
        return;
    }
    
    // Check if there are translation runs available
    if (!dashboard.availableRuns.translation_runs.length) {
        alert('No translation runs found. Please run batch translation first.');
        return;
    }
    
    const latestTranslationRun = dashboard.availableRuns.translation_runs[0];
    const confirmed = confirm(`Start batch evaluation for ${sourceLang.toUpperCase()} to ${targetLang.toUpperCase()}?\n\nThis will evaluate translations from run: ${latestTranslationRun}`);
    if (!confirmed) return;
    
    try {
        // Show progress modal
        showProgressModal('Evaluation', 'Starting batch evaluation...');
        
        // Start batch evaluation via API
        const response = await fetch('/api/batch-evaluate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                source_lang: sourceLang,
                target_lang: targetLang,
                translation_run_id: latestTranslationRun
            })
        });
        
        const result = await response.json();
        hideProgressModal();
        
        if (result.success) {
            alert(`Evaluation completed successfully!\nRun ID: ${result.eval_run_id}\nProcessed: ${result.processed} items`);
            dashboard.loadAvailableRuns(); // Refresh available runs
            // Auto-load the new evaluation results
            dashboard.runSelect.value = result.eval_run_id;
            dashboard.loadResults();
        } else {
            alert(`Evaluation failed: ${result.error}`);
        }
    } catch (error) {
        hideProgressModal();
        alert(`Error starting evaluation: ${error.message}`);
    }
}

function showProgressModal(operation, message) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('progressModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'progressModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-cog fa-spin me-2"></i>Batch ${operation}
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <div class="spinner-border text-primary mb-3" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <p id="progressMessage">${message}</p>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    document.getElementById('progressMessage').textContent = message;
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

function hideProgressModal() {
    const modal = document.getElementById('progressModal');
    if (modal) {
        const bootstrapModal = bootstrap.Modal.getInstance(modal);
        if (bootstrapModal) {
            bootstrapModal.hide();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.batchDashboard = new BatchDashboard();
}); 