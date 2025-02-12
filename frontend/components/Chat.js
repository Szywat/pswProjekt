"use client";
import { useEffect, useState } from "react";
import { io } from "socket.io-client"

const socket = io("wss://127.0.0.1:5000");

export default function Chat() {
    const [messages, setMessages] = useState([]);
    const [message, setMessage] = useState("");
    const [login, setLogin] = useState("");

    useEffect(() => {
        setLogin(sessionStorage.getItem("login"))
        socket.on("message", (msg) => {
            setMessages((prev) => [...prev, msg]);
        });

        return () => {
            socket.off("message");
        };
    }, []);

    const sendMessage = (e) => {
        e.preventDefault();
        if (message.trim()) {
            socket.emit("message", message, login);
            setMessage("");
        }
    };

    return (
        <div id="chatbox">
            <ul id="messages">
                {messages.map((msg, i) => (
                    <li key={i}><b>{msg.login}</b>: {msg.text}</li>
                ))}
            </ul>
            <form id="form" onSubmit={sendMessage}>
                <input 
                    id="input" 
                    autoComplete="off" 
                    value={message} 
                    onChange={(e) => setMessage(e.target.value)} 
                />
                <button type="submit">Send</button>
            </form>
        </div>
       
    )
}