const UI = {
    elements: {},
    hasMessages: false,

    init() {
        this.elements = {
            chatContainer: document.getElementById('chatContainer'),
            messages: document.getElementById('messages'),
            welcomeMessage: document.getElementById('welcomeMessage'),
            messageInput: document.getElementById('messageInput'),
            sendBtn: document.getElementById('sendBtn'),
            newChatBtn: document.getElementById('newChatBtn'),
            sessionDisplay: document.getElementById('sessionDisplay'),
            charCount: document.getElementById('charCount'),
            toastContainer: document.getElementById('toastContainer'),
            loadingOverlay: document.getElementById('loadingOverlay')
        }
        console.log('UI initialized')
    },

    hideWelcome() {
    if (this.elements.welcomeMessage) {
        console.log('Hiding welcome message')
        this.elements.welcomeMessage.classList.add('hidden')
        this.hasMessages = true
    }
},

showWelcome() {
    if (this.elements.welcomeMessage) {
        console.log('Showing welcome message')
        this.elements.welcomeMessage.classList.remove('hidden')
        this.hasMessages = false
    }
},

    addMessage(role, content, time = null) {
        console.log(`Adding ${role} message`)
        this.hideWelcome()

        const messageEl = document.createElement('div')
        messageEl.className = `message ${role}`
        messageEl.setAttribute('data-message', 'true')

        const timestamp = time || new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        })

        const formattedContent = role === 'assistant' 
            ? marked.parse(content) 
            : this.escapeHtml(content)

        messageEl.innerHTML = `
            <div class="message-avatar">
                ${role === 'user' 
                    ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                        <circle cx="12" cy="7" r="4"/>
                       </svg>`
                    : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                       </svg>`
                }
            </div>
            <div class="message-content">
                <div class="message-bubble">${formattedContent}</div>
                <div class="message-time">${timestamp}</div>
            </div>
        `

        this.elements.messages.appendChild(messageEl)
        this.scrollToBottom()
    },

    showTyping() {
        console.log('Showing typing indicator')
        this.hideWelcome()
        this.hasMessages = true
        
        // Remove existing typing indicator if any
        const existingTyping = document.getElementById('typingIndicator')
        if (existingTyping) {
            existingTyping.remove()
        }

        const typingEl = document.createElement('div')
        typingEl.className = 'typing-indicator'
        typingEl.id = 'typingIndicator'
        typingEl.setAttribute('data-typing', 'true')

        typingEl.innerHTML = `
            <div class="message-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
            </div>
            <div class="typing-bubble">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `

        this.elements.messages.appendChild(typingEl)
        this.scrollToBottom()
    },

    hideTyping() {
        const typingEl = document.getElementById('typingIndicator')
        if (typingEl) {
            console.log('Hiding typing indicator')
            typingEl.remove()
        }
    },

    clearMessages() {
        console.log('Clearing all messages')
        // Only remove actual messages, not typing indicators
        const messages = this.elements.messages.querySelectorAll('[data-message="true"]')
        messages.forEach(msg => msg.remove())
        
        // Remove typing indicator too
        this.hideTyping()
        
        // Reset flag and show welcome
        this.hasMessages = false
        this.showWelcome()
    },

    scrollToBottom() {
        setTimeout(() => {
            this.elements.chatContainer.scrollTop = this.elements.chatContainer.scrollHeight
        }, 50)
    },

    updateSessionDisplay(sessionId) {
        if (this.elements.sessionDisplay) {
            const shortId = sessionId.substring(sessionId.length - 8)
            this.elements.sessionDisplay.textContent = shortId
        }
    },

    updateCharCount(count, max) {
        if (this.elements.charCount) {
            this.elements.charCount.textContent = `${count} / ${max}`
            
            if (count > max * 0.9) {
                this.elements.charCount.style.color = 'var(--accent-red)'
            } else {
                this.elements.charCount.style.color = 'var(--text-muted)'
            }
        }
    },

    showToast(message, type = 'success') {
        const toast = document.createElement('div')
        toast.className = `toast ${type}`

        const icon = type === 'success'
            ? `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
               </svg>`
            : `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
               </svg>`

        toast.innerHTML = `${icon}<span>${message}</span>`

        this.elements.toastContainer.appendChild(toast)

        setTimeout(() => {
            toast.style.opacity = '0'
            toast.style.transform = 'translateX(20px)'
            setTimeout(() => toast.remove(), 300)
        }, 3000)
    },

    showLoading() {
        this.elements.loadingOverlay.classList.add('active')
    },

    hideLoading() {
        this.elements.loadingOverlay.classList.remove('active')
    },

    disableInput() {
        this.elements.messageInput.disabled = true
        this.elements.sendBtn.disabled = true
    },

    enableInput() {
        this.elements.messageInput.disabled = false
        this.elements.sendBtn.disabled = false
        this.elements.messageInput.focus()
    },

    clearInput() {
        this.elements.messageInput.value = ''
        this.elements.messageInput.style.height = 'auto'
        this.updateCharCount(0, 1000)
    },

    escapeHtml(text) {
        const div = document.createElement('div')
        div.textContent = text
        return div.innerHTML
    }
}