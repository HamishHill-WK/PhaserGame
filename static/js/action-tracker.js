// static/js/user-action-tracker.js
class UserActionTracker {
    constructor(experimentLogger) {
        this.logger = experimentLogger;
        this.editor = null;
        this.lastCode = '';
        this.editSession = null;
        this.setupCodeEditorTracking();
        this.setupUITracking();
        this.setupAITracking();
    }

    setupCodeEditorTracking() {
        // Wait for editor to be ready
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                this.editor = ace.edit("editor");
                if (this.editor) {
                    this.initializeEditorTracking();
                }
            }, 1000);
        });
    }    initializeEditorTracking() {        
        // Track when user saves code
        this.setupSaveTracking();

        // Track when user clicks in editor
        this.editor.on('focus', () => {
            this.logger.logAction(ActionCodes.CODE_FOCUS, {
                timestamp: Date.now()
            });
        });

        this.editor.on('blur', () => {
            this.logger.logAction(ActionCodes.CODE_BLUR, {
                code_length: this.editor.getValue().length,
                timestamp: Date.now()
            });
        });

        // Store initial code state
        this.lastCode = this.editor.getValue();
    }    setupSaveTracking() {
        // Listen for save button clicks - just track, don't trigger save
        const saveButton = document.getElementById('save-code');
        if (saveButton) {
            saveButton.addEventListener('click', () => {
                this.trackCodeSave();
            });
        }
    }trackCodeSave() {
        const currentCode = this.editor.getValue();
        const lineChanges = this.calculateLineChanges(this.lastCode, currentCode);
        
        this.logger.logAction(ActionCodes.CODE_SAVE, {
            total_lines: currentCode.split('\n').length,
            total_characters: currentCode.length,
            lines_added: lineChanges.added,
            lines_removed: lineChanges.removed,
            lines_modified: lineChanges.modified,
            net_change: currentCode.length - this.lastCode.length,
            code_content: currentCode,
            previous_length: this.lastCode.length,
            save_timestamp: Date.now()
        });

        // Update the stored code state
        this.lastCode = currentCode;
    }

    calculateLineChanges(oldCode, newCode) {
        const oldLines = oldCode.split('\n');
        const newLines = newCode.split('\n');
        
        // Simple diff calculation
        const maxLines = Math.max(oldLines.length, newLines.length);
        let added = 0, removed = 0, modified = 0;
        
        if (newLines.length > oldLines.length) {
            added = newLines.length - oldLines.length;
        } else if (oldLines.length > newLines.length) {
            removed = oldLines.length - newLines.length;
        }
        
        // Count modified lines (simple comparison)
        const minLines = Math.min(oldLines.length, newLines.length);
        for (let i = 0; i < minLines; i++) {
            if (oldLines[i] !== newLines[i]) {
                modified++;
            }
        }
        
        return { added, removed, modified };
    }
}