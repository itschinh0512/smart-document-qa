import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './Components/Sidebar';
import FileUpload from './Components/FileUpload';
import ChatInterface from './Components/ChatInterface';
import './App.css';

const BASE_URL = "https://polaris0512-smart-document-ask.hf.space";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [stats, setStats] = useState({});
  const [health, setHealth] = useState("Checking...");
  const [topK, setTopK] = useState(3);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    refreshSystemData();
  }, []);

  const refreshSystemData = async () => {
    try {
      const [healthRes, statsRes] = await Promise.all([
        axios.get(`${BASE_URL}/ping`),
        axios.get(`${BASE_URL}/stats`)
      ]);
      setHealth("Online");
      setStats(statsRes.data);
    } catch {
      setHealth("Offline");
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', text: input };
    setMessages([...messages, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(`${BASE_URL}/ai-ask`, {
        question: input,
        top_k: topK
      });
      setMessages(prev => [...prev, { role: 'bot', text: res.data.answer }]);
    } catch {
      setMessages(prev => [...prev, { role: 'bot', text: "Model error." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-layout">
      <Sidebar health={health} stats={stats} topK={topK} setTopK={setTopK} />

      <div className="main-content">
        <FileUpload baseUrl={BASE_URL} onUploadSuccess={refreshSystemData} />

        <ChatInterface
          messages={messages}
          input={input}
          setInput={setInput}
          sendMessage={sendMessage}
          loading={loading}
        />
      </div>
    </div>
  );
}

export default App;