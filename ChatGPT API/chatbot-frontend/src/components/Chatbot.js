import React, { useState } from 'react';
import './style.css'; // Import the updated CSS file

const Chatbot = () => {
    const [message, setMessage] = useState('');
    const [chatHistory, setChatHistory] = useState([]);

    const handleSendMessage = async () => {
        if (!message.trim()) return; // Prevent sending empty messages
        const userMessage = { sender: 'user', text: message };
        setChatHistory([...chatHistory, userMessage]);

        try {
            // Send message to Flask backend
            const response = await fetch('http://127.0.0.1:5000/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });

            const responseData = await response.json();
            const botMessage = { sender: 'bot', text: responseData.response };

            setChatHistory([...chatHistory, userMessage, botMessage]);
        } catch (error) {
            const botMessage = { sender: 'bot', text: 'Error: Could not reach the server.' };
            setChatHistory([...chatHistory, userMessage, botMessage]);
        }

        setMessage('');  // Clear input field
    };

    // Function to handle pressing "Enter" key
    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleSendMessage(); // Trigger the send message function when Enter is pressed
        }
    };

    return (
        <div className="container">
            <div className="chat-box" id="chatBox">
                {chatHistory.map((chat, index) => (
                    <div key={index} className={chat.sender === 'user' ? 'user-message' : 'bot-message'}>
                        <strong>{chat.sender === 'user' ? 'You' : 'Bot'}:</strong> {chat.text}
                    </div>
                ))}
            </div>
            <div className="input-group">
                <input
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyPress}  // Listen for key press (Enter key)
                    placeholder="Type your message here..."
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
};

export default Chatbot;
