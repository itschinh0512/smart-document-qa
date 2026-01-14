import React, { useEffect, useRef } from 'react';

const ChatInterface = ({ messages, input, setInput, sendMessage, loading }) => {
    const messagesEndRef = useRef(null);

    // Automatically scroll to the bottom of the chat when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    return (
        <div className="chat-container">
            {/* Messages List Area */}
            <div className="messages-list">
                {messages.length === 0 && (
                    <div className="empty-state">
                        <h3>Start a Conversation</h3>
                        <p>Upload a PDF and ask a question about its content.</p>
                    </div>
                )}

                {messages.map((m, i) => (
                    <div key={i} className={`message ${m.role}`}>
                        <div className="message-content">
                            {m.text}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="message bot">
                        <div className="typing-indicator">
                            <span></span><span></span><span></span>
                            AI is searching and generating...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="input-box">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Ask a question..."
                    disabled={loading}
                />
                <button
                    onClick={sendMessage}
                    disabled={loading || !input.trim()}
                >
                    {loading ? "..." : "Ask"}
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;