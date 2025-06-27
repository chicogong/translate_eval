class PlaygroundDashboard {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.loadAndPopulateExamples();
    }

    initializeElements() {
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
        this.fluencyRateSpan = document.getElementById('fluency-rate');
        this.totalItemsSpan = document.getElementById('total-items');
        this.resultsTableBody = document.querySelector('#results-table tbody');
        this.chartCanvas = document.getElementById('score-chart');
        this.scoreChart = null;
        
        // Play All Buttons
        this.playAllContainer = document.getElementById('play-all-container');
        this.playAllDropdownBtn = document.getElementById('play-all-dropdown-btn');
        this.playAllSourcesBtn = document.getElementById('play-all-sources-btn');
        this.playAllTranslationsBtn = document.getElementById('play-all-translations-btn');

        // Data
        this.examples = {}; // Will be fetched from backend
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
        
        // File upload, history, and audio playback functionality
        this.setupFileUpload();
        this.setupHistory();
        this.bindAudioEvents();
    }

    bindAudioEvents() {
        // Use event delegation for individual play buttons in the results table
        this.resultsTableBody.addEventListener('click', (e) => {
            const target = e.target.closest('.play-btn');
            if (target) {
                const text = target.dataset.text;
                const lang = target.dataset.lang;
                if (text && lang) {
                    this.playAudio(text, lang, target);
                }
            }
        });

        // "Play All" button events
        this.playAllSourcesBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.playAllVisible('source');
        });
        this.playAllTranslationsBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.playAllVisible('translation');
        });
    }
    
    setupFileUpload() {
        const fileUploadArea = document.getElementById('file-upload-area');
        const fileInput = document.getElementById('file-input');
        const selectFileBtn = document.getElementById('select-file-btn');
        
        // Click to select file
        selectFileBtn.addEventListener('click', () => fileInput.click());
        fileUploadArea.addEventListener('click', () => fileInput.click());
        
        // File input change
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));
        
        // Drag and drop
        fileUploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUploadArea.classList.add('dragover');
        });
        
        fileUploadArea.addEventListener('dragleave', () => {
            fileUploadArea.classList.remove('dragover');
        });
        
        fileUploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }
    
    handleFileSelect(file) {
        if (!file) return;
        
        if (!file.name.endsWith('.txt')) {
            alert('Please select a .txt file');
            return;
        }
        
        if (file.size > 1024 * 1024) { // 1MB limit
            alert('File size must be less than 1MB');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target.result;
            this.textArea.value = content;
            
            // Show success message
            const uploadArea = document.getElementById('file-upload-area');
            const originalHTML = uploadArea.innerHTML;
            uploadArea.innerHTML = `
                <div class="upload-placeholder">
                    <i class="fas fa-check-circle fa-2x mb-2 text-success"></i>
                    <p class="mb-2 text-success">File "${file.name}" loaded successfully!</p>
                    <small class="text-muted">${content.split('\n').filter(line => line.trim()).length} lines loaded</small>
                </div>
            `;
            
            // Reset after 3 seconds
            setTimeout(() => {
                uploadArea.innerHTML = originalHTML;
                this.setupFileUpload(); // Re-bind events
            }, 3000);
        };
        
        reader.onerror = () => {
            alert('Error reading file');
        };
        
        reader.readAsText(file);
    }
    
    setupHistory() {
        const historyBtn = document.getElementById('history-btn');
        historyBtn.addEventListener('click', () => this.showHistory());
    }
    
    async showHistory() {
        const modal = new bootstrap.Modal(document.getElementById('historyModal'));
        modal.show();
        
        const loadingDiv = document.getElementById('history-loading');
        const contentDiv = document.getElementById('history-content');
        const errorDiv = document.getElementById('history-error');
        const tableBody = document.getElementById('history-table-body');
        
        // Reset states
        loadingDiv.style.display = 'block';
        contentDiv.style.display = 'none';
        errorDiv.style.display = 'none';
        
        try {
            const response = await fetch('/api/history');
            const data = await response.json();
            
            if (data.success) {
                tableBody.innerHTML = '';
                
                if (data.history.length === 0) {
                    tableBody.innerHTML = `
                        <tr>
                            <td colspan="6" class="text-center text-muted py-4">
                                <i class="fas fa-inbox fa-2x mb-2"></i><br>
                                No history found. Start by running some translations!
                            </td>
                        </tr>
                    `;
                } else {
                    data.history.forEach(item => {
                        const row = document.createElement('tr');
                        
                        // Format timestamp
                        const timestamp = this.formatTimestamp(item.timestamp);
                        
                        // Format language pairs
                        const langPairs = item.language_pairs.map(pair => {
                            const score = pair.avg_score ? ` (${pair.avg_score})` : '';
                            return `${pair.pair} (${pair.items}${score})`;
                        }).join(', ');
                        
                        // Type badge
                        const typeBadge = item.type === 'translation' 
                            ? '<span class="badge bg-primary">Translation</span>'
                            : '<span class="badge bg-success">Evaluation</span>';
                        
                        // Average score
                        const avgScore = item.avg_score ? 
                            `<span class="badge bg-info">${item.avg_score}/10</span>` : 
                            '<span class="text-muted">-</span>';
                        
                        row.innerHTML = `
                            <td><code>${item.run_id}</code></td>
                            <td>${typeBadge}</td>
                            <td><small>${langPairs}</small></td>
                            <td class="text-center">${item.total_items}</td>
                            <td class="text-center">${avgScore}</td>
                            <td><small>${timestamp}</small></td>
                        `;
                        
                        tableBody.appendChild(row);
                    });
                }
                
                loadingDiv.style.display = 'none';
                contentDiv.style.display = 'block';
            } else {
                throw new Error(data.error || 'Failed to load history');
            }
        } catch (error) {
            console.error('Error loading history:', error);
            loadingDiv.style.display = 'none';
            errorDiv.style.display = 'block';
        }
    }
    
    formatTimestamp(timestamp) {
        // Convert YYYYMMDD_HHMM to readable format
        if (timestamp.length === 13 && timestamp.includes('_')) {
            const [date, time] = timestamp.split('_');
            const year = date.substring(0, 4);
            const month = date.substring(4, 6);
            const day = date.substring(6, 8);
            const hour = time.substring(0, 2);
            const minute = time.substring(2, 4);
            
            return `${year}-${month}-${day} ${hour}:${minute}`;
        }
        return timestamp;
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
            this.playAllContainer.style.display = 'none';
            return;
        }

        this.noDataAlert.style.display = 'none';
        this.resultsSection.style.display = 'block';
        this.summarySection.style.display = 'block';
        this.playAllContainer.style.display = 'inline-flex';

        // Populate table and collect scores for the chart
        const scores = [];
        const lineLabels = [];
        const sourceLang = this.sourceSelect.value;
        const targetLang = this.targetSelect.value;

        results.forEach(res => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td class="text-center"><strong>${res.line_number}</strong></td>
                <td class="text-center"><span class="score-badge ${this.getScoreClass(res.evaluation_score)}">${res.evaluation_score}/10</span></td>
                <td class="text-center">${res.bleu_score ? res.bleu_score.toFixed(3) : '-'}</td>
                <td><div class="text-truncate" style="max-width: 250px;" title="${this.escapeHtml(res.source_text)}">${this.escapeHtml(res.source_text)}</div></td>
                <td><div class="text-truncate" style="max-width: 250px;" title="${this.escapeHtml(res.translation)}">${this.escapeHtml(res.translation)}</div></td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-secondary play-btn play-source-btn" 
                            data-text="${this.escapeHtml(res.source_text)}" 
                            data-lang="${sourceLang}" 
                            title="Play Source Text">
                        <i class="fas fa-volume-up"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-info play-btn play-translation-btn" 
                            data-text="${this.escapeHtml(res.translation)}" 
                            data-lang="${targetLang}"
                            title="Play Translation">
                        <i class="fas fa-volume-up"></i>
                    </button>
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

        // Calculate fluency rate (percentage of scores >= 7)
        const fluencyRate = scores.length > 0 ? 
            (scores.filter(score => score >= 7).length / scores.length * 100).toFixed(1) : 0;

        // Update summary elements
        this.avgScoreSpan.textContent = avgScore ? avgScore.toFixed(2) : 'N/A';
        this.avgBleuSpan.textContent = avgBleu ? avgBleu.toFixed(3) : 'N/A';
        this.fluencyRateSpan.textContent = fluencyRate + '%';
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

    async playAudio(text, lang, btnElement) {
        if (!text || !lang) return;

        const originalIcon = btnElement.innerHTML;
        btnElement.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        btnElement.disabled = true;

        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, language: lang })
            });

            const data = await response.json();

            if (data.success && data.audio_data) {
                const audioBlob = this.base64ToBlob(data.audio_data, 'audio/mp3');
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                audio.onended = () => {
                    btnElement.innerHTML = originalIcon;
                    btnElement.disabled = false;
                    URL.revokeObjectURL(audioUrl);
                };
                 audio.onerror = () => {
                    alert('Error playing audio');
                    btnElement.innerHTML = originalIcon;
                    btnElement.disabled = false;
                    URL.revokeObjectURL(audioUrl);
                };
                audio.play();

            } else {
                throw new Error(data.error || 'Failed to get audio data.');
            }
        } catch (error) {
            console.error('TTS Error:', error);
            alert(`Could not play audio: ${error.message}`);
            btnElement.innerHTML = originalIcon;
            btnElement.disabled = false;
        }
    }

    async playAllVisible(type) {
        if (!type) return;

        const rows = this.resultsTableBody.querySelectorAll('tr');
        this.playAllDropdownBtn.disabled = true;
        this.playAllDropdownBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Playing...';

        for (const row of rows) {
            const btn = row.querySelector(`.play-${type}-btn`);
            if (btn) {
                const text = btn.dataset.text;
                const lang = btn.dataset.lang;
                
                // Play audio and wait for it to finish
                await new Promise(async (resolve) => {
                    if (text && lang) {
                        const originalIcon = btn.innerHTML;
                        btn.innerHTML = '<i class="fas fa-pause"></i>';
                        
                        const response = await fetch('/api/tts', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: text, language: lang })
                        });
                        const data = await response.json();
                        
                        if(data.success) {
                            const audioBlob = this.base64ToBlob(data.audio_data, 'audio/mp3');
                            const audioUrl = URL.createObjectURL(audioBlob);
                            const audio = new Audio(audioUrl);
                            audio.onended = () => {
                                btn.innerHTML = originalIcon;
                                URL.revokeObjectURL(audioUrl);
                                // Wait 1 second before playing the next
                                setTimeout(resolve, 1000); 
                            };
                            audio.onerror = () => {
                                btn.innerHTML = originalIcon;
                                URL.revokeObjectURL(audioUrl);
                                setTimeout(resolve, 1000);
                            }
                            audio.play();
                        } else {
                            // If TTS fails for one, just move on
                           setTimeout(resolve, 100); 
                        }
                    } else {
                        resolve();
                    }
                });
            }
        }
        
        this.playAllDropdownBtn.disabled = false;
        this.playAllDropdownBtn.innerHTML = '<i class="fas fa-play-circle me-1"></i> Play All';
    }
    
    base64ToBlob(audioData, mimeType) {
        try {
            // Check if the data is hex string (from MiniMax API)
            if (audioData.match(/^[0-9a-fA-F]+$/)) {
                // Convert hex string to byte array
                const byteNumbers = new Array(audioData.length / 2);
                for (let i = 0; i < audioData.length; i += 2) {
                    byteNumbers[i / 2] = parseInt(audioData.substr(i, 2), 16);
                }
                const byteArray = new Uint8Array(byteNumbers);
                return new Blob([byteArray], { type: mimeType });
            } else {
                // Handle base64 string
                // Remove data URL prefix if present
                const base64 = audioData.replace(/^data:audio\/[^;]+;base64,/, '');
                const byteCharacters = atob(base64);
                const byteNumbers = new Array(byteCharacters.length);
                
                for (let i = 0; i < byteCharacters.length; i++) {
                    byteNumbers[i] = byteCharacters.charCodeAt(i);
                }
                
                const byteArray = new Uint8Array(byteNumbers);
                return new Blob([byteArray], { type: mimeType });
            }
        } catch (error) {
            console.error('Error converting audio data:', error);
            throw new Error('Failed to convert audio data');
        }
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