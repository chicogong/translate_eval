class PlaygroundDashboard {
    constructor() {
        // UI Elements
        this.sourceSelect = document.getElementById('source-lang');
        this.targetSelect = document.getElementById('target-lang');
        this.runBtn = document.getElementById('run-playground');
        this.textArea = document.getElementById('source-text-area');
        this.exampleBtnsContainer = document.getElementById('example-buttons');
        
        // Results Display
        this.resultsSection = document.getElementById('results-section');
        this.noDataAlert = document.getElementById('no-data');
        this.summarySection = document.getElementById('summary-section');
        this.avgScoreSpan = document.getElementById('avg-score');
        this.avgBleuSpan = document.getElementById('avg-bleu');
        this.totalItemsSpan = document.getElementById('total-items');
        this.resultsTableBody = document.querySelector('#results-table tbody');
        this.chartCanvas = document.getElementById('score-chart');
        this.scoreChart = null;

        // Data
        this.examples = {}; // Will be fetched from backend

        this.bindEvents();
        this.loadAndPopulateExamples();
    }

    bindEvents() {
        this.runBtn.addEventListener('click', () => this.runPlayground());
        this.sourceSelect.addEventListener('change', () => this.populateExamples());

        // Auto-swap languages if they are the same
        this.targetSelect.addEventListener('change', () => {
            if (this.sourceSelect.value === this.targetSelect.value) {
                const options = Array.from(this.sourceSelect.options);
                const currentSource = this.sourceSelect.value;
                const newOpt = options.find(opt => opt.value !== currentSource && opt.value !== 'auto');
                if (newOpt) this.sourceSelect.value = newOpt.value;
                this.populateExamples();
            }
        });
    }

    async loadAndPopulateExamples() {
        try {
            const response = await fetch('/api/examples');
            if (!response.ok) throw new Error('Failed to fetch examples.');
            this.examples = await response.json();
            this.populateExamples();
        } catch (error) {
            console.error("Could not load examples:", error);
            this.exampleBtnsContainer.innerHTML = `<span class="text-danger small">Error loading examples from server.</span>`;
        }
    }

    populateExamples() {
        this.exampleBtnsContainer.innerHTML = '';
        const lang = this.sourceSelect.value;
        const langExampleCategories = this.examples[lang];

        if (langExampleCategories) {
            langExampleCategories.forEach(category => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'btn btn-sm btn-outline-secondary me-1 mb-1';
                btn.textContent = category.label;
                btn.onclick = () => {
                    this.textArea.value = category.texts.join('\n');
                };
                this.exampleBtnsContainer.appendChild(btn);
            });
        } else {
            this.exampleBtnsContainer.innerHTML = `<span class="text-muted small">No examples available for this language.</span>`;
        }
    }

    async runPlayground() {
        const sourceLang = this.sourceSelect.value;
        const targetLang = this.targetSelect.value;
        const texts = this.textArea.value.split('\n').filter(line => line.trim() !== '');

        if (sourceLang === targetLang) {
            alert('Please select two different languages.');
            return;
        }

        if (texts.length === 0) {
            alert('Please enter some text to translate.');
            return;
        }

        this.setLoading(true);

        try {
            const resp = await fetch('/api/playground-run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ source_lang: sourceLang, target_lang: targetLang, texts: texts })
            });
            const data = await resp.json();
            
            if (data.success) {
                this.displayResults(data.results, data.avg_score, data.avg_bleu);
            } else {
                alert(`Error: ${data.error}` || 'An unknown error occurred.');
                this.displayResults([], null, null);
            }
        } catch (err) {
            console.error(err);
            alert('A network error occurred. Please check the console for details.');
            this.displayResults([], null, null);
        } finally {
            this.setLoading(false);
        }
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

        // Populate table and collect scores for the chart
        const scores = [];
        const lineLabels = [];

        results.forEach(res => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td class="text-center"><strong>${res.line_number}</strong></td>
                <td class="text-center"><span class="score-badge ${this.getScoreClass(res.evaluation_score)}">${res.evaluation_score}/10</span></td>
                <td class="text-center">${res.bleu_score ? res.bleu_score.toFixed(3) : '-'}</td>
                <td><div class="text-truncate" style="max-width: 250px;" title="${this.escapeHtml(res.source_text)}">${this.escapeHtml(res.source_text)}</div></td>
                <td><div class="text-truncate" style="max-width: 250px;" title="${this.escapeHtml(res.translation)}">${this.escapeHtml(res.translation)}</div></td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary" onclick="showDetailsModal('${res.line_number}', '${this.escapeHtml(res.justification || 'No details available')}')" title="View Details">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            `;
            this.resultsTableBody.appendChild(row);

            if (typeof res.evaluation_score === 'number') {
                scores.push(res.evaluation_score);
                lineLabels.push(res.line_number);
            }
        });

        this.renderChart(lineLabels, scores);

        // Update summary elements
        this.avgScoreSpan.textContent = avgScore ? avgScore.toFixed(2) : 'N/A';
        this.avgBleuSpan.textContent = avgBleu ? avgBleu.toFixed(3) : 'N/A';
        this.totalItemsSpan.textContent = results.length;
    }

    renderChart(labels, data) {
        if (this.scoreChart) {
            this.scoreChart.destroy();
        }
        
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js not available, skipping chart rendering');
            return;
        }
        
        const colors = data.map(score => {
            if (score >= 8) return '#28a745';
            if (score >= 6) return '#ffc107';
            return '#dc3545';
        });

        try {
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
                    scales: { y: { beginAtZero: true, max: 10, title: { display: true, text: 'Score (1-10)' } },
                              x: { title: { display: true, text: 'Text Line Number' } } },
                    plugins: { legend: { display: false }, title: { display: true, text: 'Translation Quality Scores' } }
                }
            });
        } catch (error) {
            console.error('Error creating chart:', error);
            // Show a simple text representation instead
            const chartContainer = this.chartCanvas.parentElement;
            chartContainer.innerHTML = `
                <div class="alert alert-info">
                    <h6>Score Summary:</h6>
                    <p>Average Score: ${(data.reduce((a, b) => a + b, 0) / data.length).toFixed(2)}/10</p>
                    <p>Highest Score: ${Math.max(...data)}/10</p>
                    <p>Lowest Score: ${Math.min(...data)}/10</p>
                </div>
            `;
        }
    }

    setLoading(isLoading) {
        this.runBtn.disabled = isLoading;
        this.runBtn.innerHTML = isLoading 
            ? '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...' 
            : '<i class="fas fa-play me-1"></i>Translate & Evaluate';
    }

    getScoreClass(score) {
        if (score >= 8) return 'score-excellent';
        if (score >= 6) return 'score-good';
        return 'score-poor';
    }

    escapeHtml(text) {
        if (!text) return '';
        return text.toString()
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

// Global function for details modal
function showDetailsModal(lineNumber, justification) {
    let modal = document.getElementById('detailsModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'detailsModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"><i class="fas fa-info-circle me-2"></i>Evaluation Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <h6>Line <span id="detailLineNumber"></span> - Justification:</h6>
                        <div class="alert alert-info">
                            <p id="detailJustification" class="mb-0"></p>
                        </div>
                    </div>
                </div>
            </div>`;
        document.body.appendChild(modal);
    }
    
    document.getElementById('detailLineNumber').textContent = lineNumber;
    document.getElementById('detailJustification').textContent = justification;
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new PlaygroundDashboard();
}); 