import { useCallback, useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import PostComposer from '../components/PostComposer';
import Feed from '../components/Feed';
import ProfileCard from '../components/ProfileCard';
import StatsPanel from '../components/StatsPanel';
import SearchBar from '../components/SearchBar';
import { getFeed, deletePost, getStats } from '../api/client';

export default function Home() {
  const { showToast } = useOutletContext();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [stats, setStats] = useState({ total: 0, low: 0, medium: 0, high: 0 });
  const [searchTerm, setSearchTerm] = useState('');

  const loadFeed = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getFeed();
      setPosts(data.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)));
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      setStats(await getStats());
    } catch {
      /* stats are supplementary */
    }
  }, []);

  useEffect(() => {
    loadFeed();
    loadStats();
  }, [loadFeed, loadStats]);

  const handlePosted = (newPost) => {
    setPosts((prev) => [newPost, ...prev]);
    loadStats();
  };

  const handleDelete = async (id) => {
    const prev = posts;
    setPosts((p) => p.filter((post) => post.id !== id));
    try {
      await deletePost(id);
      loadStats();
    } catch {
      setPosts(prev);
      showToast('Could not delete post');
    }
  };

  return (
    <>
      <main className="main-col">
        <div className="page-header">
          <h1>Home</h1>
          <p>Every post is checked before it goes live</p>
        </div>
        <div className="page-body">
          <PostComposer onPosted={handlePosted} onToast={showToast} />
          <Feed posts={posts} loading={loading} error={error} searchTerm={searchTerm} onDelete={handleDelete} />
        </div>
      </main>

      <aside className="right-panel">
        <SearchBar value={searchTerm} onChange={setSearchTerm} />
        <ProfileCard postsCount={stats.total} />
        <StatsPanel stats={stats} />
      </aside>
    </>
  );
}
