/**
 * API Communication Module
 * Handles all backend API calls
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

const API = {
    /**
     * Send a chat message to the backend
     * @param {string} query - User's message
     * @param {string} sessionId - Current session ID
     * @param {string} userEmail - User's email
     * @returns {Promise<Object>} API response
     */
    async sendMessage(query, sessionId, userEmail = 'john@example.com') {
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    session_id: sessionId,
                    user_email: userEmail
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to send message');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Get conversation history
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Conversation history
     */
    async getConversationHistory(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/conversation/${sessionId}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    return { messages: [] };
                }
                throw new Error('Failed to fetch conversation history');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            return { messages: [] };
        }
    },

    /**
     * Delete a conversation
     * @param {string} sessionId - Session ID
     * @returns {Promise<Object>} Delete response
     */
    async deleteConversation(sessionId) {
        try {
            const response = await fetch(`${API_BASE_URL}/conversation/${sessionId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Failed to delete conversation');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * Health check
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            
            if (!response.ok) {
                throw new Error('Health check failed');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Health check error:', error);
            throw error;
        }
    }
};