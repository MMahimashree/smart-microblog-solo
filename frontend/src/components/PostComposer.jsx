import { useEffect, useRef, useState } from 'react';
import { FiSmile, FiImage } from 'react-icons/fi';
import RiskMeter from './RiskMeter';
import WarningModal from './WarningModal';
import useDebounce from '../hooks/useDebounce';
import { scanPost, savePost } from '../api/client';
import './PostComposer.css';

const MAX_LEN = 500;
const EMOJIS = ['😀', '😂', '🔥', '🎉', '💡', '👍', '❤️', '😮'];

export default function PostComposer({ onPosted, onToast }) {
  const [content, setContent] = useState('');
  const [scanning, setScanning] = useState(false);
  const [liveResult, setLiveResult] = useState(null);
  const [showEmoji, setShowEmoji] = useState(false);
  const [posting, setPosting] = useState(false);
  const [pendingReview, setPendingReview] = useState(null);
  const debouncedContent = useDebounce(content, 600);
  const requestId = useRef(0);

  useEffect(() => {
    const text = debouncedContent.trim();
    if (text.length < 3) {
      setLiveResult(null);
      return;
    }
    const currentRequest = ++requestId.current;
    setScanning(true);
    scanPost(text)
      .then((result) => {
        if (currentRequest === requestId.current) setLiveResult(result);
      })
      .catch(() => {})
      .finally(() => {
        if (currentRequest === requestId.current) setScanning(false);
      });
  }, [debouncedContent]);

  const remaining = MAX_LEN - content.length;
  const canPost = content.trim().length > 0 && remaining >= 0 && !posting;

  const insertEmoji = (emoji) => {
    setContent((c) => (c + emoji).slice(0, MAX_LEN));
    setShowEmoji(false);
  };

  const finalizePost = async (scan, text) => {
    const saved = await savePost({ content: text, scan });
    onPosted(saved);
    setContent('');
    setLiveResult(null);
    onToast('Posted');
  };

  const handlePost = async () => {
    const text = content.trim();
    if (!text) return;
    setPosting(true);
    try {
      const scan = await scanPost(text);
      if (scan.riskLevel === 'LOW') {
        await finalizePost(scan, text);
      } else {
        setPendingReview({ scan, text });
      }
    } catch (err) {
      onToast('Could not reach the backend. Is it running?');
    } finally {
      setPosting(false);
    }
  };

  const handleConfirmFromModal = async () => {
    if (!pendingReview) return;
    try {
      await finalizePost(pendingReview.scan, pendingReview.text);
    } catch {
      onToast('Could not save the post.');
    } finally {
      setPendingReview(null);
    }
  };

  return (
    <div className="composer">
      <div className="composer__row">
        <div className="composer__avatar" />
        <div className="composer__main">
          <textarea
            placeholder="What's happening? (Privacy Guard is watching)"
            value={content}
            maxLength={MAX_LEN + 40}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
          />

          <div className="composer__meter-wrap">
            <RiskMeter scanning={scanning} result={liveResult} idle={!liveResult && !scanning} />
          </div>

          <div className="composer__toolbar">
            <div className="composer__icons" style={{ position: 'relative' }}>
              <button className="composer__icon-btn" onClick={() => setShowEmoji((s) => !s)} title="Emoji">
                <FiSmile size={19} />
              </button>
              <button className="composer__icon-btn" disabled title="Image upload (UI only)">
                <FiImage size={19} />
              </button>
              {showEmoji && (
                <div className="composer__emoji-pop">
                  {EMOJIS.map((e) => (
                    <button key={e} onClick={() => insertEmoji(e)}>
                      {e}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="composer__right">
              <span
                className={
                  remaining < 0
                    ? 'composer__counter composer__counter--over'
                    : remaining < 40
                    ? 'composer__counter composer__counter--warn'
                    : 'composer__counter'
                }
              >
                {remaining}
              </span>
              <button className="composer__post-btn" disabled={!canPost} onClick={handlePost}>
                {posting ? 'Checking…' : 'Post'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {pendingReview && (
        <WarningModal
          level={pendingReview.scan.riskLevel}
          scan={pendingReview.scan}
          onCancel={() => setPendingReview(null)}
          onConfirm={handleConfirmFromModal}
        />
      )}
    </div>
  );
}