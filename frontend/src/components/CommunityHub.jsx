import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { communityAPI, api } from '../services/api';
import { Users, Building2, TrendingUp, MapPin, Megaphone, BarChart3, MessageCircle, Heart, Share2, Send, Image, X, ChevronDown, ChevronUp } from 'lucide-react';

const glass = { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: '1.25rem', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)' };

const postsAPI = {
  getAll: (params) => api.get('/posts', { params }),
  create: (data) => api.post('/posts', data),
  delete: (id) => api.delete(`/posts/${id}`),
  toggleLike: (id) => api.post(`/posts/${id}/like`),
  getComments: (id) => api.get(`/posts/${id}/comments`),
  createComment: (id, data) => api.post(`/posts/${id}/comments`, data),
  deleteComment: (postId, commentId) => api.delete(`/posts/${postId}/comments/${commentId}`),
  toggleCommentLike: (postId, commentId) => api.post(`/posts/${postId}/comments/${commentId}/like`),
};

const CommunityHub = () => {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [overview, setOverview] = useState(null);
  const [districtStats, setDistrictStats] = useState(null);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('posts');

  const [posts, setPosts] = useState([]);
  const [postsLoading, setPostsLoading] = useState(false);
  const [newPostContent, setNewPostContent] = useState('');
  const [newPostTitle, setNewPostTitle] = useState('');
  const [newPostCategory, setNewPostCategory] = useState('general');
  const [expandedComments, setExpandedComments] = useState({});
  const [commentInputs, setCommentInputs] = useState({});
  const [replyInputs, setReplyInputs] = useState({});

  useEffect(() => { fetchData(); }, []);
  useEffect(() => { if (activeTab === 'posts') fetchPosts(); }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [hierarchyResp, districtResp, announcementsResp] = await Promise.all([
        communityAPI.getHierarchy().catch(() => ({ data: null })),
        isAdmin ? communityAPI.getDistrictOverview(user?.district || 'Hyderabad').catch(() => ({ data: null })) : Promise.resolve({ data: null }),
        communityAPI.getAnnouncements().catch(() => ({ data: [] })),
      ]);
      setOverview(hierarchyResp.data);
      setDistrictStats(districtResp?.data);
      setAnnouncements(announcementsResp.data);
    } catch { console.error('Failed to fetch community data'); }
    finally { setLoading(false); }
  };

  const fetchPosts = async () => {
    try {
      setPostsLoading(true);
      const response = await postsAPI.getAll({ limit: 50 });
      setPosts(response.data.items || []);
    } catch (error) {
      console.error('Failed to fetch posts:', error);
    } finally {
      setPostsLoading(false);
    }
  };

  const handleCreatePost = async () => {
    if (!newPostContent.trim()) return;
    try {
      await postsAPI.create({
        title: newPostTitle || undefined,
        content: newPostContent,
        category: newPostCategory,
        post_type: 'general'
      });
      setNewPostContent('');
      setNewPostTitle('');
      fetchPosts();
    } catch (error) {
      alert('Failed to create post: ' + (error.response?.data?.detail || 'Unknown error'));
    }
  };

  const handleDeletePost = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;
    try {
      await postsAPI.delete(postId);
      fetchPosts();
    } catch (error) {
      alert('Failed to delete post');
    }
  };

  const handleToggleLike = async (postId) => {
    try {
      const response = await postsAPI.toggleLike(postId);
      setPosts(posts.map(p => p.id === postId ? { 
        ...p, 
        is_liked: response.data.liked, 
        likes_count: response.data.likes_count 
      } : p));
    } catch (error) {
      console.error('Failed to toggle like:', error);
    }
  };

  const toggleComments = async (postId) => {
    if (expandedComments[postId]) {
      setExpandedComments({ ...expandedComments, [postId]: null });
    } else {
      try {
        const response = await postsAPI.getComments(postId);
        setExpandedComments({ ...expandedComments, [postId]: response.data });
      } catch (error) {
        console.error('Failed to fetch comments:', error);
      }
    }
  };

  const handleAddComment = async (postId, parent_id = null) => {
    const inputKey = parent_id ? `reply-${parent_id}` : `comment-${postId}`;
    const content = parent_id ? replyInputs[inputKey] : commentInputs[postId];
    if (!content?.trim()) return;

    try {
      await postsAPI.createComment(postId, { content, parent_id });
      if (parent_id) {
        setReplyInputs({ ...replyInputs, [inputKey]: '' });
      } else {
        setCommentInputs({ ...commentInputs, [postId]: '' });
      }
      const response = await postsAPI.getComments(postId);
      setExpandedComments({ ...expandedComments, [postId]: response.data });
      setPosts(posts.map(p => p.id === postId ? { ...p, comments_count: (p.comments_count || 0) + 1 } : p));
    } catch (error) {
      alert('Failed to add comment');
    }
  };

  const handleToggleCommentLike = async (postId, commentId) => {
    try {
      await postsAPI.toggleCommentLike(postId, commentId);
      const response = await postsAPI.getComments(postId);
      setExpandedComments({ ...expandedComments, [postId]: response.data });
    } catch (error) {
      console.error('Failed to toggle comment like:', error);
    }
  };

  const handleDeleteComment = async (postId, commentId) => {
    if (!window.confirm('Delete this comment?')) return;
    try {
      await postsAPI.deleteComment(postId, commentId);
      const response = await postsAPI.getComments(postId);
      setExpandedComments({ ...expandedComments, [postId]: response.data });
      setPosts(posts.map(p => p.id === postId ? { ...p, comments_count: Math.max(0, (p.comments_count || 1) - 1) } : p));
    } catch (error) {
      alert('Failed to delete comment');
    }
  };

  const formatTimeAgo = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    if (diff < 60) return 'just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  const CommentItem = ({ comment, postId }) => {
    const [showReplyInput, setShowReplyInput] = useState(false);
    const replyKey = `reply-${comment.id}`;

    return (
      <div style={{ marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <div style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg, #8b5cf6, #a855f7)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: '0.7rem', fontWeight: 700, color: '#fff' }}>
            {comment.author_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: '0.5rem 0.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.8rem' }}>{comment.author_name}</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{formatTimeAgo(comment.created_at)}</span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', margin: 0 }}>{comment.content}</p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', marginTop: 4, marginLeft: 8 }}>
              <button onClick={() => handleToggleCommentLike(postId, comment.id)} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', color: comment.is_liked ? '#f87171' : 'var(--text-muted)', fontSize: '0.7rem', cursor: 'pointer', padding: 0 }}>
                <Heart size={12} fill={comment.is_liked ? '#f87171' : 'none'} /> {comment.likes_count || 0}
              </button>
              <button onClick={() => setShowReplyInput(!showReplyInput)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '0.7rem', cursor: 'pointer', padding: 0 }}>
                Reply
              </button>
              {comment.author_id === user?.id && (
                <button onClick={() => handleDeleteComment(postId, comment.id)} style={{ background: 'none', border: 'none', color: '#f87171', fontSize: '0.7rem', cursor: 'pointer', padding: 0 }}>
                  Delete
                </button>
              )}
            </div>
            {showReplyInput && (
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                <input
                  type="text"
                  value={replyInputs[replyKey] || ''}
                  onChange={(e) => setReplyInputs({ ...replyInputs, [replyKey]: e.target.value })}
                  placeholder="Write a reply..."
                  style={{ flex: 1, padding: '0.4rem 0.6rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.8rem' }}
                />
                <button onClick={() => handleAddComment(postId, comment.id)} style={{ padding: '0.4rem 0.6rem', background: '#8b5cf6', border: 'none', borderRadius: 8, color: '#fff', cursor: 'pointer' }}>
                  <Send size={14} />
                </button>
              </div>
            )}
            {comment.replies && comment.replies.length > 0 && (
              <div style={{ marginLeft: '1.5rem', marginTop: '0.5rem', borderLeft: '2px solid rgba(139,92,246,0.2)', paddingLeft: '0.5rem' }}>
                {comment.replies.map(reply => <CommentItem key={reply.id} comment={reply} postId={postId} />)}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const sendAlert = async () => {
    const title = prompt('Enter alert title:');
    const message = prompt('Enter alert message:');
    const targetLevel = prompt('Target level (All, SHG, SLF, TLF):');
    if (!title || !message) return;
    try { await communityAPI.sendAlert(title, message, targetLevel, user?.district); alert('Alert sent!'); fetchData(); }
    catch (error) { alert('Failed: ' + (error.response?.data?.detail || 'Unknown error')); }
  };

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
      <div style={{ width: 36, height: 36, borderRadius: '50%', border: '3px solid rgba(139,92,246,0.2)', borderTopColor: '#8b5cf6', margin: '0 auto 12px', animation: 'spin 0.7s linear infinite' }} />
      Loading community hub...
    </div>
  );

  const TABS = [['posts','Community Posts'],['hierarchy','Hierarchy'],['announcements','Announcements'],...(isAdmin?[['admin','Admin Actions']]:[])] ;
  const statCards = [
    { icon: Users,      color: '#8b5cf6', value: districtStats?.total_shgs||0,  label:'Total SHGs' },
    { icon: TrendingUp, color: '#10b981', value: districtStats?.active_shgs||0, label:'Active SHGs' },
    { icon: Building2,  color: '#a855f7', value: districtStats?.total_products||0, label:'Products' },
    { icon: MapPin,     color: '#f59e0b', value: districtStats?.avg_trust_score?.toFixed(1)||0, label:'Avg Trust' },
  ];

  return (
    <div className="animate-fade-in" style={{ padding:'1.5rem', maxWidth:1100, margin:'0 auto', paddingBottom:'6rem' }}>
      <div style={{ marginBottom:'1.75rem' }}>
        <h1 style={{ fontSize:'1.75rem', fontWeight:900, margin:'0 0 4px', background:'linear-gradient(135deg,#f8fafc 0%,#c4b5fd 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent', backgroundClip:'text' }}>Agent Sampark</h1>
        <p style={{ color:'var(--text-muted)', fontSize:'0.875rem', margin:0 }}>Community Orchestration & Federation</p>
      </div>

      {/* Stats */}
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(150px,1fr))', gap:'0.9rem', marginBottom:'1.5rem' }}>
        {statCards.map(({ icon:Icon, color, value, label }) => (
          <div key={label} style={{ ...glass, padding:'1.1rem', textAlign:'center' }}>
            <Icon size={26} style={{ color, margin:'0 auto 8px' }} />
            <p style={{ fontWeight:900, fontSize:'1.6rem', color:'var(--text-primary)', margin:'0 0 3px' }}>{value}</p>
            <p style={{ fontSize:'0.72rem', color:'var(--text-muted)', margin:0 }}>{label}</p>
          </div>
        ))}
      </div>

      {/* Federation + District */}
      {overview && (
        <div style={{ display:'grid', gridTemplateColumns:(isAdmin&&districtStats)?'1fr 1fr':'1fr', gap:'1rem', marginBottom:'1.5rem' }}>
          <div style={{ ...glass, padding:'1.25rem' }}>
            <h3 style={{ fontWeight:800, color:'var(--text-primary)', fontSize:'1rem', marginBottom:'0.9rem', display:'flex', alignItems:'center', gap:8 }}>
              <Building2 size={18} style={{ color:'#a78bfa' }} /> Your Federation
            </h3>
            {[['Level', user?.hierarchy_level||'SHG'],['Parent Federation',overview.upstream?.length>0?overview.upstream[0].name:'None'],['Peer SHGs',overview.peers?.length||0]].map(([k,v])=>(
              <div key={k} style={{ display:'flex', justifyContent:'space-between', fontSize:'0.875rem', borderBottom:'1px solid rgba(255,255,255,0.04)', padding:'6px 0' }}>
                <span style={{ color:'var(--text-muted)' }}>{k}</span>
                <span style={{ fontWeight:600, color:'var(--text-secondary)' }}>{v}</span>
              </div>
            ))}
          </div>
          {isAdmin && districtStats && (
            <div style={{ ...glass, padding:'1.25rem' }}>
              <h3 style={{ fontWeight:800, color:'var(--text-primary)', fontSize:'1rem', marginBottom:'0.9rem', display:'flex', alignItems:'center', gap:8 }}>
                <MapPin size={18} style={{ color:'#10b981' }} /> {districtStats.district} Overview
              </h3>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.6rem' }}>
                {[['Total SHGs',districtStats.total_shgs,'#8b5cf6'],['Active SHGs',districtStats.active_shgs,'#10b981'],['Products',districtStats.total_products,'#a855f7'],['Revenue',`₹${districtStats.total_revenue?.toLocaleString()}`,'#6ee7b7']].map(([l,v,c])=>(
                  <div key={l} style={{ background:`${c}10`, border:`1px solid ${c}25`, borderRadius:10, padding:'0.65rem' }}>
                    <p style={{ fontWeight:900, color:c, fontSize:'1.1rem', margin:'0 0 2px' }}>{v}</p>
                    <p style={{ fontSize:'0.7rem', color:'var(--text-muted)', margin:0 }}>{l}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tabs */}
      <div style={{ ...glass, overflow:'hidden' }}>
        <div style={{ display:'flex', borderBottom:'1px solid rgba(139,92,246,0.15)' }}>
          {TABS.map(([id,label])=>(
            <button key={id} onClick={()=>setActiveTab(id)} style={{ flex:1, padding:'0.9rem', fontSize:'0.875rem', fontWeight:600, cursor:'pointer', border:'none', background:'transparent', color:activeTab===id?'#c4b5fd':'var(--text-muted)', borderBottom:activeTab===id?'2px solid #8b5cf6':'2px solid transparent', transition:'all 0.2s' }}>
              {label}
            </button>
          ))}
        </div>
        <div style={{ padding:'1.25rem' }}>
          {activeTab === 'posts' && (
            <div>
              {/* Create Post */}
              <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 12, padding: '1rem', marginBottom: '1rem' }}>
                <input
                  type="text"
                  value={newPostTitle}
                  onChange={(e) => setNewPostTitle(e.target.value)}
                  placeholder="Post title (optional)"
                  style={{ width: '100%', padding: '0.5rem 0.75rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem', marginBottom: '0.5rem' }}
                />
                <textarea
                  value={newPostContent}
                  onChange={(e) => setNewPostContent(e.target.value)}
                  placeholder="What's on your mind?"
                  rows={3}
                  style={{ width: '100%', padding: '0.5rem 0.75rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.9rem', resize: 'none', marginBottom: '0.5rem' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <select
                    value={newPostCategory}
                    onChange={(e) => setNewPostCategory(e.target.value)}
                    style={{ padding: '0.4rem 0.6rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.8rem' }}
                  >
                    <option value="general">General</option>
                    <option value="discussion">Discussion</option>
                    <option value="question">Question</option>
                    <option value="announcement">Announcement</option>
                    <option value="showcase">Showcase</option>
                  </select>
                  <button
                    onClick={handleCreatePost}
                    disabled={!newPostContent.trim()}
                    style={{ padding: '0.5rem 1.25rem', background: newPostContent.trim() ? 'linear-gradient(135deg, #7c3aed, #a855f7)' : 'rgba(139,92,246,0.3)', border: 'none', borderRadius: 8, color: '#fff', fontWeight: 700, cursor: newPostContent.trim() ? 'pointer' : 'not-allowed' }}
                  >
                    Post
                  </button>
                </div>
              </div>

              {/* Posts List */}
              {postsLoading ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>Loading posts...</div>
              ) : posts.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                  <MessageCircle size={48} style={{ margin: '0 auto 0.75rem', opacity: 0.3 }} />
                  <p>No posts yet. Be the first to share!</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {posts.map((post) => (
                    <div key={post.id} style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(139,92,246,0.15)', borderRadius: 12, padding: '1rem' }}>
                      {/* Post Header */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                        <div style={{ display: 'flex', gap: '0.75rem' }}>
                          <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'linear-gradient(135deg, #8b5cf6, #a855f7)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, color: '#fff' }}>
                            {post.author_name?.charAt(0)?.toUpperCase() || 'U'}
                          </div>
                          <div>
                            <p style={{ fontWeight: 700, color: 'var(--text-primary)', margin: 0, fontSize: '0.9rem' }}>{post.author_name}</p>
                            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>{formatTimeAgo(post.created_at)} • {post.category || 'General'}</p>
                          </div>
                        </div>
                        {post.author_id === user?.id && (
                          <button onClick={() => handleDeletePost(post.id)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 4 }}>
                            <X size={16} />
                          </button>
                        )}
                      </div>

                      {/* Post Content */}
                      {post.title && <h4 style={{ fontWeight: 700, color: 'var(--text-primary)', margin: '0 0 0.5rem', fontSize: '1rem' }}>{post.title}</h4>}
                      <p style={{ color: 'var(--text-secondary)', margin: '0 0 0.75rem', fontSize: '0.9rem', lineHeight: 1.5 }}>{post.content}</p>

                      {/* Engagement */}
                      <div style={{ display: 'flex', gap: '1rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                        <button onClick={() => handleToggleLike(post.id)} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', color: post.is_liked ? '#f87171' : 'var(--text-muted)', cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem' }}>
                          <Heart size={18} fill={post.is_liked ? '#f87171' : 'none'} /> {post.likes_count || 0}
                        </button>
                        <button onClick={() => toggleComments(post.id)} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontWeight: 600, fontSize: '0.85rem' }}>
                          <MessageCircle size={18} /> {post.comments_count || 0}
                        </button>
                      </div>

                      {/* Comments Section */}
                      {expandedComments[postId = post.id] && (
                        <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                          {/* Add Comment Input */}
                          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                            <input
                              type="text"
                              value={commentInputs[post.id] || ''}
                              onChange={(e) => setCommentInputs({ ...commentInputs, [post.id]: e.target.value })}
                              placeholder="Write a comment..."
                              style={{ flex: 1, padding: '0.5rem 0.75rem', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 8, color: 'var(--text-primary)', fontSize: '0.85rem' }}
                            />
                            <button onClick={() => handleAddComment(post.id)} style={{ padding: '0.5rem 0.75rem', background: '#8b5cf6', border: 'none', borderRadius: 8, color: '#fff', cursor: 'pointer' }}>
                              <Send size={16} />
                            </button>
                          </div>

                          {/* Comments List */}
                          {expandedComments[post.id].length > 0 ? (
                            expandedComments[post.id].map(comment => (
                              <CommentItem key={comment.id} comment={comment} postId={post.id} />
                            ))
                          ) : (
                            <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>No comments yet</p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {activeTab==='hierarchy' && overview && (
            <div>
              <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem' }}>Federation Structure</h3>
              {overview.upstream?.length>0 && (
                <div style={{ marginBottom:'1rem' }}>
                  <p style={{ fontSize:'0.78rem', fontWeight:600, color:'var(--text-muted)', marginBottom:8 }}>Parent Federation</p>
                  <div style={{ background:'rgba(59,130,246,0.08)', border:'1px solid rgba(59,130,246,0.2)', borderRadius:10, padding:'0.75rem' }}>
                    <p style={{ fontWeight:700, color:'#93c5fd', margin:'0 0 3px' }}>{overview.upstream[0].name}</p>
                    <p style={{ fontSize:'0.78rem', color:'var(--text-muted)', margin:0 }}>{overview.upstream[0].level} • {overview.upstream[0].district}</p>
                  </div>
                </div>
              )}
              {overview.downstream?.length>0 && (
                <div style={{ marginBottom:'0.9rem' }}>
                  <p style={{ fontSize:'0.78rem', fontWeight:600, color:'var(--text-muted)', marginBottom:8 }}>Child SHGs ({overview.downstream.length})</p>
                  <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(170px,1fr))', gap:8 }}>
                    {overview.downstream.map(m=>(
                      <div key={m.id} style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(139,92,246,0.15)', borderRadius:10, padding:'0.65rem' }}>
                        <p style={{ fontWeight:600, color:'var(--text-primary)', margin:'0 0 3px', fontSize:'0.875rem' }}>{m.name}</p>
                        <p style={{ fontSize:'0.75rem', color:'var(--text-muted)', margin:'0 0 5px' }}>{m.district}</p>
                        <span style={{ fontSize:'0.75rem', fontWeight:700, color:'#a78bfa' }}>★ {m.trust_score}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              {overview.peers?.length>0 && (
                <div>
                  <p style={{ fontSize:'0.78rem', fontWeight:600, color:'var(--text-muted)', marginBottom:8 }}>Peer SHGs ({overview.peers.length})</p>
                  <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
                    {overview.peers.map(p=><span key={p.id} style={{ padding:'3px 10px', background:'rgba(139,92,246,0.12)', border:'1px solid rgba(139,92,246,0.25)', borderRadius:99, fontSize:'0.72rem', fontWeight:600, color:'#c4b5fd' }}>{p.name}</span>)}
                  </div>
                </div>
              )}
            </div>
          )}
          {activeTab==='announcements' && (
            <div>
              <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem' }}>Community Announcements</h3>
              {announcements.length===0 ? (
                <p style={{ textAlign:'center', color:'var(--text-muted)', padding:'2rem 0' }}>No announcements yet</p>
              ) : (
                <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
                  {announcements.map((a,idx)=>(
                    <div key={idx} style={{ background:'rgba(245,158,11,0.07)', border:'1px solid rgba(245,158,11,0.2)', borderRadius:10, padding:'0.9rem' }}>
                      <p style={{ fontSize:'0.7rem', fontWeight:800, color:'#f59e0b', margin:'0 0 4px', textTransform:'uppercase' }}>{a.type}</p>
                      <h4 style={{ fontWeight:700, color:'var(--text-primary)', margin:'0 0 6px', fontSize:'0.9rem' }}>{a.title}</h4>
                      <p style={{ fontSize:'0.82rem', color:'var(--text-secondary)', margin:'0 0 5px' }}>{a.message}</p>
                      <p style={{ fontSize:'0.72rem', color:'var(--text-muted)', margin:0 }}>Valid until: {new Date(a.valid_until).toLocaleDateString()}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {activeTab==='admin' && isAdmin && (
            <div>
              <h3 style={{ fontWeight:700, color:'var(--text-primary)', marginBottom:'1rem', fontSize:'1rem' }}>Admin Actions</h3>
              <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
                <button onClick={sendAlert} style={{ padding:'0.75rem', background:'linear-gradient(135deg,#7c3aed,#a855f7)', border:'none', borderRadius:10, color:'#fff', fontWeight:700, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, boxShadow:'0 4px 14px rgba(139,92,246,0.35)' }}>
                  <Megaphone size={18}/> Send Community Alert
                </button>
                <button onClick={()=>navigate('/reports')} style={{ padding:'0.75rem', background:'rgba(16,185,129,0.1)', border:'1px solid rgba(16,185,129,0.3)', borderRadius:10, color:'#6ee7b7', fontWeight:700, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>
                  <BarChart3 size={18}/> View Reports
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommunityHub;
