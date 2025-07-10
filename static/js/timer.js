// Experiment Timer - 1 hour countdown
class ExperimentTimer {
    constructor() {
        this.duration = 60 * 60; // 1 hour in seconds
        this.timeRemaining = this.duration;
        this.timerInterval = null;
        this.timerElement = document.getElementById('timer-text');
        this.timerContainer = document.getElementById('experiment-timer');
        
        // Check if timer was already started in previous session
        this.loadTimerState();
        this.startTimer();
    }

    loadTimerState() {
        const savedStartTime = localStorage.getItem('experiment_start_time');
        if (savedStartTime) {
            const startTime = parseInt(savedStartTime);
            const currentTime = Date.now();
            const elapsedSeconds = Math.floor((currentTime - startTime) / 1000);
            
            this.timeRemaining = Math.max(0, this.duration - elapsedSeconds);
            
            if (this.timeRemaining === 0) {
                this.handleTimeUp();
                return;
            }
        } else {
            // First time starting - save start time
            localStorage.setItem('experiment_start_time', Date.now().toString());
        }
    }

    startTimer() {
        this.updateDisplay();
        
        this.timerInterval = setInterval(() => {
            this.timeRemaining--;
            this.updateDisplay();
            
            // Save progress periodically
            if (this.timeRemaining % 60 === 0) {
                this.saveProgress();
            }
            
            // Warning states
            if (this.timeRemaining <= 300) { // Last 5 minutes
                this.timerContainer.classList.add('critical');
            } else if (this.timeRemaining <= 600) { // Last 10 minutes
                this.timerContainer.classList.add('warning');
            }
            
            if (this.timeRemaining <= 0) {
                this.handleTimeUp();
            }
        }, 1000);
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        if (this.timerElement) {
            this.timerElement.textContent = timeString;
        }
    }    saveProgress() {
        // Save current timer state
        const experimentData = {
            timeElapsed: this.duration - this.timeRemaining,
            lastSaved: Date.now()
        };
        
        localStorage.setItem('experiment_data', JSON.stringify(experimentData));
    }

    handleTimeUp() {
        // Stop the timer
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }

        // Save final progress
        this.saveProgress();

        // Show time up message
        if (this.timerElement) {
            this.timerElement.textContent = '00:00';
        }

        // Redirect to debrief page after a short delay
        setTimeout(() => {
            alert('Time is up! The experiment is complete. You will now be redirected to the next page.');
            window.location.href = '/sus';
        }, 1000);
    }

    // Method to manually end experiment early (if needed)
    endExperiment() {
        this.handleTimeUp();
    }
}

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check for development mode
    const isDevelopment = window.location.hostname === 'localhost' || 
                         window.location.hostname === '127.0.0.1' ||
                         window.location.search.includes('dev=true');
    // Only start timer if not on the tutorial page
    const isTutorial = window.location.pathname.includes('tutorial');
    if (document.getElementById('experiment-timer') && !isDevelopment && !isTutorial) {
        window.experimentTimer = new ExperimentTimer();
    } else if (isDevelopment && document.getElementById('experiment-timer')) {
        // Show timer but do not start countdown in dev mode
        const timerText = document.getElementById('timer-text');
        if (timerText) {
            timerText.textContent = '60:00';
        }
        // Optionally, add a class to indicate dev mode
        document.getElementById('experiment-timer').style.opacity = '0.7';
    } else if (isTutorial) {
        // Show timer but do not start countdown; set to 60:00
        const timerText = document.getElementById('timer-text');
        if (timerText) {
            timerText.textContent = '60:00';
        }
    }
});
