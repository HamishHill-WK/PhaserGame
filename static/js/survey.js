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
// Programming fields toggle
function toggleProgrammingFields() {
    var progExp = document.getElementById('programming_experience_detailed').value;
    var gameExp = document.getElementById('game_dev_experience_detailed').value;
    var show = (progExp && progExp !== 'none') || (gameExp && gameExp !== 'none');
    document.getElementById('programming-years-group').style.display = show ? 'block' : 'none';
    document.getElementById('programming-languages-group').style.display = show ? 'block' : 'none';
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('programming_experience_detailed').addEventListener('change', toggleProgrammingFields);
    document.getElementById('game_dev_experience_detailed').addEventListener('change', toggleProgrammingFields);
    toggleProgrammingFields();
});

function toggleProgrammingFields() {
    var progExp = document.getElementById('programming_experience_detailed').value;
    var gameExp = document.getElementById('game_dev_experience_detailed').value;
    var show = (progExp && progExp !== 'none') || (gameExp && gameExp !== 'none');
    document.getElementById('programming-years-group').style.display = show ? 'block' : 'none';
    document.getElementById('programming-languages-group').style.display = show ? 'block' : 'none';
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('programming_experience_detailed').addEventListener('change', toggleProgrammingFields);
    document.getElementById('game_dev_experience_detailed').addEventListener('change', toggleProgrammingFields);
    toggleProgrammingFields();
});

// Game engines toggle
function toggleGameEngines() {
    var exp = document.getElementById('game_dev_experience_detailed').value;
    document.getElementById('game-engines-group').style.display = (exp && exp !== 'none') ? 'block' : 'none';
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('game_dev_experience_detailed').addEventListener('change', toggleGameEngines);
    toggleGameEngines();
});

// Self-taught toggle
function toggleSelfTaughtFields() {
    var isSelfTaught = document.getElementById('is_self_taught').checked;
    document.getElementById('self-taught-details-group').style.display = isSelfTaught ? 'block' : 'none';
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('is_self_taught').addEventListener('change', toggleSelfTaughtFields);
    toggleSelfTaughtFields();
});

// Course programming experience toggle
function toggleCourseProgrammingExperience() {
    var isStudent = document.getElementById('is_student').checked;
    var isGraduate = document.getElementById('is_graduate').checked;
    document.getElementById('course-programming-experience-group').style.display = (isStudent || isGraduate) ? 'block' : 'none';
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('is_student').addEventListener('change', toggleCourseProgrammingExperience);
    document.getElementById('is_graduate').addEventListener('change', toggleCourseProgrammingExperience);
    toggleCourseProgrammingExperience();
});

// Undergrad year toggle
function toggleUndergradYear() {
    var degreeLevel = document.getElementById('degree_level_current').value;
    document.getElementById('undergrad-year-group').style.display = (degreeLevel === 'undergraduate') ? 'block' : 'none';
}
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('degree_level_current').addEventListener('change', toggleUndergradYear);
    toggleUndergradYear();
});

// Graduate fields toggle
function toggleGraduateFields() {
    var isGraduate = document.getElementById('is_graduate').checked;
    document.getElementById('degree-level-highest-group').style.display = isGraduate ? 'block' : 'none';
}
function toggleStudentFields() {
    var isStudent = document.getElementById('is_student').checked;
    document.getElementById('degree-level-current-group').style.display = isStudent ? 'block' : 'none';
}
document.addEventListener('DOMContentLoaded', function() {
    toggleGraduateFields();
    toggleStudentFields();
    document.getElementById('is_graduate').addEventListener('change', toggleGraduateFields);
    document.getElementById('is_student').addEventListener('change', toggleStudentFields);
});

// Word count and limit functionality for AI usage details and description fields
function setupWordCountLimit(textareaId, counterId, maxWords) {
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(counterId);
    if (!textarea || !counter) return;
    function updateCount() {
        const words = textarea.value.trim().split(/\s+/).filter(Boolean);
        let wordCount = words.length;
        if (wordCount > maxWords) {
            // Trim to max words
            textarea.value = words.slice(0, maxWords).join(' ');
            wordCount = maxWords;
        }
        counter.textContent = `${wordCount} / ${maxWords} words`;
    }
    textarea.addEventListener('input', updateCount);
    // Initialize on page load
    updateCount();
}

document.addEventListener('DOMContentLoaded', function() {
    setupWordCountLimit('ai_usage_details', 'ai_usage_details_count', 100);
    setupWordCountLimit('description', 'description_count', 100);
});

function toggleCourseRelated() {
    const isStudent = document.getElementById('is_student').checked;
    const isGraduate = document.getElementById('is_graduate').checked;
    const courseRelatedGroup = document.getElementById('course-related-group');
    if (isStudent || isGraduate) {
        courseRelatedGroup.style.display = 'block';
    } else {
        courseRelatedGroup.style.display = 'none';
        const radios = courseRelatedGroup.querySelectorAll('input[type="radio"]');
        radios.forEach(r => r.checked = false);
    }
}

document.getElementById('is_student').addEventListener('change', toggleCourseRelated);
document.getElementById('is_graduate').addEventListener('change', toggleCourseRelated);
document.addEventListener('DOMContentLoaded', toggleCourseRelated);
