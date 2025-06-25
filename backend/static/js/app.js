// Translation Evaluation Tool - Frontend JavaScript

class TranslationApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.updateCharCount();
    }

    initializeElements() {
        // Language selectors
        this.sourceLangSelect = document.getElementById('source-lang');
        this.targetLangSelect = document.getElementById('target-lang');
        this.swapButton = document.getElementById('swap-languages');

        // Text areas
        this.sourceText = document.getElementById('source-text');
        this.translationText = document.getElementById('translation-text');
        this.charCount = document.getElementById('char-count');

        // Buttons
        this.translateBtn = document.getElementById('translate-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.evaluateBtn = document.getElementById('evaluate-btn');

        // Evaluation elements
        this.evaluationSection = document.getElementById('evaluation-section');
        this.evaluationResult = document.getElementById('evaluation-result');
        this.noTranslationMsg = document.getElementById('no-translation-msg');
        this.scoreValue = document.getElementById('score-value');
        this.scoreBar = document.getElementById('score-bar');
        this.justificationText = document.getElementById('justification-text');

        // Loading overlay
        this.loadingOverlay = document.getElementById('loading-overlay');

        // Example buttons
        this.exampleButtons = document.querySelectorAll('.example-btn');
    }

    bindEvents() {
        // Language swap
        this.swapButton.addEventListener('click', () => this.swapLanguages());

        // Text input
        this.sourceText.addEventListener('input', () => {
            this.updateCharCount();
            this.resetEvaluation();
        });

        // Translation
        this.translateBtn.addEventListener('click', () => this.translateText());
        
        // Clear
        this.clearBtn.addEventListener('click', () => this.clearAll());

        // Evaluation
        this.evaluateBtn.addEventListener('click', () => this.evaluateTranslation());

        // Example buttons
        this.exampleButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const exampleText = btn.getAttribute('data-text');
                this.sourceText.value = exampleText;
                this.updateCharCount();
                this.resetEvaluation();
            });
        });

        // Language change handlers
        this.sourceLangSelect.addEventListener('change', () => this.resetEvaluation());
        this.targetLangSelect.addEventListener('change', () => this.resetEvaluation());

        // Enter key for translation
        this.sourceText.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.translateText();
            }
        });
    }

    swapLanguages() {
        const sourceLang = this.sourceLangSelect.value;
        const targetLang = this.targetLangSelect.value;
        
        this.sourceLangSelect.value = targetLang;
        this.targetLangSelect.value = sourceLang;
        
        // Swap text content if both exist
        if (this.sourceText.value && this.translationText.value) {
            const sourceText = this.sourceText.value;
            this.sourceText.value = this.translationText.value;
            this.translationText.value = sourceText;
            this.updateCharCount();
        }
        
        this.resetEvaluation();
    }

    updateCharCount() {
        const count = this.sourceText.value.length;
        this.charCount.textContent = count;
        
        // Color coding for character count
        if (count > 1000) {
            this.charCount.style.color = '#dc3545';
        } else if (count > 500) {
            this.charCount.style.color = '#ffc107';
        } else {
            this.charCount.style.color = '#6c757d';
        }
    }

    async translateText() {
        const sourceLang = this.sourceLangSelect.value;
        const targetLang = this.targetLangSelect.value;
        const text = this.sourceText.value.trim();

        // Validation
        if (!text) {
            this.showAlert('Please enter some text to translate', 'warning');
            return;
        }

        if (sourceLang === targetLang) {
            this.showAlert('Please select different source and target languages', 'warning');
            return;
        }

        this.showLoading();
        this.translateBtn.disabled = true;

        try {
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source_lang: sourceLang,
                    target_lang: targetLang,
                    text: text
                })
            });

            const result = await response.json();

            if (result.success) {
                this.translationText.value = result.translation;
                this.showEvaluationSection();
                this.showAlert('Translation completed successfully!', 'success');
            } else {
                this.showAlert(`Translation failed: ${result.error}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Network error: ${error.message}`, 'danger');
        } finally {
            this.hideLoading();
            this.translateBtn.disabled = false;
        }
    }

    async evaluateTranslation() {
        const sourceLang = this.sourceLangSelect.value;
        const targetLang = this.targetLangSelect.value;
        const sourceText = this.sourceText.value.trim();
        const translation = this.translationText.value.trim();

        if (!sourceText || !translation) {
            this.showAlert('Both source text and translation are required for evaluation', 'warning');
            return;
        }

        this.showLoading();
        this.evaluateBtn.disabled = true;

        try {
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source_lang: sourceLang,
                    target_lang: targetLang,
                    source_text: sourceText,
                    translation: translation
                })
            });

            const result = await response.json();

            if (result.success) {
                this.displayEvaluationResult(result.score, result.justification);
                this.showAlert('Evaluation completed!', 'success');
            } else {
                this.showAlert(`Evaluation failed: ${result.error}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Network error: ${error.message}`, 'danger');
        } finally {
            this.hideLoading();
            this.evaluateBtn.disabled = false;
        }
    }

    displayEvaluationResult(score, justification) {
        this.scoreValue.textContent = score;
        this.justificationText.textContent = justification;

        // Update progress bar
        const percentage = (score / 10) * 100;
        this.scoreBar.style.width = `${percentage}%`;
        this.scoreBar.setAttribute('aria-valuenow', score);

        // Color coding based on score
        const scoreDisplay = document.querySelector('.score-display');
        const progressBar = this.scoreBar;
        
        // Remove existing classes
        scoreDisplay.className = 'score-display score-animate';
        progressBar.className = 'progress-bar';

        if (score >= 9) {
            scoreDisplay.classList.add('score-excellent');
            progressBar.classList.add('progress-bar-excellent');
        } else if (score >= 7) {
            scoreDisplay.classList.add('score-good');
            progressBar.classList.add('progress-bar-good');
        } else if (score >= 5) {
            scoreDisplay.classList.add('score-fair');
            progressBar.classList.add('progress-bar-fair');
        } else {
            scoreDisplay.classList.add('score-poor');
            progressBar.classList.add('progress-bar-poor');
        }

        this.evaluationResult.style.display = 'block';
    }

    showEvaluationSection() {
        this.evaluationSection.style.display = 'block';
        this.noTranslationMsg.style.display = 'none';
        this.evaluationResult.style.display = 'none';
    }

    resetEvaluation() {
        this.evaluationSection.style.display = 'none';
        this.noTranslationMsg.style.display = 'block';
        this.evaluationResult.style.display = 'none';
        this.translationText.value = '';
    }

    clearAll() {
        this.sourceText.value = '';
        this.translationText.value = '';
        this.updateCharCount();
        this.resetEvaluation();
    }

    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }

    showAlert(message, type) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert-dismissible');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TranslationApp();
});

// Add some keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl+T for translate
    if (e.ctrlKey && e.key === 't') {
        e.preventDefault();
        document.getElementById('translate-btn').click();
    }
    
    // Ctrl+E for evaluate
    if (e.ctrlKey && e.key === 'e') {
        e.preventDefault();
        const evaluateBtn = document.getElementById('evaluate-btn');
        if (!evaluateBtn.disabled && evaluateBtn.style.display !== 'none') {
            evaluateBtn.click();
        }
    }
    
    // Ctrl+L for clear
    if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        document.getElementById('clear-btn').click();
    }
}); 