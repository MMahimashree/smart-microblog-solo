import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PostInput from './components/PostInput';
import WarningModal from './components/WarningModal';
import Feed from './components/Feed';
import Sidebar from './components/Sidebar';
import RightPanel from './components/RightPanel';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [postText, setPostText] = useState('');
  const [posts, setPosts] = useState([]);
  const [warning, setWarning] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    try {
      const response = await axios.get(`${API_URL}/get-feed`);
      setPosts(response.data.posts);
    } catch (error) {
      console.error('Error fetching feed:', error);
    }
  };

  const handlePublish = async () => {
    if (!postText.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.post(`${API_URL}/scan-post`, {
        text: postText
      });
      const result = response.data;
      if (result.risk_level === 'HIGH') {
        setWarning(result);
      } else {
        await savePost(result.risk_level, result.risk_score);
      }
    } catch (error) {
      console.error('Error scanning post:', error);
    }
    setIsLoading(false);
  };

  const savePost = async (riskLevel, riskScore) => {
    try {
      await axios.post(`${API_URL}/save-post`, {
        content: postText,
        risk_level: riskLevel,
        risk_score: riskScore
      });
      setPostText('');
      setWarning(null);
      fetchFeed();
    } catch (error) {
      console.error('Error saving post:', error);
    }
  };

  const handleCancel = () => {
    setWarning(null);
  };

  return (
    <div className={`app-wrapper ${isDark ? 'dark' : 'light'}`}>

      {/* LEFT SIDEBAR */}
      <Sidebar />

      {/* MAIN FEED */}
      <div className="main-content">

        {/* TOP BAR */}
        <div className="top-bar">
          <span className="top-title">Home</span>
          <button
            className="theme-toggle"
            onClick={() => setIsDark(!isDark)}
          >
            {isDark ? '☀️ Light mode' : '🌙 Dark mode'}
          </button>
        </div>

        {/* POST COMPOSER */}
        <PostInput
          postText={postText}
          setPostText={setPostText}
          onPublish={handlePublish}
          isLoading={isLoading}
        />

        {/* WARNING — shows inline when HIGH risk */}
        {warning && (
          <WarningModal
            warning={warning}
            onConfirm={() => savePost(warning.risk_level, warning.risk_score)}
            onCancel={handleCancel}
          />
        )}

        {/* FEED */}
        <Feed posts={posts} />

      </div>

      {/* RIGHT PANEL */}
      <RightPanel posts={posts} />

    </div>
  );
}

export default App;