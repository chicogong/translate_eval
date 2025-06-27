// Translation Evaluation Tool - Frontend JavaScript

class TranslationApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.updateCharCount();
    }

    // --- 1. SETUP METHODS ---
    initializeElements() {
        // Language selectors
        this.sourceLangSelect = document.getElementById('source-lang');
        this.targetLangSelect = document.getElementById('target-lang');
        this.swapButton = document.getElementById('swap-languages');

        // Text areas
        this.sourceText = document.getElementById('source-text');
        this.translationText = document.getElementById('translation-text');
        this.charCount = document.getElementById('char-count');

        // Translation settings
        this.streamModeSelect = document.getElementById('stream-mode');
        this.temperatureInput = document.getElementById('temperature');
        this.topPInput = document.getElementById('top-p');

        // Buttons
        this.translateBtn = document.getElementById('translate-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.evaluateBtn = document.getElementById('evaluate-btn');
        this.playSourceBtn = document.getElementById('play-source-btn');
        this.playTranslationBtn = document.getElementById('play-translation-btn');

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
        
        // Audio element for playback
        this.audioPlayer = new Audio();
    }

    bindEvents() {
        // Language swap
        this.swapButton.addEventListener('click', () => this.swapLanguages());

        // Text input
        this.sourceText.addEventListener('input', () => {
            this.updateCharCount();
            this.resetEvaluation();
        });

        // Buttons
        this.translateBtn.addEventListener('click', () => this.translateText());
        this.clearBtn.addEventListener('click', () => this.clearAll());
        this.evaluateBtn.addEventListener('click', () => this.evaluateTranslation());
        this.playSourceBtn.addEventListener('click', () => this.playText('source'));
        this.playTranslationBtn.addEventListener('click', () => this.playText('translation'));

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

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch (e.key) {
                    case 'Enter':
                        this.translateText();
                        break;
                    case 't':
                        e.preventDefault();
                        this.translateBtn.click();
                        break;
                    case 'e':
                        e.preventDefault();
                        if (!this.evaluateBtn.disabled && this.evaluateBtn.style.display !== 'none') {
                            this.evaluateBtn.click();
                        }
                        break;
                    case 'l':
                        e.preventDefault();
                        this.clearBtn.click();
                        break;
                }
            }
        });
    }

    // --- 2. CORE ACTION METHODS ---
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

    clearAll() {
        this.sourceText.value = '';
        this.translationText.value = '';
        this.updateCharCount();
        this.resetEvaluation();
        
        // Disable TTS buttons
        this.playSourceBtn.disabled = true;
        this.playTranslationBtn.disabled = true;
        
        // Stop any playing audio
        this.audioPlayer.pause();
        this.audioPlayer.currentTime = 0;
    }

    async translateText() {
        const sourceLang = this.sourceLangSelect.value;
        const targetLang = this.targetLangSelect.value;
        const text = this.sourceText.value.trim();

        if (!text) {
            this.showAlert('Please enter some text to translate', 'warning');
            return;
        }

        if (sourceLang === targetLang) {
            this.showAlert('Please select different source and target languages', 'warning');
            return;
        }

        this.setLoading(true);
        this.translateBtn.disabled = true;

        const requestBody = {
            source_lang: sourceLang,
            target_lang: targetLang,
            text: text
        };

        if (this.streamModeSelect.value) {
            requestBody.stream = this.streamModeSelect.value === 'true';
        }
        if (this.temperatureInput.value) {
            requestBody.temperature = parseFloat(this.temperatureInput.value);
        }
        if (this.topPInput.value) {
            requestBody.top_p = parseFloat(this.topPInput.value);
        }

        try {
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });
            const result = await response.json();

            if (result.success) {
                this.translationText.value = result.translation;
                this.showEvaluationSection();
                this.showAlert('Translation completed successfully!', 'success');
                this.playTranslationBtn.disabled = false;
            } else {
                this.showAlert(`Translation failed: ${result.error}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Network error: ${error.message}`, 'danger');
        } finally {
            this.setLoading(false);
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

        this.setLoading(true);
        this.evaluateBtn.disabled = true;

        try {
            const response = await fetch('/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
            this.setLoading(false);
            this.evaluateBtn.disabled = false;
        }
    }

    async playText(type) {
        let text, language, button;
        
        if (type === 'source') {
            text = this.sourceText.value.trim();
            language = this.sourceLangSelect.value;
            button = this.playSourceBtn;
        } else {
            text = this.translationText.value.trim();
            language = this.targetLangSelect.value;
            button = this.playTranslationBtn;
        }

        if (!text) {
            this.showAlert('No text to play', 'warning');
            return;
        }

        if (text.length > 500) {
            text = text.substring(0, 500) + '...';
            this.showAlert('Text truncated to 500 characters for speech synthesis', 'info');
        }

        const originalHTML = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Loading...';

        try {
            const response = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text, language: language })
            });
            const result = await response.json();

            if (result.success) {
                const audioBlob = this.base64ToBlob(result.audio_data, 'audio/mp3');
                const audioUrl = URL.createObjectURL(audioBlob);
                
                this.audioPlayer.pause();
                this.audioPlayer.currentTime = 0;
                this.audioPlayer.src = audioUrl;
                
                button.innerHTML = '<i class="fas fa-stop me-1"></i>Stop';
                button.disabled = false;
                
                this.audioPlayer.onended = () => {
                    button.innerHTML = originalHTML;
                    URL.revokeObjectURL(audioUrl);
                };
                
                this.audioPlayer.onerror = () => {
                    this.showAlert('Error playing audio', 'danger');
                    button.innerHTML = originalHTML;
                    button.disabled = false;
                    URL.revokeObjectURL(audioUrl);
                };
                
                await this.audioPlayer.play();
                
                const stopHandler = () => {
                    this.audioPlayer.pause();
                    this.audioPlayer.currentTime = 0;
                    button.innerHTML = originalHTML;
                    button.removeEventListener('click', stopHandler);
                    URL.revokeObjectURL(audioUrl);
                };
                button.addEventListener('click', stopHandler, { once: true });
                
            } else {
                this.showAlert(`Text-to-speech failed: ${result.error}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`TTS error: ${error.message}`, 'danger');
        } finally {
            if (button.innerHTML.includes('Loading')) {
                button.innerHTML = originalHTML;
                button.disabled = false;
            }
        }
    }

    // --- 3. UI UPDATE METHODS ---
    updateCharCount() {
        const count = this.sourceText.value.length;
        this.charCount.textContent = count;
        
        if (count > 1000) {
            this.charCount.style.color = '#dc3545';
        } else if (count > 500) {
            this.charCount.style.color = '#ffc107';
        } else {
            this.charCount.style.color = '#6c757d';
        }
        
        this.playSourceBtn.disabled = !this.sourceText.value.trim();
    }

    displayEvaluationResult(score, justification) {
        this.scoreValue.textContent = score;
        this.justificationText.textContent = justification;

        const percentage = (score / 10) * 100;
        this.scoreBar.style.width = `${percentage}%`;
        this.scoreBar.setAttribute('aria-valuenow', score);

        const scoreDisplay = document.querySelector('.score-display');
        const progressBar = this.scoreBar;
        
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

    setLoading(isLoading) {
        this.loadingOverlay.style.display = isLoading ? 'flex' : 'none';
    }

    showAlert(message, type) {
        const existingAlerts = document.querySelectorAll('.alert-dismissible');
        existingAlerts.forEach(alert => alert.remove());

        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
        
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(alertDiv);

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // --- 4. HELPER METHODS ---
    base64ToBlob(audioData, mimeType) {
        try {
            if (audioData.match(/^[0-9a-fA-F]+$/)) {
                const byteNumbers = new Array(audioData.length / 2);
                for (let i = 0; i < audioData.length; i += 2) {
                    byteNumbers[i / 2] = parseInt(audioData.substr(i, 2), 16);
                }
                const byteArray = new Uint8Array(byteNumbers);
                return new Blob([byteArray], { type: mimeType });
            } else {
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

document.addEventListener('DOMContentLoaded', () => {
    new TranslationApp();
}); 