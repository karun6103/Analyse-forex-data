// Claude AI Frontend Application
class ClaudeAI {
    constructor() {
        this.isLoading = false;
        this.conversationHistory = [];
        this.currentSystemPrompt = '';
        
        this.initializeElements();
        this.bindEvents();
        this.loadSystemPrompt();
        this.showWelcomeMessage();
        
        // Auto-resize textarea
        this.setupAutoResize();
    }
    
    initializeElements() {
        // Chat elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.conversationSummary = document.getElementById('conversationSummary');
        
        // Header buttons
        this.clearBtn = document.getElementById('clearBtn');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.exportBtn = document.getElementById('exportBtn');
        
        // Modal elements
        this.settingsModal = document.getElementById('settingsModal');
        this.systemPromptTextarea = document.getElementById('systemPrompt');
        this.saveSettingsBtn = document.getElementById('saveSettingsBtn');
        this.cancelSettingsBtn = document.getElementById('cancelSettingsBtn');
        this.closeSettingsBtn = document.getElementById('closeSettingsBtn');
        this.viewHistoryBtn = document.getElementById('viewHistoryBtn');
        this.exportHistoryBtn = document.getElementById('exportHistoryBtn');
        
        // Toast container
        this.toastContainer = document.getElementById('toastContainer');
    }
    
    bindEvents() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Header button events
        this.clearBtn.addEventListener('click', () => this.clearConversation());
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.exportBtn.addEventListener('click', () => this.exportConversation());
        
        // Modal events
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        this.cancelSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.closeSettingsBtn.addEventListener('click', () => this.closeSettings());
        this.viewHistoryBtn.addEventListener('click', () => this.viewHistory());
        this.exportHistoryBtn.addEventListener('click', () => this.exportConversation());
        
