// ============================================
// App.js
// PURPOSE: Main component — root of our React app
// This is the parent component that holds everything
// It manages the main state of the application
// and passes data/functions down to child components
// ============================================

import React, { useState, useEffect } from 'react';
// useState → lets us store and update data inside a component
// useEffect → lets us run code when component loads or updates

import axios from 'axios';
// axios → library to make HTTP requests to our FastAPI backend

import PostInput from './components/PostInput';
// PostInput → our text area + publish button component

import WarningModal from './components/WarningModal';
// WarningModal → our warning popup + countdown timer component

import Feed from './components/Feed';
// Feed → our list of published posts component

import './App.css';
// App.css → our custom styles

// ── BACKEND URL ──────────────────────────────────────────────
// This is where our FastAPI backend is running
// All API calls will go to this address
const API_URL = 'http://127.0.0.1:8000';

function App() {

  // ── STATE VARIABLES ────────────────────────────────────────
  // useState stores data that can change over time
  // When state changes, React automatically re-renders the UI

  const [postText, setPostText] = useState('');
  // postText → stores what the user is typing in the text area
  // setPostText → function to update postText

  const [posts, setPosts] = useState([]);
  // posts → stores the list of all published posts for the feed
  // setPosts → function to update posts list

  const [warning, setWarning] = useState(null);
  // warning → stores the risk result when high risk is detected
  // null means no warning is showing
  // When it has data, the warning modal appears

  const [isLoading, setIsLoading] = useState(false);
  // isLoading → true while we are waiting for backend response
  // Used to show loading state on the publish button

  // ── LOAD FEED ON START ────────────────────────────────────
  // useEffect with empty [] runs ONCE when the app first loads
  // It fetches all existing posts from the database
  useEffect(() => {
    fetchFeed();
  }, []); // [] = run only once on mount

  // ── FETCH FEED FUNCTION ───────────────────────────────────
  // Calls GET /get-feed to load all posts from database
  const fetchFeed = async () => {
    try {
      const response = await axios.get(`${API_URL}/get-feed`);
      // response.data.posts = array of post objects from backend
      setPosts(response.data.posts);
    } catch (error) {
      console.error('Error fetching feed:', error);
    }
  };

  // ── HANDLE PUBLISH FUNCTION ───────────────────────────────
  // Called when user clicks the Publish button
  // Sends text to backend for PII scanning
  const handlePublish = async () => {

    // Don't do anything if text is empty
    if (!postText.trim()) return;

    setIsLoading(true); // show loading state

    try {
      // STEP 1: Send text to /scan-post for PII analysis
      const response = await axios.post(`${API_URL}/scan-post`, {
        text: postText
      });

      const result = response.data;
      // result contains: detected_entities, risk_score, risk_level, recommendation

      if (result.risk_level === 'HIGH') {
        // HIGH RISK → show warning modal with countdown
        // Store the full result in warning state
        // This triggers WarningModal to appear
        setWarning(result);

      } else {
        // LOW or MEDIUM → save post directly without warning
        await savePost(result.risk_level, result.risk_score);
      }

    } catch (error) {
      console.error('Error scanning post:', error);
    }

    setIsLoading(false); // hide loading state
  };

  // ── SAVE POST FUNCTION ────────────────────────────────────
  // Called after user confirms they want to publish
  // Sends post to /save-post to store in database
  const savePost = async (riskLevel, riskScore) => {
    try {
      await axios.post(`${API_URL}/save-post`, {
        content: postText,
        risk_level: riskLevel,
        risk_score: riskScore
      });

      // Clear the text area after successful post
      setPostText('');

      // Close warning modal if it was open
      setWarning(null);

      // Refresh the feed to show the new post
      fetchFeed();

    } catch (error) {
      console.error('Error saving post:', error);
    }
  };

  // ── HANDLE CANCEL FUNCTION ────────────────────────────────
  // Called when user clicks Cancel and Edit in warning modal
  // Just closes the modal — text stays in composer for editing
  const handleCancel = () => {
    setWarning(null); // close warning modal
  };

  // ── RENDER ────────────────────────────────────────────────
  // This is what gets displayed on screen
  // JSX = HTML-like syntax inside JavaScript
  return (
    <div className="app-container">

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="logo">
          <div className="logo-icon">🛡️</div>
          <div>
            <div className="logo-text">PrivGuard</div>
            <div className="logo-sub">Smart Microblog</div>
          </div>
        </div>
        <span className="nav-badge">✓ Privacy Protected</span>
      </nav>

      {/* MAIN CONTENT */}
      <div className="main-content">

        {/* POST COMPOSER */}
        <PostInput
          postText={postText}
          setPostText={setPostText}
          onPublish={handlePublish}
          isLoading={isLoading}
        />

        {/* WARNING MODAL — only shows when warning state has data */}
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
    </div>
  );
}

export default App;