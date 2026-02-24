export default function MessageBubble({ message }) {
    const isUser = message.role === 'user';

    return (
        <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
            <div className="message-avatar">
                {isUser ? '👤' : '🤖'}
            </div>
            <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
                <div className="message-text">{message.content}</div>

                {!isUser && message.sources && message.sources.length > 0 && (
                    <div className="message-sources">
                        <div className="sources-label">📎 Sources:</div>
                        {message.sources.map((source, idx) => (
                            <div key={idx} className="source-chip">
                                <span className="source-name">{source.filename}</span>
                                <span className="source-score">
                                    {Math.round(source.score * 100)}% match
                                </span>
                            </div>
                        ))}
                    </div>
                )}

                {!isUser && message.loading && (
                    <div className="typing-indicator">
                        <span></span><span></span><span></span>
                    </div>
                )}
            </div>
        </div>
    );
}