        // Modal backdrop click
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.closeSettings();
            }
        });
        
        // Focus message input on load
        this.messageInput.focus();
    }
    
    setupAutoResize() {
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 200) + 'px';
        });
    }
    
    showWelcomeMessage() {
        // Welcome message is already in HTML, just ensure it's visible
        this.updateConversationSummary('Ready to chat');
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        // Add user message to chat
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Show loading
        this.setLoading(true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add Claude's response to chat
            this.addMessage('assistant', data.response, data.formatted_response);
            this.updateConversationSummary(data.conversation_summary);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast('Error: ' + error.message, 'error');
            this.addMessage('assistant', '❌ Sorry, I encountered an error processing your message. Please try again.', null, true);
        } finally {
            this.setLoading(false);
            this.messageInput.focus();
        }
    }
    
    addMessage(role, content, formattedContent = null, isError = false) {
        // Remove welcome message if this is the first real message
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage && (role === 'user' || role === 'assistant')) {
            welcomeMessage.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (isError) {
            bubble.style.borderLeft = '4px solid #e74c3c';
        }
        
        // Use formatted content if available, otherwise use plain content
        if (formattedContent) {
            bubble.innerHTML = formattedContent;
        } else {
            bubble.textContent = content;
        }
        
        const timestamp = document.createElement('div');
        timestamp.className = 'message-time';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        messageContent.appendChild(bubble);
        messageContent.appendChild(timestamp);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    setLoading(loading) {
        this.isLoading = loading;
        this.sendBtn.disabled = loading;
        this.loadingIndicator.style.display = loading ? 'flex' : 'none';
        
        if (loading) {
            this.scrollToBottom();
        }
    }
    
    updateConversationSummary(summary) {
        this.conversationSummary.textContent = summary;
    }
    
    async clearConversation() {
        if (!confirm('Are you sure you want to clear the conversation?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/conversation/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Clear chat messages
            this.chatMessages.innerHTML = '';
            this.showWelcomeMessage();
            this.updateConversationSummary('Ready to chat');
            
            this.showToast('Conversation cleared successfully', 'success');
            
        } catch (error) {
            console.error('Error clearing conversation:', error);
            this.showToast('Error clearing conversation: ' + error.message, 'error');
        }
    }
    
    async loadSystemPrompt() {
        try {
            const response = await fetch('/api/system-prompt');
            if (response.ok) {
                const data = await response.json();
                this.currentSystemPrompt = data.system_prompt;
                this.systemPromptTextarea.value = this.currentSystemPrompt;
            }
        } catch (error) {
            console.error('Error loading system prompt:', error);
        }
    }
    
    openSettings() {
        this.settingsModal.style.display = 'flex';
        this.systemPromptTextarea.value = this.currentSystemPrompt;
        this.systemPromptTextarea.focus();
    }
    
    closeSettings() {
        this.settingsModal.style.display = 'none';
    }
    
    async saveSettings() {
        const newSystemPrompt = this.systemPromptTextarea.value.trim();
        
        if (!newSystemPrompt) {
            this.showToast('System prompt cannot be empty', 'warning');
            return;
        }
        
        try {
            const response = await fetch('/api/system-prompt', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ system_prompt: newSystemPrompt })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.currentSystemPrompt = newSystemPrompt;
            this.closeSettings();
            this.showToast('Settings saved successfully', 'success');
            
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showToast('Error saving settings: ' + error.message, 'error');
        }
    }
    
    async viewHistory() {
        try {
            const response = await fetch('/api/conversation/history');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.history && data.history.length > 0) {
                let historyText = 'Conversation History:\\n\\n';
                data.history.forEach((msg, index) => {
                    historyText += `${index + 1}. [${msg.role.toUpperCase()}] ${msg.timestamp}\\n${msg.content}\\n\\n`;
                });
                
                // Create a new window/modal to show history
                const historyWindow = window.open('', '_blank', 'width=800,height=600');
                historyWindow.document.write(`
                    <html>
                        <head>
                            <title>Conversation History</title>
                            <style>
                                body { font-family: monospace; padding: 20px; line-height: 1.6; }
                                .message { margin-bottom: 20px; padding: 10px; border-left: 3px solid #ccc; }
                                .user { border-left-color: #667eea; }
                                .assistant { border-left-color: #3498db; }
                                .role { font-weight: bold; color: #333; }
                                .timestamp { font-size: 0.8em; color: #666; }
                                .content { margin-top: 5px; }
                            </style>
                        </head>
                        <body>
                            <h1>Conversation History</h1>
                            <p><strong>Summary:</strong> ${data.summary}</p>
                            <hr>
                            ${data.history.map((msg, index) => `
                                <div class="message ${msg.role}">
                                    <div class="role">${msg.role.toUpperCase()} #${index + 1}</div>
                                    <div class="timestamp">${msg.timestamp}</div>
                                    <div class="content">${msg.formatted_content || msg.content}</div>
                                </div>
                            `).join('')}
                        </body>
                    </html>
                `);
            } else {
                this.showToast('No conversation history found', 'warning');
            }
            
        } catch (error) {
            console.error('Error viewing history:', error);
            this.showToast('Error viewing history: ' + error.message, 'error');
        }
    }
    
    async exportConversation() {
        try {
            const response = await fetch('/api/conversation/export');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Create download link
            const blob = new Blob([data.conversation], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            this.showToast('Conversation exported successfully', 'success');
            
        } catch (error) {
            console.error('Error exporting conversation:', error);
            this.showToast('Error exporting conversation: ' + error.message, 'error');
        }
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        this.toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
        
        // Click to dismiss
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
}

// Health check function
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('✅ Claude AI service is healthy');
            console.log('Model:', data.model);
        } else {
            console.warn('⚠️ Claude AI service is unhealthy:', data.error);
        }
    } catch (error) {
        console.error('❌ Health check failed:', error);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.claudeAI = new ClaudeAI();
    checkHealth();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Escape to close modals
        if (e.key === 'Escape') {
            if (window.claudeAI.settingsModal.style.display === 'flex') {
                window.claudeAI.closeSettings();
            }
        }
        
        // Ctrl+K to focus message input
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            window.claudeAI.messageInput.focus();
        }
        
        // Ctrl+L to clear conversation
        if (e.ctrlKey && e.key === 'l') {
            e.preventDefault();
            window.claudeAI.clearConversation();
        }
    });
    
    console.log('🤖 Claude AI Assistant initialized');
    console.log('Keyboard shortcuts:');
    console.log('  Ctrl+Enter: Send message');
    console.log('  Ctrl+K: Focus message input');
    console.log('  Ctrl+L: Clear conversation');
    console.log('  Escape: Close modals');
});