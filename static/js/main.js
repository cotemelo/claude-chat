document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');
    const clearHistoryButton = document.getElementById('clear-history');
    const typingContainer = document.querySelector('.typing-container');

    // Configure marked options
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        },
        breaks: true,
        gfm: true
    });

    function appendMessage(content, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-4 ${isUser ? 'text-right' : ''}`;
        
        const innerDiv = document.createElement('div');
        innerDiv.className = `inline-block max-w-[80%] ${
            isUser ? 'bg-purple-600 text-white' : 'bg-gray-100 text-gray-800'
        } rounded-lg px-4 py-2`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'prose max-w-none';
        
        // Parse markdown for assistant messages only
        if (!isUser) {
            contentDiv.innerHTML = marked.parse(content);
            // Initialize syntax highlighting for code blocks
            contentDiv.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
            });
        } else {
            contentDiv.textContent = content;
        }

        innerDiv.appendChild(contentDiv);
        messageDiv.appendChild(innerDiv);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function showTypingIndicator() {
        typingContainer.classList.remove('hidden');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function hideTypingIndicator() {
        typingContainer.classList.add('hidden');
    }

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Append user message
        appendMessage(message, true);
        userInput.value = '';

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (response.ok) {
                let assistantMessage = '';
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.slice(6));
                                if (data.content) {
                                    assistantMessage += data.content;
                                    // Update the message in real-time
                                    const existingMessage = chatContainer.lastElementChild;
                                    if (existingMessage && !existingMessage.classList.contains('text-right')) {
                                        const contentDiv = existingMessage.querySelector('.prose');
                                        contentDiv.innerHTML = marked.parse(assistantMessage);
                                        // Reinitialize syntax highlighting
                                        contentDiv.querySelectorAll('pre code').forEach((block) => {
                                            hljs.highlightBlock(block);
                                        });
                                    } else {
                                        appendMessage(assistantMessage);
                                    }
                                    chatContainer.scrollTop = chatContainer.scrollHeight;
                                }
                            } catch (e) {
                                console.error('Error parsing SSE data:', e);
                            }
                        }
                    }
                }
            } else {
                const error = await response.json();
                appendMessage(`Error: ${error.error}`, false);
            }
        } catch (error) {
            appendMessage(`Error: ${error.message}`, false);
        } finally {
            hideTypingIndicator();
        }
    });

    clearHistoryButton.addEventListener('click', async function() {
        const response = await fetch('/clear_history', {
            method: 'POST',
        });
        
        if (response.ok) {
            chatContainer.innerHTML = '';
        }
    });

    // Enable enter to submit, shift+enter for new line
    userInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
});