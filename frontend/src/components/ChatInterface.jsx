import { useState, useRef, useEffect } from 'react';
import { queryDocuments } from '../api/client';
import MessageBubble from './MessageBubble';

export default function ChatInterface() {
    const [messages, setMessages] = useState([
        {
            id: 'welcome',
            role: 'assistant',
            content:
                'Hello! I\'m your RAG assistant. Upload some documents using the sidebar, then ask me anything about them. 🚀',
        },
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const question = input.trim();
        if (!question || isLoading) return;

        // Add user message
        const userMsg = { id: Date.now(), role: 'user', content: question };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        // Add loading placeholder
        const loadingId = Date.now() + 1;
        setMessages((prev) => [
            ...prev,
            { id: loadingId, role: 'assistant', content: '', loading: true },
        ]);

        try {
            const result = await queryDocuments(question);
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === loadingId
                        ? {
                            ...m,
                            content: result.answer,
                            sources: result.sources,
                            loading: false,
                        }
                        : m
                )
            );
        } catch (err) {
            setMessages((prev) =>
                prev.map((m) =>
                    m.id === loadingId
                        ? {
                            ...m,
                            content: `Error: ${err.message}`,
                            loading: false,
                        }
                        : m
                )
            );
        } finally {
            setIsLoading(false);
            inputRef.current?.focus();
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2>💬 RAG Chat</h2>
                <span className="chat-subtitle">Ask questions about your documents</span>
            </div>

            <div className="chat-messages">
                {messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                ))}
                <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-form" onSubmit={handleSubmit}>
                <div className="input-wrapper">
                    <input
                        ref={inputRef}
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a question about your documents..."
                        disabled={isLoading}
                        className="chat-input"
                    />
                    <button
                        type="submit"
                        disabled={isLoading || !input.trim()}
                        className="send-btn"
                    >
                        {isLoading ? '⏳' : '🚀'}
                    </button>
                </div>
            </form>
        </div>
    );
}
