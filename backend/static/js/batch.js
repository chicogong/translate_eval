class BatchDashboard {
    constructor() {
        this.sourceSelect = document.getElementById('source-lang');
        this.targetSelect = document.getElementById('target-lang');
        this.loadBtn = document.getElementById('load-results');
        this.versionSelect = document.getElementById('version-select');
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

        this.bindEvents();
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
    }

    async loadResults() {
        const sourceLang = this.sourceSelect.value;
        const targetLang = this.targetSelect.value;

        if (sourceLang === targetLang) {
            alert('Please select two different languages.');
            return;
        }

        this.setLoading(true);

        try {
            const version = this.versionSelect ? this.versionSelect.value : 'v1';
            const resp = await fetch(`/api/results?source_lang=${sourceLang}&target_lang=${targetLang}&version=${version}`);
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
        this.resultCountBadge.textContent = results.length;

        // Populate table and collect scores
        const scores = [];
        const lineLabels = [];

        results.forEach(res => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${res.line_number}</td>
                <td>${res.evaluation_score}</td>
                <td>${res.bleu_score ?? '-'}</td>
                <td>${this.escapeHtml(res.source_text).slice(0, 80)}...</td>
                <td>${this.escapeHtml(res.translation).slice(0, 80)}...</td>
                <td><span title="${this.escapeHtml(res.justification || '')}">${this.escapeHtml(res.justification || '').slice(0,60)}...</span></td>
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
        this.avgBleuSpan.textContent = avgBleu ? avgBleu.toFixed(2) : '-';
    }

    renderChart(labels, data) {
        if (this.scoreChart) {
            this.scoreChart.destroy();
        }
        this.scoreChart = new Chart(this.chartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Evaluation Score',
                    data: data,
                    backgroundColor: '#0d6efd'
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10
                    }
                }
            }
        });
    }

    setLoading(isLoading) {
        this.loadBtn.disabled = isLoading;
        this.loadBtn.innerHTML = isLoading ? '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...' : '<i class="fas fa-database me-1"></i>Load Results';
    }

    escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new BatchDashboard();
}); 