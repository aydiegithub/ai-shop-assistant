class ChatApp {
    constructor() {
        this.messageInput = document.getElementById('message-input');
        this.sendBtn = document.getElementById('send-btn');
        this.chatForm = document.getElementById('chat-form');
        this.messagesContainer = document.getElementById('messages-container');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.clearChatBtn = document.getElementById('clear-chat-btn');
        
        this.messages = [];
        this.conversationState = 'normal';
        this.init();
    }

    init() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.clearChatBtn.addEventListener('click', () => this.clearConversation());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSubmit(e);
            }
        });
        this.messageInput.addEventListener('input', () => this.autoResize());
        this.autoResize();
    }

    autoResize() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async handleSubmit(e) {
        e.preventDefault();
        const message = this.messageInput.value.trim();
        if (!message || this.conversationState === 'ended') return;

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResize();
        this.showTyping();

        try {
            let endpoint = '/chat';
            let body = {
                message: message,
                messages: this.messages,
                state: this.conversationState
            };

            // If waiting for feedback, use feedback endpoint!
            if (this.conversationState === 'awaiting_feedback') {
                endpoint = '/feedback';
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await response.json();
            this.hideTyping();
            this.addMessage(data.message, 'bot');
            this.messages = data.messages || [];
            this.conversationState = data.state || 'normal';

            // If conversation ended, disable input
            if (this.conversationState === 'ended') {
                this.messageInput.disabled = true;
                this.sendBtn.disabled = true;
            }

        } catch (error) {
            this.hideTyping();
            this.addMessage('Network error. Please try again.', 'bot');
            console.error('Error:', error);
        }
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';

        let formattedContent = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n/g, '<br>');

        messageContent.innerHTML = formattedContent;
        messageDiv.appendChild(messageContent);

        if (sender === 'user') {
            const welcomeMsg = this.messagesContainer.querySelector('.welcome-message');
            if (welcomeMsg) welcomeMsg.remove();
        }
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    showTyping() {
        this.typingIndicator.classList.add('visible');
        this.sendBtn.disabled = true;
        this.scrollToBottom();
    }

    hideTyping() {
        this.typingIndicator.classList.remove('visible');
        this.sendBtn.disabled = false;
    }

    clearConversation() {
        this.messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="message bot-message">
                    <div class="message-content">
                        Welcome! I'm your AI shopping assistant. Tell me what laptop you're looking for and I'll help you find the perfect product.
                    </div>
                </div>
            </div>
        `;
        this.messages = [];
        this.conversationState = 'normal';
        this.messageInput.value = '';
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.autoResize();
        this.hideTyping();
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 50);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});