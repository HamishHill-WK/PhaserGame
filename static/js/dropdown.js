// Dropdown functionality
function toggleDropdown() {
    const dropdown = document.getElementById("dropdown-content");
    dropdown.classList.toggle("show");
}

// Close dropdown when clicking outside
window.onclick = function(event) {
    if (!event.target.matches('.dropdown-btn') && !event.target.closest('.dropdown-content')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}

// Handle checkbox changes
document.addEventListener('DOMContentLoaded', function() {
    Object.keys(taskDependencies).forEach(taskId => {
        const checkbox = document.getElementById(taskId);
        if (checkbox) {
            checkbox.addEventListener('click', function(event) {
                //event.preventDefault();
                const current = this.checked
                handleTaskChange(taskId, current, event);
            });
        }
    });
    resetTasks(); // Initialize settings on page load
});

// Task dependencies - define which tasks depend on which
const taskDependencies = {
    'task1': [], // Task 1 - no dependencies
    'task2': ['task1'], // Task 2 depends on Task 1
    'task3': ['task1', 'task2'], // Task 3 depends on Tasks 1 & 2
    'task4': ['task1', 'task2', 'task3'], // Task 4 depends on 1, 2 & 3
    'task5': ['task1', 'task2', 'task3', 'task4'] // Task 5 depends on all previous
};

function resetTasks() {
    document.getElementById('task1').checked = false;
    document.getElementById('task2').checked = false;
    document.getElementById('task3').checked = false;
    document.getElementById('task4').checked = false;
    document.getElementById('task5').checked = false;
}

function handleTaskChange(taskId, isChecked, event) {
    const dependencies = taskDependencies[taskId];
    console.log(`Task ${taskId} changed to ${isChecked}. Checking dependencies...`);
    //if (isChecked === false) {
        console.log(`checking ${taskId}. Checking dependencies...`);
        let canCheck = true;

        dependencies.forEach(dep => {
            const depCheckbox = document.getElementById(dep);
            if (depCheckbox && !depCheckbox.checked) {
                canCheck = false; // Can uncheck if all dependencies are checked
            } 
        });

        if (canCheck) {
            // If no dependencies are checked, reset the task
            document.getElementById(taskId).checked = true;
            console.warn(`checking ${taskId} due to met dependencies.`);
        }
        else{
            document.getElementById(taskId).checked = false;
            console.warn(`Cannot check ${taskId} due to unmet dependencies.`);
        }
    //} 
}