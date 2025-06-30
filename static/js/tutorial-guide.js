// tutorial-guide.js
// Step-by-step guided overlay for the tutorial page

const tutorialSteps = [
  {
    selector: '#game-container',
    title: 'Game Area',
    content: 'This is the game area. You will see the game here and test your code changes in real time.'
  },
  {
    selector: '.editor-container',
    title: 'Code Editor',
    content: 'This is the code editor. Edit the game logic here to complete tasks.'
  },
  {
    selector: '#console-container',
    title: 'Console',
    content: 'The console displays output and error messages from your code.'
  },
  {
    selector: '#input-form',
    title: 'AI Assistant',
    content: 'Use the chat box to ask the AI assistant for help or code suggestions.'
  },
  // Switch to code editor after AI assistant explanation
  {
    selector: '#editor',
    title: 'Code Editor',
    content: 'This is the code editor. Edit the game logic here to complete tasks.',
    onShow: function() {
      // Switch to code tab
      var codeBtn = document.getElementById('code-button');
      if (codeBtn) codeBtn.click();
    }
  },
  {
    selector: '.dropdown-btn',
    title: 'Task List',
    content: 'Click here to view your list of tasks. Each task describes a feature to implement.'
  },
  {
    selector: '#save-code',
    title: 'Save Changes',
    content: 'Click here to save your code changes.'
  },
  {
    selector: '#reload-game',
    title: 'Reload Game',
    content: 'Click here to reload the game and test your changes.'
  },
  {
    selector: '#finish-experiment-btn',
    title: 'Finish Experiment',
    content: 'When you have completed all tasks, click here to finish the experiment.'
  }
];

let currentStep = 0;

function showTutorialStep(stepIdx) {
  removeTutorialOverlay();
  const step = tutorialSteps[stepIdx];
  if (!step) return;
  const target = document.querySelector(step.selector);
  if (!target) return;

  // If step has onShow, call it
  if (typeof step.onShow === 'function') step.onShow();

  // Highlight target
  const rect = target.getBoundingClientRect();
  const overlay = document.createElement('div');
  overlay.className = 'tutorial-overlay';
  overlay.style.position = 'fixed';
  overlay.style.left = rect.left + 'px';
  overlay.style.top = rect.top + 'px';
  overlay.style.width = rect.width + 'px';
  overlay.style.height = rect.height + 'px';
  overlay.style.background = 'rgba(0, 123, 255, 0.15)';
  overlay.style.border = '2px solid #007bff';
  overlay.style.zIndex = 2000;
  overlay.style.pointerEvents = 'none';
  document.body.appendChild(overlay);

  // Tooltip
  const tooltip = document.createElement('div');
  tooltip.className = 'tutorial-tooltip';
  tooltip.style.position = 'fixed';

  // Calculate tooltip position to keep it on screen
  let tooltipLeft = rect.left + rect.width + 16;
  let tooltipTop = rect.top;
  const tooltipWidth = 340; // maxWidth + padding
  const tooltipHeight = 160; // estimated, will adjust below
  const padding = 16;

  // If tooltip would go off right edge, place to the left
  if (tooltipLeft + tooltipWidth > window.innerWidth) {
    tooltipLeft = rect.left - tooltipWidth - padding;
    if (tooltipLeft < 0) tooltipLeft = padding;
  }
  // If tooltip would go off bottom, adjust up
  if (tooltipTop + tooltipHeight > window.innerHeight) {
    tooltipTop = window.innerHeight - tooltipHeight - padding;
    if (tooltipTop < 0) tooltipTop = padding;
  }

  tooltip.style.left = tooltipLeft + 'px';
  tooltip.style.top = tooltipTop + 'px';
  tooltip.style.background = '#fff';
  tooltip.style.border = '1px solid #007bff';
  tooltip.style.borderRadius = '8px';
  tooltip.style.boxShadow = '0 2px 8px rgba(0,0,0,0.12)';
  tooltip.style.padding = '20px 28px';
  tooltip.style.zIndex = 2001;
  tooltip.style.maxWidth = '320px';
  tooltip.style.wordBreak = 'break-word';
  tooltip.innerHTML = `<h3 style='margin-top:0;'>${step.title}</h3><p>${step.content}</p><button id='next-tutorial-step' class='tab-button'>${stepIdx === tutorialSteps.length-1 ? 'Finish Tutorial' : 'Next'}</button>`;
  document.body.appendChild(tooltip);

  // Adjust tooltip height if needed
  const actualTooltipHeight = tooltip.offsetHeight;
  if (tooltipTop + actualTooltipHeight > window.innerHeight) {
    tooltip.style.top = (window.innerHeight - actualTooltipHeight - padding) + 'px';
  }

  document.getElementById('next-tutorial-step').onclick = function(e) {
    e.stopPropagation();
    if (stepIdx < tutorialSteps.length - 1) {
      showTutorialStep(stepIdx + 1);
    } else {
      removeTutorialOverlay();
      if (window.tutorialComplete) window.tutorialComplete();
    }
  };
}

function removeTutorialOverlay() {
  document.querySelectorAll('.tutorial-overlay, .tutorial-tooltip').forEach(el => el.remove());
}

window.startTutorialGuide = function() {
  currentStep = 0;
  showTutorialStep(currentStep);
};

document.addEventListener('DOMContentLoaded', function() {
  if (window.location.pathname.includes('tutorial')) {
    setTimeout(() => startTutorialGuide(), 500);
  }
});
