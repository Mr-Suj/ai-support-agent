/**
 * Main Application Logic
 * Handles user interactions and coordinates API/UI
 */

class ChatApp {
    constructor() {
        this.sessionId = null;
        this.userEmail = 'john@example.com';
        this.isProcessing = false;
    }

    /**
     * Initialize the application
     */
    async init() {
        console.log('🚀 Initializing AI Support Agent...');

        // Initialize UI
        UI.init();

        // Load or create session
        this.loadSession();

        // Setup event listeners
        this.setupEventListeners();

        // Load conversation history
        await this.loadConversationHistory();

        console.log('✅ Application ready!');
    }

    /**
     * Load or create session ID
     */
    loadSession() {
        this.sessionId = localStorage.getItem('sessionId');

        if (!this.sessionId) {
            this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            localStorage.setItem('sessionId', this.sessionId);
            console.log('Created new session:', this.sessionId);
        } else {
            console.log('Loaded existing session:', this.sessionId);
        }

        UI.updateSessionDisplay(this.sessionId);
    }

    /**
     * Setup event listeners with form submission control
     */
    setupEventListeners() {
        // Get form element
        const form = document.getElementById('chatForm');

        // Handle form submission (Enter key + Send button)
        form.addEventListener('submit', (e) => {
            e.preventDefault();   // 🔥 PREVENTS PAGE RELOAD
            e.stopPropagation();
            this.handleSendMessage();
        });

        // Handle Shift+Enter for new lines in textarea
        UI.elements.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.shiftKey) {
                // Allow newline
                return;
            }
        });

        // Auto-resize textarea
        UI.elements.messageInput.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = (e.target.scrollHeight) + 'px';
            UI.updateCharCount(e.target.value.length, 1000);
        });

        // New chat button - PREVENT DEFAULT
        UI.elements.newChatBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.handleNewChat();
        });

        // Suggestion chips - PREVENT DEFAULT
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const query = e.target.getAttribute('data-query');
                UI.elements.messageInput.value = query;
                this.handleSendMessage();
            });
        });

        console.log('✅ Event listeners attached (form-controlled)');
    }

    /**
     * Handle sending a message
     */
    async handleSendMessage() {
        const query = UI.elements.messageInput.value.trim();

        if (!query || this.isProcessing) {
            console.log('⚠️ Message empty or already processing');
            return;
        }

        console.log('📤 Sending message:', query);
        this.isProcessing = true;

        // Add user message to UI
        UI.addMessage('user', query);
        UI.clearInput();
        UI.disableInput();
        UI.showTyping();

        try {
            console.log('⏳ Waiting for API response...');
            
            // Send message to backend
            const response = await API.sendMessage(query, this.sessionId, this.userEmail);

            console.log('✅ Got API response');

            // Remove typing indicator
            UI.hideTyping();

            // Add assistant response
            UI.addMessage('assistant', response.response);

            console.log('Response metadata:', response.metadata);

        } catch (error) {
            console.error('❌ API Error:', error);
            UI.hideTyping();
            UI.showToast('Failed to send message. Please try again.', 'error');

            // Add error message to chat
            UI.addMessage('assistant', '❌ Sorry, I encountered an error. Please try again or start a new chat.');
        } finally {
            this.isProcessing = false;
            UI.enableInput();
            console.log('✅ Message handling complete');
        }
    }

    /**
     * Handle new chat
     */
    async handleNewChat() {
        const confirmed = confirm('Start a new conversation? Current chat will be saved.');

        if (!confirmed) return;

        console.log('🆕 Starting new chat');

        // Create new session
        this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        localStorage.setItem('sessionId', this.sessionId);

        // Clear UI
        UI.clearMessages();
        UI.updateSessionDisplay(this.sessionId);

        UI.showToast('New conversation started!', 'success');
        console.log('Started new session:', this.sessionId);
    }

    /**
     * Load conversation history from backend
     */
    async loadConversationHistory() {
        try {
            const history = await API.getConversationHistory(this.sessionId);

            if (history.messages && history.messages.length > 0) {
                console.log(`Loading ${history.messages.length} previous messages...`);

                history.messages.forEach(msg => {
                    const time = new Date(msg.created_at).toLocaleTimeString('en-US', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });

                    UI.addMessage(msg.role, msg.content, time);
                });

                UI.scrollToBottom();
            } else {
                console.log('No previous messages in this session.');
            }
        } catch (error) {
            console.error('Failed to load conversation history:', error);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new ChatApp();
    app.init();
});