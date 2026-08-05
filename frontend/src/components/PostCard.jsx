import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiHeart, FiMessageCircle, FiRepeat, FiShare, FiBookmark, FiTrash2 } from 'react-icons/fi';
import RiskBadge from './RiskBadge';
import './PostCard.css';

function timeAgo(iso) {
  const diffMs = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return 'now';
  if (mins < 60) return `${mins}m`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h`;
  return `${Math.floor(hrs / 24)}d`;
}

export default function PostCard({ post, onDelete }) {
  const [liked, setLiked] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [likeCount, setLikeCount] = useState(() => Math.floor(Math.random() * 40));
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  const avatarUrl = `https://api.dicebear.com/7.x/thumbs/svg?seed=${encodeURIComponent(
    post.handle || post.username || String(post.id)
  )}`;

  const handleDeleteClick = () => {
    if (confirmingDelete) {
      onDelete(post.id);
    } else {
      setConfirmingDelete(true);
      setTimeout(() => setConfirmingDelete(false), 2500);
    }
  };

  return (
    <motion.article
      className="post-card glass-card glass-card--hover"
      layout
      initial={{ opacity: 0, y: -10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="post-card__row">
        <div className="post-card__avatar-ring">
          <img className="post-card__avatar" src={avatarUrl} alt="" />
        </div>

        <div className="post-card__main">
          <div className="post-card__meta">
            <span className="post-card__name">{post.username}</span>
            <span className="post-card__handle">{post.handle || `@${post.username}`}</span>
            <span className="post-card__dot">·</span>
            <span className="post-card__time">{timeAgo(post.createdAt)}</span>
            <span className="post-card__badge">
              <RiskBadge level={post.riskLevel} score={post.riskScore} />
            </span>
          </div>

          <p className="post-card__content">{post.content}</p>

          <div className="post-card__actions">
            <button className="post-card__action" title="Comment (UI only)">
              <FiMessageCircle size={16} />
              <span>Reply</span>
            </button>
            <button className="post-card__action" title="Repost (UI only)">
              <FiRepeat size={16} />
              <span>Repost</span>
            </button>
            <button
              className={`post-card__action ${liked ? 'post-card__action--liked' : ''}`}
              onClick={() => {
                setLiked((l) => !l);
                setLikeCount((c) => c + (liked ? -1 : 1));
              }}
              title="Like"
            >
              <FiHeart size={16} fill={liked ? 'currentColor' : 'none'} />
              <span>{likeCount > 0 ? likeCount : ''}</span>
            </button>
            <button className="post-card__action" title="Share (UI only)">
              <FiShare size={16} />
            </button>
            <button
              className={`post-card__action ${bookmarked ? 'post-card__action--saved' : ''}`}
              onClick={() => setBookmarked((b) => !b)}
              title="Bookmark"
            >
              <FiBookmark size={16} fill={bookmarked ? 'currentColor' : 'none'} />
            </button>
            <button
              className={`post-card__action post-card__action--danger ${
                confirmingDelete ? 'post-card__action--confirm' : ''
              }`}
              onClick={handleDeleteClick}
              title="Delete"
            >
              <FiTrash2 size={16} />
              {confirmingDelete && <span>Confirm</span>}
            </button>
          </div>
        </div>
      </div>
    </motion.article>
  );
}