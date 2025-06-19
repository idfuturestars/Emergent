import React, { useState, useEffect, useContext, createContext, useCallback, useMemo, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation, Link, useParams } from 'react-router-dom';
import axios from 'axios';
import io from 'socket.io-client';
import './App.css';

// Import components
import BattleArena from './components/BattleArena';
import SkillScan from './components/SkillScan';
import StarBadges from './components/StarBadges';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ================================
// AUTHENTICATION CONTEXT
// ================================
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = useCallback(async (email, password) => {
    try {
      console.log('Login function called with API:', API);
      const response = await axios.post(`${API}/auth/login`, { email, password });
      console.log('Login response:', response.data);
      const { token, user: userData } = response.data;
      
      localStorage.setItem('token', token);
      setUser(userData);
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error response:', error.response?.data);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  }, []);

  const register = useCallback(async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { token, user: newUser } = response.data;
      
      localStorage.setItem('token', token);
      setUser(newUser);
      
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        await axios.post(`${API}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  const contextValue = useMemo(() => ({
    user,
    login,
    register,
    logout,
    loading
  }), [user, login, register, logout, loading]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// ================================
// LOGO COMPONENT
// ================================
const StarLogo = () => (
  <div className="starguide-logo">
    <div className="logo-icon">⭐</div>
    <div className="logo-text">
      <div className="logo-main">StarGuide</div>
      <div className="logo-subtitle">powered by IDFS PathwayIQ™</div>
    </div>
  </div>
);

// ================================
// ACHIEVEMENT SYSTEM
// ================================
const AchievementNotification = ({ achievement, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="achievement-notification">
      <div className="achievement-content">
        <div className="achievement-icon">🏆</div>
        <div className="achievement-text">
          <h3>Achievement Unlocked!</h3>
          <h4>{achievement.title}</h4>
          <p>{achievement.description}</p>
        </div>
        <button className="achievement-close" onClick={onClose}>×</button>
      </div>
    </div>
  );
};

let showAchievementNotification = () => {};

const useAchievements = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((title, description) => {
    const achievement = {
      id: Date.now(),
      title,
      description
    };
    setNotifications(prev => [...prev, achievement]);
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  }, []);

  useEffect(() => {
    showAchievementNotification = addNotification;
  }, [addNotification]);

  return {
    notifications,
    removeNotification
  };
};

// ================================
// NAVIGATION SYSTEM
// ================================
const NavigationMenu = ({ currentPath, onNavigate, isMobile, onClose }) => {
  const menuStructure = [
    {
      section: "Mission Operations",
      items: [
        { id: "mission-control", icon: "🎯", label: "Mission Control", path: "/mission-control", badge: "HQ" },
        { id: "stargate-challenge", icon: "🚀", label: "Stargate Challenge", path: "/stargate-challenge" },
        { id: "skillscan", icon: "🔍", label: "SkillScan™", path: "/skillscan" },
        { id: "starmentor", icon: "🧠", label: "StarMentor™", path: "/starmentor" },
      ]
    },
    {
      section: "Battle Systems",
      items: [
        { id: "battle-arena", icon: "⚔️", label: "Battle Arena", path: "/battle-arena" },
        { id: "galaxy-quests", icon: "🌌", label: "Galaxy Quests", path: "/galaxy-quests" },
        { id: "learning-pods", icon: "🏠", label: "Learning Pods", path: "/learning-pods" },
        { id: "daily-challenges", icon: "📅", label: "Daily Challenges", path: "/daily-challenges" },
        { id: "tournaments", icon: "🏆", label: "Tournaments", path: "/tournaments" },
      ]
    },
    {
      section: "Navigation Systems",
      items: [
        { id: "vision-quest", icon: "👁️", label: "Vision Quest", path: "/vision-quest" },
        { id: "trajectory", icon: "📊", label: "Trajectory", path: "/trajectory" },
        { id: "starrankings", icon: "🏅", label: "StarRankings", path: "/starrankings" },
        { id: "starbadges", icon: "⭐", label: "StarBadges™", path: "/starbadges" },
      ]
    },
    {
      section: "Support Systems", 
      items: [
        { id: "sos-station", icon: "🆘", label: "SOS Station", path: "/sos-station" },
        { id: "mission-intel", icon: "📋", label: "Mission Intel", path: "/mission-intel" },
      ]
    }
  ];

  const handleNavigation = (path) => {
    onNavigate(path);
    if (isMobile && onClose) {
      onClose();
    }
  };

  return (
    <nav className={`starguide-sidebar ${isMobile ? 'mobile' : ''}`}>
      {menuStructure.map((section) => (
        <div key={section.section} className="nav-section">
          <div className="nav-section-title">{section.section}</div>
          <ul className="nav-menu">
            {section.items.map((item) => (
              <li key={item.id} className="nav-item">
                <a
                  href={item.path}
                  className={`nav-link ${currentPath === item.path ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    handleNavigation(item.path);
                  }}
                >
                  <span className="nav-icon">{item.icon}</span>
                  <span className="nav-label">{item.label}</span>
                  {item.badge && (
                    <span className="nav-badge">{item.badge}</span>
                  )}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
};

// ================================
// HEADER COMPONENT
// ================================
const Header = ({ user, logout, onMenuToggle, isMobile }) => {
  return (
    <header className="starguide-header">
      <div className="header-content">
        {isMobile && (
          <button className="mobile-menu-btn" onClick={onMenuToggle}>
            <span className="hamburger"></span>
          </button>
        )}
        
        <StarLogo />
        
        <div className="header-actions">
          <div className="user-info">
            <span className="user-level">Level {user?.level || 1}</span>
            <span className="user-name">{user?.username || 'User'} ({user?.role || 'Demo'})</span>
            <button onClick={logout} className="btn btn-ghost btn-sm">
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

// ================================
// MISSION CONTROL DASHBOARD
// ================================
const MissionControl = ({ user }) => {
  const [stats, setStats] = useState({
    level: user?.level || 2,
    xp: user?.xp_points || 150,
    maxXp: 200,
    streak: user?.study_streak || 3,
    onlineUsers: 28
  });

  const [missions, setMissions] = useState([
    {
      id: 'stargate-challenge',
      title: 'Stargate Challenge',
      subtitle: '60-minute Mars mission assessment',
      status: 'ready',
      action: 'Launch Mission',
      description: 'Complete the ultimate assessment challenge'
    },
    {
      id: 'daily-challenge',
      title: 'Daily Challenge',
      subtitle: "Complete today's challenge to maintain your streak!",
      status: 'pending',
      value: stats.streak,
      label: 'Day Streak',
      description: 'Keep your learning momentum going'
    },
    {
      id: 'skillscan',
      title: 'SkillScan™',
      subtitle: 'Adaptive assessment system',
      status: 'available',
      value: 6,
      label: 'Available',
      description: 'Discover your knowledge gaps'
    }
  ]);

  const [onlineUsers, setOnlineUsers] = useState([
    { name: 'Alex Chen', level: 12, status: 'In Battle', avatar: '👨‍💻' },
    { name: 'Sarah Kim', level: 8, status: 'Taking Quiz', avatar: '👩‍🎓' },
    { name: 'Mike Rodriguez', level: 15, status: 'Study Session', avatar: '👨‍🚀' },
    { name: 'Emma Wilson', level: 10, status: 'AI Chat', avatar: '👩‍💼' }
  ]);

  return (
    <div className="mission-control-dashboard">
      <div className="mission-control-header">
        <div className="mission-control-icon">🎯</div>
        <div>
          <h1 className="mission-control-title">Mission Control</h1>
          <p className="mission-control-subtitle">powered by IDFS PathwayIQ™</p>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="main-content">
          <div className="missions-grid">
            {missions.map((mission) => (
              <div key={mission.id} className="starguide-card mission-card">
                <div className="card-header">
                  <div className="card-icon">
                    {mission.id === 'stargate-challenge' && '🚀'}
                    {mission.id === 'daily-challenge' && '📅'}
                    {mission.id === 'skillscan' && '🔍'}
                  </div>
                  <div className="card-content">
                    <h3 className="card-title">{mission.title}</h3>
                    <p className="card-subtitle">{mission.subtitle}</p>
                    <p className="card-description">{mission.description}</p>
                  </div>
                </div>

                <div className="mission-footer">
                  {mission.status === 'ready' && (
                    <div className="mission-actions">
                      <div className="status-indicator ready">READY</div>
                      <button className="btn btn-primary">
                        {mission.action}
                      </button>
                    </div>
                  )}

                  {mission.value && (
                    <div className="mission-stats">
                      <div className="stat-value">{mission.value}</div>
                      <div className="stat-label">{mission.label}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="sidebar-content">
          <div className="starguide-card">
            <div className="card-header">
              <div className="card-icon">⭐</div>
              <h3 className="card-title">Your Progress</h3>
            </div>
            
            <div className="progress-content">
              <div className="level-display">
                <div className="level-number">Level {stats.level}</div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{width: `${(stats.xp / stats.maxXp) * 100}%`}}
                  ></div>
                </div>
                <div className="progress-text">{stats.xp} / {stats.maxXp} XP</div>
              </div>
            </div>
          </div>

          <div className="starguide-card">
            <div className="card-header">
              <div className="card-icon">🔥</div>
              <h3 className="card-title">Current Streak</h3>
            </div>
            
            <div className="streak-content">
              <div className="streak-number">{stats.streak}</div>
              <div className="streak-label">Days in a row</div>
              <div className="streak-message">Keep it up! 🎯</div>
            </div>
          </div>

          <div className="starguide-card">
            <div className="card-header">
              <div className="card-icon">👥</div>
              <h3 className="card-title">Online Warriors</h3>
            </div>
            
            <div className="online-content">
              <div className="online-count">{stats.onlineUsers} users online</div>
              
              <div className="user-list">
                {onlineUsers.map((user, index) => (
                  <div key={index} className="user-item">
                    <div className="user-avatar">{user.avatar}</div>
                    <div className="user-details">
                      <div className="user-name">{user.name}</div>
                      <div className="user-status">Level {user.level} • {user.status}</div>
                    </div>
                    <div className="status-dot active"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// ================================
// STARGATE CHALLENGE
// ================================
const StargateChallenge = () => {
  const [timeRemaining, setTimeRemaining] = useState(3600); // 60 minutes
  const [isActive, setIsActive] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(1);
  const totalQuestions = 25;

  useEffect(() => {
    if (isActive && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [isActive, timeRemaining]);

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const startChallenge = () => {
    setIsActive(true);
    showAchievementNotification('Challenge Started!', 'Mars mission assessment is now active');
  };

  return (
    <div className="stargate-challenge">
      <div className="challenge-header">
        <div className="challenge-icon">🚀</div>
        <div>
          <h1 className="challenge-title">Stargate Challenge</h1>
          <p className="challenge-subtitle">60-minute Mars mission assessment</p>
        </div>
      </div>

      <div className="challenge-status">
        <div className="timer-display">
          <div className="timer-value">{formatTime(timeRemaining)}</div>
          <div className="timer-label">Time Remaining</div>
        </div>

        <div className="progress-display">
          <div className="question-count">{currentQuestion} / {totalQuestions}</div>
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{width: `${(currentQuestion / totalQuestions) * 100}%`}}
            ></div>
          </div>
        </div>
      </div>

      {!isActive ? (
        <div className="challenge-start">
          <div className="start-card">
            <h3>Ready for Launch?</h3>
            <p>This assessment will test your knowledge across multiple subjects. You have 60 minutes to complete 25 questions.</p>
            <button className="btn btn-primary btn-lg" onClick={startChallenge}>
              Launch Mission 🚀
            </button>
          </div>
        </div>
      ) : (
        <div className="challenge-active">
          <div className="question-card">
            <h3>Question {currentQuestion}</h3>
            <p>Sample assessment question would appear here...</p>
            <div className="answer-options">
              <button className="answer-option">Option A</button>
              <button className="answer-option">Option B</button>
              <button className="answer-option">Option C</button>
              <button className="answer-option">Option D</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// ================================
// STARMENTOR AI COMPONENT
// ================================
const StarMentorAI = () => {
  const [conversations, setConversations] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [aiProvider, setAiProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const messagesEndRef = useRef(null);

  const aiProviders = useMemo(() => ({
    openai: {
      name: 'OpenAI',
      models: [
        { id: 'gpt-4o', name: 'GPT-4o', description: 'Latest multimodal model' },
        { id: 'gpt-4-turbo', name: 'GPT-4 Turbo', description: 'Advanced reasoning' },
        { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast and efficient' }
      ],
      icon: '🤖'
    },
    claude: {
      name: 'Anthropic Claude',
      models: [
        { id: 'claude-3-sonnet', name: 'Claude 3 Sonnet', description: 'Balanced performance' },
        { id: 'claude-3-haiku', name: 'Claude 3 Haiku', description: 'Fast responses' },
        { id: 'claude-3-opus', name: 'Claude 3 Opus', description: 'Maximum capability' }
      ],
      icon: '🧠'
    },
    gemini: {
      name: 'Google Gemini',
      models: [
        { id: 'gemini-2.0-flash-exp', name: 'Gemini 2.0 Flash', description: 'Latest experimental' },
        { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'High performance' },
        { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', description: 'Speed optimized' }
      ],
      icon: '💎'
    }
  }), []);

  const quickActions = useMemo(() => [
    { label: '📚 Explain Concept', prompt: 'Can you explain a complex concept in simple terms?' },
    { label: '✍️ Create Quiz', prompt: 'Generate 5 quiz questions about ' },
    { label: '🔍 Research Help', prompt: 'Help me research the topic of ' },
    { label: '💡 Study Tips', prompt: 'Give me effective study tips for ' },
    { label: '🧮 Math Help', prompt: 'Help me solve this math problem: ' },
    { label: '📝 Essay Outline', prompt: 'Create an essay outline for: ' }
  ], []);

  const sendMessage = useCallback(async (message = currentMessage) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
      provider: aiProvider,
      model: selectedModel
    };

    setConversations(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsTyping(true);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/ai/chat`, {
        message,
        provider: aiProvider,
        model: selectedModel,
        session_id: sessionId,
        conversation_history: conversations.slice(-10)
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        provider: aiProvider,
        model: selectedModel,
        usage: response.data.usage || null
      };

      setConversations(prev => [...prev, aiMessage]);
      
      if (conversations.length > 0 && conversations.length % 5 === 0) {
        showAchievementNotification('AI Expert', `You've had ${conversations.length + 1} AI conversations!`);
      }

    } catch (error) {
      console.error('AI chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        provider: aiProvider,
        model: selectedModel,
        error: true
      };
      setConversations(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [currentMessage, aiProvider, selectedModel, sessionId, conversations]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, isTyping]);

  const handleProviderChange = useCallback((provider) => {
    setAiProvider(provider);
    const firstModel = aiProviders[provider].models[0];
    setSelectedModel(firstModel.id);
  }, [aiProviders]);

  return (
    <div className="starmentor-container">
      <div className="starmentor-header">
        <div className="mentor-icon">🧠</div>
        <div>
          <h1 className="mentor-title">StarMentor™</h1>
          <p className="mentor-subtitle">Your AI-powered learning companion</p>
        </div>
      </div>

      <div className="ai-provider-section">
        <div className="provider-tabs">
          {Object.entries(aiProviders).map(([key, provider]) => (
            <button
              key={key}
              className={`provider-tab ${aiProvider === key ? 'active' : ''}`}
              onClick={() => handleProviderChange(key)}
            >
              <span className="provider-icon">{provider.icon}</span>
              <span className="provider-name">{provider.name}</span>
            </button>
          ))}
        </div>

        <div className="model-selector">
          <select 
            value={selectedModel} 
            onChange={(e) => setSelectedModel(e.target.value)}
            className="model-select"
          >
            {aiProviders[aiProvider].models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name} - {model.description}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="quick-actions-section">
        <h3>Quick Actions:</h3>
        <div className="quick-actions">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="quick-action-btn"
              onClick={() => setCurrentMessage(action.prompt)}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      <div className="conversation-area">
        <div className="messages-container">
          {conversations.map((message) => (
            <div key={message.id} className={`message ${message.role} ${message.error ? 'error' : ''}`}>
              <div className="message-header">
                <span className="message-sender">
                  {message.role === 'user' ? '👤 You' : `${aiProviders[message.provider]?.icon || '🤖'} ${aiProviders[message.provider]?.name || 'AI'}`}
                </span>
                <span className="message-model">{message.model}</span>
                <span className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="message-content">
                {message.content}
              </div>
              {message.usage && (
                <div className="message-usage">
                  Tokens: {message.usage.total_tokens || 'N/A'}
                </div>
              )}
            </div>
          ))}
          
          {isTyping && (
            <div className="message assistant typing">
              <div className="message-header">
                <span className="message-sender">
                  {aiProviders[aiProvider]?.icon} {aiProviders[aiProvider]?.name} is thinking...
                </span>
              </div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-container">
            <textarea
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              placeholder={`Ask ${aiProviders[aiProvider]?.name} anything about your studies...`}
              className="message-input"
              rows="3"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              disabled={isTyping}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!currentMessage.trim() || isTyping}
              className={`send-btn ${isTyping ? 'loading' : ''}`}
            >
              {isTyping ? 'Sending...' : 'Send 🚀'}
            </button>
          </div>
          <div className="input-help">
            Press Enter to send • Shift+Enter for new line • Try the quick actions above!
          </div>
        </div>
      </div>
    </div>
  );
};

// ================================
// LEARNING PODS (STUDY ROOMS)
// ================================
const LearningPods = () => {
  const [pods, setPods] = useState([
    {
      id: 1,
      name: 'Mathematics Mastery',
      subject: 'Mathematics',
      members: 12,
      maxMembers: 20,
      level: 'Advanced',
      status: 'active',
      description: 'Advanced calculus and linear algebra discussions'
    },
    {
      id: 2,
      name: 'Science Squadron',
      subject: 'Physics',
      members: 8,
      maxMembers: 15,
      level: 'Intermediate',
      status: 'active',
      description: 'Quantum mechanics and thermodynamics'
    },
    {
      id: 3,
      name: 'Code Warriors',
      subject: 'Computer Science',
      members: 15,
      maxMembers: 25,
      level: 'Mixed',
      status: 'active',
      description: 'Programming challenges and algorithms'
    }
  ]);

  const [newPodForm, setNewPodForm] = useState({
    name: '',
    subject: '',
    description: '',
    isPublic: true,
    maxMembers: 20
  });

  const [showCreateForm, setShowCreateForm] = useState(false);

  const createPod = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/groups`, newPodForm, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPods(prev => [...prev, response.data]);
      setNewPodForm({ name: '', subject: '', description: '', isPublic: true, maxMembers: 20 });
      setShowCreateForm(false);
      showAchievementNotification('Pod Created!', 'Your learning pod is now active');
    } catch (error) {
      console.error('Error creating pod:', error);
    }
  };

  return (
    <div className="learning-pods">
      <div className="pods-header">
        <div className="pods-icon">🏠</div>
        <div>
          <h1 className="pods-title">Learning Pods</h1>
          <p className="pods-subtitle">Collaborative learning spaces</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowCreateForm(true)}
        >
          Create New Pod
        </button>
      </div>

      {showCreateForm && (
        <div className="create-pod-form">
          <div className="starguide-card">
            <h3>Create New Learning Pod</h3>
            <div className="form-grid">
              <input
                type="text"
                placeholder="Pod Name"
                value={newPodForm.name}
                onChange={(e) => setNewPodForm(prev => ({...prev, name: e.target.value}))}
                className="form-input"
              />
              <input
                type="text"
                placeholder="Subject"
                value={newPodForm.subject}
                onChange={(e) => setNewPodForm(prev => ({...prev, subject: e.target.value}))}
                className="form-input"
              />
              <textarea
                placeholder="Description"
                value={newPodForm.description}
                onChange={(e) => setNewPodForm(prev => ({...prev, description: e.target.value}))}
                className="form-input"
                rows="3"
              />
              <div className="form-actions">
                <button className="btn btn-primary" onClick={createPod}>
                  Create Pod
                </button>
                <button className="btn btn-secondary" onClick={() => setShowCreateForm(false)}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="pods-grid">
        {pods.map((pod) => (
          <div key={pod.id} className="pod-card starguide-card">
            <div className="pod-header">
              <h3 className="pod-name">{pod.name}</h3>
              <div className="pod-subject">{pod.subject}</div>
            </div>
            
            <div className="pod-content">
              <p className="pod-description">{pod.description}</p>
              
              <div className="pod-stats">
                <div className="stat">
                  <span className="stat-value">{pod.members}</span>
                  <span className="stat-label">Members</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{pod.level}</span>
                  <span className="stat-label">Level</span>
                </div>
                <div className="stat">
                  <span className={`status-badge ${pod.status}`}>{pod.status}</span>
                </div>
              </div>
            </div>
            
            <div className="pod-actions">
              <button className="btn btn-primary">Join Pod</button>
              <button className="btn btn-secondary">View Details</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ================================
// MAIN LAYOUT COMPONENT
// ================================
const MainLayout = ({ children }) => {
  const { user, logout } = useAuth();
  const [currentPath, setCurrentPath] = useState('/mission-control');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth <= 768);
  const { notifications, removeNotification } = useAchievements();

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
      if (window.innerWidth > 768) {
        setIsMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleNavigation = (path) => {
    setCurrentPath(path);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const renderContent = () => {
    switch (currentPath) {
      case '/mission-control':
        return <MissionControl user={user} />;
      case '/stargate-challenge':
        return <StargateChallenge />;
      case '/starmentor':
        return <StarMentorAI />;
      case '/learning-pods':
        return <LearningPods />;
      case '/skillscan':
        return <SkillScan />;
      case '/battle-arena':
        return <BattleArena />;
      case '/starbadges':
        return <StarBadges />;
      case '/galaxy-quests':
        return <div className="coming-soon"><h2>🌌 Galaxy Quests</h2><p>Epic learning adventures coming soon!</p></div>;
      case '/daily-challenges':
        return <div className="coming-soon"><h2>📅 Daily Challenges</h2><p>Daily learning objectives coming soon!</p></div>;
      case '/tournaments':
        return <div className="coming-soon"><h2>🏆 Tournaments</h2><p>Competitive tournaments coming soon!</p></div>;
      case '/vision-quest':
        return <div className="coming-soon"><h2>👁️ Vision Quest</h2><p>Goal tracking system coming soon!</p></div>;
      case '/trajectory':
        return <div className="coming-soon"><h2>📊 Trajectory</h2><p>Learning path analytics coming soon!</p></div>;
      case '/starrankings':
        return <div className="coming-soon"><h2>🏅 StarRankings</h2><p>Global leaderboards coming soon!</p></div>;
      case '/sos-station':
        return <div className="coming-soon"><h2>🆘 SOS Station</h2><p>Help queue system coming soon!</p></div>;
      case '/mission-intel':
        return <div className="coming-soon"><h2>📋 Mission Intel</h2><p>Study resources coming soon!</p></div>;
      default:
        return <MissionControl user={user} />;
    }
  };

  return (
    <div className="starguide-container">
      <Header 
        user={user} 
        logout={logout} 
        onMenuToggle={toggleMobileMenu}
        isMobile={isMobile}
      />
      
      <NavigationMenu 
        currentPath={currentPath}
        onNavigate={handleNavigation}
        isMobile={isMobile}
        onClose={() => setIsMobileMenuOpen(false)}
      />
      
      {isMobile && isMobileMenuOpen && (
        <div className="mobile-overlay" onClick={() => setIsMobileMenuOpen(false)} />
      )}

      <main className={`starguide-main ${isMobile ? 'mobile' : ''}`}>
        <div className="content-container">
          {renderContent()}
        </div>
      </main>

      <div className="achievement-notifications">
        {notifications.map((notification) => (
          <AchievementNotification
            key={notification.id}
            achievement={notification}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </div>
    </div>
  );
};

// ================================
// AUTHENTICATION COMPONENTS
// ================================
const LoginForm = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [redirect, setRedirect] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    console.log('Attempting login with:', email, password);
    const result = await login(email, password);
    console.log('Login result:', result);
    
    if (!result.success) {
      setError(result.error);
      console.error('Login failed:', result.error);
    } else {
      console.log('Login successful, redirecting...');
      setRedirect(true);
    }
    
    setLoading(false);
  };
  
  if (redirect) {
    return <Navigate to="/mission-control" />;
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <StarLogo />
          <h1>Welcome to StarGuide</h1>
          <p>powered by IDFS PathwayIQ™</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="form-input"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="form-input"
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {loading ? 'Signing in...' : 'Launch Mission 🚀'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Don't have an account? <Link to="/register">Register here</Link></p>
          <div className="demo-credentials">
            <strong>Demo Credentials:</strong><br />
            Email: demo@starguide.com<br />
            Password: demo123
          </div>
        </div>
      </div>
    </div>
  );
};

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    role: 'student'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [redirect, setRedirect] = useState(false);
  const { register } = useAuth();

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    const { confirmPassword, ...registrationData } = formData;
    const result = await register(registrationData);
    
    if (!result.success) {
      setError(result.error);
    } else {
      setRedirect(true);
    }
    
    setLoading(false);
  };
  
  if (redirect) {
    return <Navigate to="/mission-control" />;
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <StarLogo />
          <h1>Join StarGuide</h1>
          <p>powered by IDFS PathwayIQ™</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="fullName">Full Name</label>
              <input
                type="text"
                id="fullName"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="form-input"
              required
            />
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className="form-input"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="role">Role</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="form-input"
              required
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </div>
          
          <button type="submit" className="btn btn-primary btn-lg" disabled={loading}>
            {loading ? 'Creating Account...' : 'Begin Your Journey 🚀'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Already have an account? <Link to="/login">Sign in here</Link></p>
        </div>
      </div>
    </div>
  );
};

// ================================
// PROTECTED ROUTE COMPONENT
// ================================
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Initializing StarGuide...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" />;
  }

  return children;
};

// ================================
// MAIN APP COMPONENT
// ================================
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/*" element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;