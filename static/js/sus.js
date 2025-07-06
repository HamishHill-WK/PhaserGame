// SUS form JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('sus-form');
    const submitBtn = document.querySelector('.submit-btn');
    
    // Add smooth scrolling for better UX
    function smoothScrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
    
    // Form validation
    function validateForm() {
        const questions = [];
        let allAnswered = true;
        
        // Check each question (q1 through q10)
        for (let i = 1; i <= 10; i++) {
            const questionInputs = document.querySelectorAll(`input[name="q${i}"]`);
            const isAnswered = Array.from(questionInputs).some(input => input.checked);
            
            if (!isAnswered) {
                allAnswered = false;
                // Highlight unanswered question
                const questionItem = document.querySelector(`input[name="q${i}"]`).closest('.question-item');
                questionItem.classList.add('sus-form-invalid');
            } else {
                // Remove invalid styling if answered
                const questionItem = document.querySelector(`input[name="q${i}"]`).closest('.question-item');
                questionItem.classList.remove('sus-form-invalid');
            }
        }
        
        return allAnswered;
    }
    
    // Real-time validation feedback
    const radioInputs = document.querySelectorAll('input[type="radio"]');
    radioInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Remove invalid styling when question is answered
            const questionItem = this.closest('.question-item');
            questionItem.classList.remove('sus-form-invalid');
            
            // Update submit button state
            updateSubmitButton();
        });
    });
    
    function updateSubmitButton() {
        const totalQuestions = 10;
        let answeredQuestions = 0;
        
        for (let i = 1; i <= totalQuestions; i++) {
            const questionInputs = document.querySelectorAll(`input[name="q${i}"]`);
            const isAnswered = Array.from(questionInputs).some(input => input.checked);
            if (isAnswered) answeredQuestions++;
        }
        
        // Enable submit button only when all questions are answered
        if (answeredQuestions === totalQuestions) {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Responses';
        } else {
            submitBtn.disabled = true;
            submitBtn.textContent = `Submit Responses (${answeredQuestions}/${totalQuestions} completed)`;
        }
    }
    
    // Form submission handling
    form.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            
            // Show error message
            let errorMsg = document.querySelector('.error-message');
            if (!errorMsg) {
                errorMsg = document.createElement('div');
                errorMsg.className = 'error-message';
                errorMsg.textContent = 'Please answer all questions before submitting.';
                form.insertBefore(errorMsg, document.querySelector('.sus-submit'));
            }
            errorMsg.classList.add('show');
            
            // Scroll to first unanswered question
            const firstInvalid = document.querySelector('.sus-form-invalid');
            if (firstInvalid) {
                firstInvalid.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
            
            return false;
        } else {
            // Hide any error messages
            const errorMsg = document.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.classList.remove('show');
            }
            
            // Show loading state
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
        }
    });
    
    // Initialize submit button state
    updateSubmitButton();
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.target.type === 'radio') {
            // Allow Enter key to select radio buttons
            e.target.checked = true;
            e.target.dispatchEvent(new Event('change'));
        }
    });
    
    // Add progress indicator
    function addProgressIndicator() {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'progress-container';
        progressContainer.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
            <div class="progress-text" id="progress-text">0 of 10 questions completed</div>
        `;
        
        // Insert after instructions
        const instructions = document.querySelector('.sus-instructions');
        instructions.insertAdjacentElement('afterend', progressContainer);
        
        // Add CSS for progress indicator
        const style = document.createElement('style');
        style.textContent = `
            .progress-container {
                margin: 20px 0 30px 0;
                text-align: center;
            }
            .progress-bar {
                width: 100%;
                height: 8px;
                background-color: #e9ecef;
                border-radius: 4px;
                overflow: hidden;
                margin-bottom: 8px;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #007bff, #0056b3);
                width: 0%;
                transition: width 0.3s ease;
            }
            .progress-text {
                font-size: 14px;
                color: #666;
                font-weight: 500;
            }
        `;
        document.head.appendChild(style);
    }
    
    function updateProgress() {
        const totalQuestions = 10;
        let answeredQuestions = 0;
        
        for (let i = 1; i <= totalQuestions; i++) {
            const questionInputs = document.querySelectorAll(`input[name="q${i}"]`);
            const isAnswered = Array.from(questionInputs).some(input => input.checked);
            if (isAnswered) answeredQuestions++;
        }
        
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        
        if (progressFill && progressText) {
            const percentage = (answeredQuestions / totalQuestions) * 100;
            progressFill.style.width = percentage + '%';
            progressText.textContent = `${answeredQuestions} of ${totalQuestions} questions completed`;
        }
    }
    
    // Add progress indicator
    addProgressIndicator();
    
    // Update progress when radio buttons change
    radioInputs.forEach(input => {
        input.addEventListener('change', updateProgress);
    });
    
    // Initial progress update
    updateProgress();
});