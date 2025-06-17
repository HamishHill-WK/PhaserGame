function toggleGameDevPosition() {
    const experience = document.getElementById('game_dev_experience_detailed').value;
    const positionGroup = document.getElementById('gamedev-position-group');
    
    if (experience === 'professional') {
        positionGroup.style.display = 'block';
    } else {
        positionGroup.style.display = 'none';
        document.getElementById('gamedev_position').value = '';
    }
}

function toggleProgrammingPosition() {
    const experience = document.getElementById('programming_experience_detailed').value;
    const positionGroup = document.getElementById('programming-position-group');
    
    if (experience === 'professional') {
        positionGroup.style.display = 'block';
    } else {
        positionGroup.style.display = 'none';
        document.getElementById('programming_position').value = '';
    }
}

function toggleAIUsage() {
    const usesAI = document.querySelector('input[name="uses_ai_tools"]:checked')?.value;
    const aiUsageGroup = document.getElementById('ai-usage-group');
    const aiDetailsGroup = document.getElementById('ai-details-group');
    
    if (usesAI === 'yes') {
        aiUsageGroup.style.display = 'block';
        aiDetailsGroup.style.display = 'block';
    } else {
        aiUsageGroup.style.display = 'none';
        aiDetailsGroup.style.display = 'none';
        // Clear AI usage checkboxes
        document.querySelectorAll('input[name="ai_usage"]').forEach(cb => cb.checked = false);
        document.getElementById('ai_usage_details').value = '';
    }
}

function toggleJavaScriptUsage() {
    const usesJS = document.querySelector('input[name="languages"][value="javascript"]:checked');
    const jsUsageGroup = document.getElementById('javascript-usage-group');
    console.log(usesJS);
    if (usesJS) {
        jsUsageGroup.style.display = 'block';
    } else {
        jsUsageGroup.style.display = 'none';
    }
}

function togglePhaserUsage(){
    const usesPhaser = document.querySelector('input[name="used_phaser"]:checked')?.value;
    const phaserUsageGroup = document.getElementById('phaser-details-group');

    if (usesPhaser === 'yes') {
        phaserUsageGroup.style.display = 'block';
    } else {
        phaserUsageGroup.style.display = 'none';
    }
}

// Handle core languages "none" option
document.addEventListener('DOMContentLoaded', function() {
    const noneCheckbox = document.querySelector('input[value="none"][name="core_languages"]');
    const otherCheckboxes = document.querySelectorAll('input[name="core_languages"]:not([value="none"])');
    
    if (noneCheckbox) {
        noneCheckbox.addEventListener('change', function() {
            if (this.checked) {
                otherCheckboxes.forEach(cb => cb.checked = false);
            }
        });
    }
    
    otherCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                noneCheckbox.checked = false;
            }
        });
    });
    
    // Initialize conditional fields on page load
    toggleGameDevPosition();
    toggleProgrammingPosition();
    toggleAIUsage();
    toggleJavaScriptUsage();
    togglePhaserUsage();
});
