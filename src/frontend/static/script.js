class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        this.chatMessages = document.getElementById('chat-messages');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.loadingOverlay = document.getElementById('loading-overlay');
        
        this.isWaitingForResponse = false;
        this.conversationEnded = false;
        
        this.initializeEventListeners();
        this.enableChat();
    }
    
    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key press
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Input validation
        this.messageInput.addEventListener('input', () => {
            this.updateSendButton();
        });
        
        // Prevent form submission
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.shiftKey) {
                // Allow Shift+Enter for new lines
                return;
            }
        });
    }
    
    enableChat() {
        // Hide loading overlay and enable input
        setTimeout(() => {
            this.loadingOverlay.style.display = 'none';
            this.messageInput.disabled = false;
            this.updateSendButton();
            this.messageInput.focus();
        }, 1000);
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        const canSend = hasText && !this.isWaitingForResponse && !this.conversationEnded;
        
        this.sendButton.disabled = !canSend;
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isWaitingForResponse || this.conversationEnded) {
            return;
        }
        
        // Clear input and disable controls
        this.messageInput.value = '';
        this.isWaitingForResponse = true;
        this.updateSendButton();
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            // Send message to backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (!response.ok) {
                throw new Error(data.error || 'Network error occurred');
            }
            
            // Add bot response to chat
            this.addMessage(data.reply, 'bot');
            
            // Check if conversation ended
            if (data.conversation_ended) {
                this.conversationEnded = true;
                this.messageInput.disabled = true;
                this.addSystemMessage("Conversation ended. Refresh the page to start a new conversation.");
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.hideTypingIndicator();
            this.addErrorMessage(`Error: ${error.message}`);
        } finally {
            this.isWaitingForResponse = false;
            this.updateSendButton();
            
            if (!this.conversationEnded) {
                this.messageInput.focus();
            }
        }
    }
    
    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const senderName = sender === 'user' ? 'You 💬' : 'ShopAssist Bot 🤖';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <span class="sender">${senderName}</span>
                <div class="text">${this.formatMessage(text)}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addSystemMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';
        
        messageDiv.innerHTML = `
            <div class="message-content">
                <span class="sender">System 📢</span>
                <div class="text">${text}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addErrorMessage(text) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = text;
        
        this.chatMessages.appendChild(errorDiv);
        this.scrollToBottom();
        
        // Auto-remove error message after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }
    
    formatMessage(text) {
        // Convert line breaks to HTML
        return text
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Bold text
            .replace(/\*(.*?)\*/g, '<em>$1</em>');  // Italic text
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    // Method to handle connection errors
    handleConnectionError() {
        this.addErrorMessage('Unable to connect to the chat service. Please check your internet connection and try again.');
        this.isWaitingForResponse = false;
        this.updateSendButton();
    }
    
    // Method to reset conversation
    resetConversation() {
        if (confirm('Are you sure you want to start a new conversation? This will clear all messages.')) {
            location.reload();
        }
    }
}

// Initialize the chat application when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Check if the browser supports required features
    if (!window.fetch) {
        alert('Your browser is not supported. Please use a modern browser.');
        return;
    }
    
    try {
        new ChatApp();
    } catch (error) {
        console.error('Failed to initialize chat app:', error);
        alert('Failed to initialize the chat application. Please refresh the page.');
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Re-focus input when page becomes visible (mobile friendly)
        const input = document.getElementById('message-input');
        if (input && !input.disabled) {
            setTimeout(() => input.focus(), 100);
        }
    }
});

// Handle connection status
window.addEventListener('online', () => {
    console.log('Connection restored');
    // Could add a message or indicator here
});

window.addEventListener('offline', () => {
    console.log('Connection lost');
    // Could add a message or indicator here
});