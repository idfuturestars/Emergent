import React, { useState, useEffect, useContext, createContext, useCallback, useMemo, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation, Link, useParams } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Authentication Context with performance optimization
const AuthContext = createContext();

// Star Logo Component - Enhanced IDFS PathwayIQ Design
const StarLogo = () => (
  <div className="starguide-logo">
    <div className="logo-icon">
      ⭐
    </div>
    <div className="logo-text">
      <div className="logo-main">StarGuide</div>
      <div className="logo-subtitle">powered by IDFS PathwayIQ™</div>
    </div>
  </div>
);

// Mobile Menu Icon
const MenuIcon = () => (
  <svg fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"/>
  </svg>
);

// Close Icon
const CloseIcon = () => (
  <svg fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd"/>
  </svg>
);

// Navigation Icons
const DashboardIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path d="M10 12l-2-2m0 0l2-2m-2 2h8m-8 0H6a2 2 0 01-2-2V6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2h-2"/>
  </svg>
);

const StudyIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
  </svg>
);

const QuizIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
  </svg>
);

const GroupIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z"/>
  </svg>
);

const AIIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
  </svg>
);

const AnalyticsIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/>
  </svg>
);

const SettingsIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd"/>
  </svg>
);

const HelpIcon = () => (
  <svg className="nav-icon" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"/>
  </svg>
);

// Auth Hook
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      // Set default auth header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Verify token and get user info
      axios.get(`${API}/auth/me`)
        .then(response => {
          setUser(response.data);
        })
        .catch(() => {
          // Token invalid, clear it
          localStorage.removeItem('token');
          setToken(null);
          delete axios.defaults.headers.common['Authorization'];
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { token: newToken, user: userData } = response.data;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { token: newToken, user: newUser } = response.data;
      
      localStorage.setItem('token', newToken);
      setToken(newToken);
      setUser(newUser);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setToken(null);
      setUser(null);
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

// Advanced Navigation Structure - Match StarGuide Advanced Version
const NavigationMenu = ({ currentPath, onNavigate }) => {
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

  return (
    <nav className="starguide-sidebar">
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
                    onNavigate(item.path);
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

// Enhanced Header Component
const Header = ({ user, logout }) => {
  return (
    <header className="starguide-header">
      <div className="header-content">
        <StarLogo />
        
        <div className="header-actions">
          <div className="user-info">
            <span className="user-name">by{user?.username || 'User'} ({user?.role || 'Demo'})</span>
            <button onClick={logout} className="btn btn-ghost btn-sm">
              Logout
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

// Mission Control Dashboard - Main Component
const MissionControl = ({ user }) => {
  const [stats, setStats] = useState({
    level: 2,
    xp: 150,
    maxXp: 200,
    streak: 3,
    onlineUsers: 28
  });

  const [missions, setMissions] = useState([
    {
      id: 'stargate-challenge',
      title: 'Stargate Challenge',
      subtitle: '60-minute Mars mission assessment',
      status: 'ready',
      action: 'Launch Mission'
    },
    {
      id: 'daily-challenge',
      title: 'Daily Challenge',
      subtitle: "Complete today's challenge to maintain your streak!",
      status: 'pending',
      value: 3,
      label: 'Day Streak'
    },
    {
      id: 'skillscan',
      title: 'SkillScan™',
      subtitle: 'Adaptive assessment system',
      status: 'available',
      value: 6,
      label: 'Available'
    }
  ]);

  const [onlineUsers, setOnlineUsers] = useState([
    { name: 'Alex Chen', level: 12, status: 'In Battle' },
    { name: 'Sarah Kim', level: 8, status: 'Taking Quiz' },
    { name: 'Mike Rodriguez', level: 15, status: 'Study Session' }
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

      <div className="grid grid-cols-3">
        <div className="grid-span-2">
          <div className="grid grid-cols-1">
            {missions.map((mission) => (
              <div key={mission.id} className="starguide-card">
                <div className="card-header">
                  <div className="card-icon">
                    {mission.id === 'stargate-challenge' && '🚀'}
                    {mission.id === 'daily-challenge' && '📅'}
                    {mission.id === 'skillscan' && '🔍'}
                  </div>
                  <div>
                    <h3 className="card-title">{mission.title}</h3>
                    <p className="card-subtitle">{mission.subtitle}</p>
                  </div>
                </div>

                <div className="mission-content">
                  {mission.status === 'ready' && (
                    <div className="mission-status">
                      <div className="status-display ready">READY</div>
                      <button className="btn btn-primary mission-button">
                        {mission.action}
                      </button>
                    </div>
                  )}

                  {mission.value && (
                    <div className="mission-value">
                      <div className="value-display">{mission.value}</div>
                      <div className="value-label">{mission.label}</div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="sidebar-stats">
          <div className="starguide-card">
            <div className="card-header">
              <div className="card-icon">⭐</div>
              <h3 className="card-title">Your Status</h3>
            </div>
            
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{stats.level}</div>
                <div className="stat-label">Level</div>
              </div>
              
              <div className="progress-section">
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
            
            <div className="streak-display">
              <div className="streak-value">{stats.streak}</div>
              <div className="streak-label">Days</div>
            </div>
          </div>

          <div className="starguide-card">
            <div className="card-header">
              <div className="card-icon">👥</div>
              <h3 className="card-title">Online Now</h3>
            </div>
            
            <div className="online-stats">
              <div className="online-count">{stats.onlineUsers} users online</div>
              
              <div className="online-users">
                {onlineUsers.map((user, index) => (
                  <div key={index} className="user-item">
                    <div className="user-name">{user.name}</div>
                    <div className="user-details">
                      Level {user.level} • {user.status}
                    </div>
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

// Global achievement notification function
let showAchievementNotification = () => {};

// Achievement System Hook
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

  // Set global function
  useEffect(() => {
    showAchievementNotification = addNotification;
  }, [addNotification]);

  return {
    notifications,
    removeNotification
  };
};
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />;
};

// Login Component
const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [redirect, setRedirect] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(email, password);
    
    if (!result.success) {
      setError(result.error);
    } else {
      setRedirect(true);
    }
    
    setLoading(false);
  };
  
  if (redirect) {
    return <Navigate to="/dashboard" />;
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <StarLogo />
          <h1>Welcome to StarGuide</h1>
          <p>Sign in to your account</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
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
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>Don't have an account? <Link to="/register">Sign up</Link></p>
        </div>
      </div>
    </div>
  );
};

// Register Component
const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'student'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [redirect, setRedirect] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await register(formData);
    
    if (!result.success) {
      setError(result.error);
    } else {
      setRedirect(true);
    }
    
    setLoading(false);
  };
  
  if (redirect) {
    return <Navigate to="/dashboard" />;
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <StarLogo />
          <h1>Join StarGuide</h1>
          <p>Create your account</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="full_name">Full Name</label>
            <input
              type="text"
              id="full_name"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="role">Role</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>Already have an account? <Link to="/login">Sign in</Link></p>
        </div>
      </div>
    </div>
  );
};

// Navigation Component with Mobile Support
const Navigation = ({ isMobileOpen, setIsMobileOpen }) => {
  const location = useLocation();
  const { user } = useAuth();
  
  const navItems = [
    { path: "/dashboard", label: "Dashboard", icon: DashboardIcon },
    { path: "/study", label: "Study Rooms", icon: StudyIcon },
    { path: "/quiz", label: "Quiz Arena", icon: QuizIcon },
    { path: "/groups", label: "Study Groups", icon: GroupIcon },
    { path: "/ai-helper", label: "AI Helper", icon: AIIcon },
    { path: "/analytics", label: "Analytics", icon: AnalyticsIcon },
    { path: "/help", label: "Help Queue", icon: HelpIcon },
    { path: "/settings", label: "Settings", icon: SettingsIcon },
  ];

  const handleNavClick = () => {
    setIsMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Overlay */}
      <div 
        className={`mobile-overlay ${isMobileOpen ? 'mobile-open' : ''}`}
        onClick={() => setIsMobileOpen(false)}
        role="button"
        tabIndex={-1}
        aria-label="Close navigation menu"
      />
      
      {/* Navigation Sidebar */}
      <nav className={`left-sidebar ${isMobileOpen ? 'mobile-open' : ''}`}>
        <ul className="nav-menu" role="list">
          {navItems.map((item) => {
            const IconComponent = item.icon;
            return (
              <li key={item.path} className="nav-item" role="listitem">
                <Link 
                  to={item.path} 
                  className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
                  onClick={handleNavClick}
                  role="menuitem"
                  aria-current={location.pathname === item.path ? 'page' : undefined}
                >
                  <IconComponent />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </>
  );
};

// Header Component with Mobile Menu
const Header = ({ isMobileOpen, setIsMobileOpen }) => {
  const { user, logout } = useAuth();

  return (
    <header className="header" role="banner">
      <div className="header-left">
        <button 
          className="mobile-menu-toggle"
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          aria-label={isMobileOpen ? "Close navigation menu" : "Open navigation menu"}
          aria-expanded={isMobileOpen}
          aria-controls="navigation-menu"
        >
          {isMobileOpen ? <CloseIcon /> : <MenuIcon />}
        </button>
        <StarLogo />
        <div className="brand-text">
          <div className="app-name">StarGuide</div>
          <div className="tagline">powered by IDFS PathwayIQ™</div>
        </div>
      </div>
      <div className="header-right">
        {user && (
          <>
            <span className="user-greeting">Welcome, {user.username}</span>
            <button className="btn btn-secondary" onClick={logout} type="button">Logout</button>
          </>
        )}
      </div>
    </header>
  );
};

// Right Sidebar Component
const RightSidebar = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    study_streak: 0,
    xp_points: 0,
    level: 1
  });

  useEffect(() => {
    if (user) {
      setStats({
        study_streak: user.study_streak || 0,
        xp_points: user.xp_points || 0,
        level: user.level || 1
      });
    }
  }, [user]);

  return (
    <aside className="right-sidebar" role="complementary">
      <div className="card">
        <h3 className="card-title">Your Progress</h3>
        <div className="card-content">
          <div className="flex justify-between mb-16">
            <span>Study Streak</span>
            <span className="text-success">{stats.study_streak} days</span>
          </div>
          <div className="flex justify-between mb-16">
            <span>XP Points</span>
            <span className="text-success">{stats.xp_points}</span>
          </div>
          <div className="flex justify-between">
            <span>Level</span>
            <span className="text-success">{stats.level}</span>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h3 className="card-title">Platform Status</h3>
        <div className="card-content">
          <div className="flex justify-between mb-16">
            <span>AI Services</span>
            <span className="status-online">• Online</span>
          </div>
          <div className="flex justify-between mb-16">
            <span>Real-time Chat</span>
            <span className="status-online">• Active</span>
          </div>
          <div className="flex justify-between">
            <span>Analytics</span>
            <span className="status-online">• Running</span>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h3 className="card-title">Quick Actions</h3>
        <div className="card-content">
          <button className="btn btn-primary mb-16" style={{width: '100%'}}>
            Start AI Chat
          </button>
          <button className="btn btn-secondary" style={{width: '100%'}}>
            Join Study Room
          </button>
        </div>
      </div>
    </aside>
  );
};

// Dashboard Component
const Dashboard = () => {
  const { user } = useAuth();
  const [apiStatus, setApiStatus] = useState("Checking...");
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    const checkApi = async () => {
      try {
        const response = await axios.get(`${API}/`);
        setApiStatus(response.data.message || "Connected");
      } catch (error) {
        setApiStatus("Connection failed");
        console.error("API Error:", error);
      }
    };

    const loadAnalytics = async () => {
      try {
        const response = await axios.get(`${API}/analytics/dashboard`);
        setAnalytics(response.data);
      } catch (error) {
        console.error("Analytics error:", error);
      }
    };

    checkApi();
    if (user) {
      loadAnalytics();
    }
  }, [user]);

  return (
    <div className="fade-in" role="main">
      <div className="card">
        <h2 className="card-title">Welcome to StarGuide, {user?.username}!</h2>
        <div className="card-content">
          <p className="mb-16">Your AI-powered learning companion with real-time collaboration features.</p>
          <div className="flex gap-12">
            <Link to="/ai-helper" className="btn btn-primary">Start AI Chat</Link>
            <Link to="/quiz" className="btn btn-secondary">Take Quiz</Link>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h3 className="card-title">System Status</h3>
        <div className="card-content">
          <div className="flex justify-between mb-16">
            <span>API Connection</span>
            <span className={apiStatus.includes("StarGuide") ? "status-online" : "status-offline"}>
              {apiStatus}
            </span>
          </div>
          <div className="flex justify-between mb-16">
            <span>AI Services</span>
            <span className="status-online">OpenAI, Claude, Gemini Ready</span>
          </div>
          <div className="flex justify-between">
            <span>Real-time Features</span>
            <span className="status-online">WebSocket Active</span>
          </div>
        </div>
      </div>
      
      {analytics && (
        <div className="card">
          <h3 className="card-title">Your Learning Analytics</h3>
          <div className="card-content">
            <div className="flex justify-between mb-16">
              <span>Total Assessments</span>
              <span className="text-success">{analytics.total_assessments}</span>
            </div>
            <div className="flex justify-between mb-16">
              <span>Average Score</span>
              <span className="text-success">{analytics.average_score.toFixed(1)}%</span>
            </div>
            <div className="progress-bar mb-16">
              <div 
                className="progress-fill" 
                style={{width: `${analytics.average_score}%`}}
                role="progressbar" 
                aria-valuenow={analytics.average_score} 
                aria-valuemin="0" 
                aria-valuemax="100"
              ></div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Enhanced AI Chat Interface with improved features
const AIHelper = () => {
  const [conversations, setConversations] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [aiProvider, setAiProvider] = useState('openai');
  const [selectedModel, setSelectedModel] = useState('gpt-4o');
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [isStreaming, setIsStreaming] = useState(false);
  const { user } = useAuth();
  const messagesEndRef = useRef(null);

  // AI Provider configurations with enhanced models
  const aiProviders = useMemo(() => ({
    openai: {
      name: 'OpenAI',
      models: [
        { id: 'gpt-4o', name: 'GPT-4o (Omni)', description: 'Latest multimodal model' },
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
        { id: 'gemini-2.0-flash-exp', name: 'Gemini 2.0 Flash', description: 'Experimental latest' },
        { id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', description: 'High performance' },
        { id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', description: 'Speed optimized' }
      ],
      icon: '💎'
    }
  }), []);

  // Enhanced message sending with typing indicators
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
    setIsStreaming(true);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API}/ai/chat`, {
        message,
        provider: aiProvider,
        model: selectedModel,
        session_id: sessionId,
        conversation_history: conversations.slice(-10) // Keep last 10 messages for context
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
      
      // Achievement check for AI interaction
      if (conversations.length > 0 && conversations.length % 10 === 0) {
        showAchievementNotification('AI Enthusiast', `You've had ${conversations.length + 1} AI conversations!`);
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
      setIsStreaming(false);
    }
  }, [currentMessage, aiProvider, selectedModel, sessionId, conversations]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversations, isTyping]);

  // Enhanced provider switching
  const handleProviderChange = useCallback((provider) => {
    setAiProvider(provider);
    const firstModel = aiProviders[provider].models[0];
    setSelectedModel(firstModel.id);
  }, [aiProviders]);

  // Quick action buttons for common tasks
  const quickActions = useMemo(() => [
    { label: '📚 Explain a concept', prompt: 'Can you explain a complex concept in simple terms?' },
    { label: '✍️ Create quiz questions', prompt: 'Generate 5 quiz questions about ' },
    { label: '🔍 Research help', prompt: 'Help me research the topic of ' },
    { label: '💡 Study tips', prompt: 'Give me effective study tips for ' },
    { label: '🧮 Math problem', prompt: 'Help me solve this math problem: ' },
    { label: '📝 Essay outline', prompt: 'Create an essay outline for the topic: ' }
  ], []);

  return (
    <div className="ai-helper-container">
      <div className="ai-header">
        <h2>🤖 AI Study Assistant</h2>
        <div className="ai-provider-selector">
          {Object.entries(aiProviders).map(([key, provider]) => (
            <button
              key={key}
              className={`provider-btn ${aiProvider === key ? 'active' : ''}`}
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
            className="form-control model-select"
          >
            {aiProviders[aiProvider].models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name} - {model.description}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="quick-actions">
        <h3>Quick Actions:</h3>
        <div className="quick-action-buttons">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="btn btn-sm btn-ghost quick-action-btn"
              onClick={() => setCurrentMessage(action.prompt)}
            >
              {action.label}
            </button>
          ))}
        </div>
      </div>

      <div className="ai-conversation">
        {conversations.map((message) => (
          <div key={message.id} className={`message ${message.role === 'user' ? 'user-message' : 'ai-message'} ${message.error ? 'error-message' : ''}`}>
            <div className="message-header">
              <span className="message-role">
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
          <div className="message ai-message typing-indicator">
            <div className="message-header">
              <span className="message-role">
                {aiProviders[aiProvider]?.icon} {aiProviders[aiProvider]?.name} is thinking...
              </span>
            </div>
            <div className="typing-animation">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="ai-input-section">
        <div className="input-group">
          <textarea
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            placeholder={`Ask ${aiProviders[aiProvider]?.name} anything about your studies...`}
            className="form-control message-input"
            rows="3"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
              }
            }}
            disabled={isStreaming}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!currentMessage.trim() || isStreaming}
            className={`btn btn-primary send-btn ${isStreaming ? 'loading' : ''}`}
          >
            {isStreaming ? 'Sending...' : 'Send 📤'}
          </button>
        </div>
        <div className="input-help">
          <small>Press Enter to send • Shift+Enter for new line • Try the quick actions above!</small>
        </div>
      </div>
    </div>
  );

// Study Groups Component
const StudyGroups = () => {
  const [groups, setGroups] = useState([]);
  const [myGroups, setMyGroups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newGroup, setNewGroup] = useState({
    name: '',
    description: '',
    subject: '',
    max_members: 10,
    is_public: true
  });

  useEffect(() => {
    loadGroups();
    loadMyGroups();
  }, []);

  const loadGroups = async () => {
    try {
      const response = await axios.get(`${API}/groups`);
      setGroups(response.data.groups);
    } catch (error) {
      console.error('Error loading groups:', error);
    }
  };

  const loadMyGroups = async () => {
    try {
      const response = await axios.get(`${API}/groups/my`);
      setMyGroups(response.data.groups);
    } catch (error) {
      console.error('Error loading my groups:', error);
    }
  };

  const createGroup = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await axios.post(`${API}/groups`, newGroup);
      setShowCreateForm(false);
      setNewGroup({ name: '', description: '', subject: '', max_members: 10, is_public: true });
      loadGroups();
      loadMyGroups();
    } catch (error) {
      console.error('Error creating group:', error);
    } finally {
      setLoading(false);
    }
  };

  const joinGroup = async (groupId) => {
    try {
      await axios.post(`${API}/groups/join`, { group_id: groupId });
      loadGroups();
      loadMyGroups();
    } catch (error) {
      console.error('Error joining group:', error);
    }
  };

  return (
    <div className="fade-in" role="main">
      <div className="card">
        <div className="flex justify-between items-center mb-24">
          <h2 className="card-title">Study Groups</h2>
          <button 
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="btn btn-primary"
          >
            Create Group
          </button>
        </div>

        {showCreateForm && (
          <form onSubmit={createGroup} className="create-group-form mb-24">
            <div className="form-row">
              <div className="form-group">
                <label>Group Name:</label>
                <input
                  type="text"
                  value={newGroup.name}
                  onChange={(e) => setNewGroup({...newGroup, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Subject:</label>
                <input
                  type="text"
                  value={newGroup.subject}
                  onChange={(e) => setNewGroup({...newGroup, subject: e.target.value})}
                  required
                />
              </div>
            </div>
            
            <div className="form-group">
              <label>Description:</label>
              <textarea
                value={newGroup.description}
                onChange={(e) => setNewGroup({...newGroup, description: e.target.value})}
                rows={3}
                required
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Max Members:</label>
                <input
                  type="number"
                  value={newGroup.max_members}
                  onChange={(e) => setNewGroup({...newGroup, max_members: parseInt(e.target.value)})}
                  min={2}
                  max={50}
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={newGroup.is_public}
                    onChange={(e) => setNewGroup({...newGroup, is_public: e.target.checked})}
                  />
                  Public Group
                </label>
              </div>
            </div>
            
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Creating...' : 'Create Group'}
              </button>
              <button 
                type="button" 
                onClick={() => setShowCreateForm(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      {/* My Groups */}
      {myGroups.length > 0 && (
        <div className="card">
          <h3 className="card-title">My Study Groups</h3>
          <div className="groups-grid">
            {myGroups.map(group => (
              <div key={group.id} className="group-card">
                <h4>{group.name}</h4>
                <p className="group-subject">{group.subject}</p>
                <p className="group-description">{group.description}</p>
                <div className="group-info">
                  <span>Members: {group.members?.length || 0}/{group.max_members}</span>
                  <span className={group.is_public ? 'status-online' : 'status-offline'}>
                    {group.is_public ? 'Public' : 'Private'}
                  </span>
                </div>
                <Link to={`/study/${group.id}`} className="btn btn-primary">
                  Enter Room
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available Groups */}
      <div className="card">
        <h3 className="card-title">Available Study Groups</h3>
        <div className="groups-grid">
          {groups.filter(group => !group.is_member).map(group => (
            <div key={group.id} className="group-card">
              <h4>{group.name}</h4>
              <p className="group-subject">{group.subject}</p>
              <p className="group-description">{group.description}</p>
              <div className="group-info">
                <span>Members: {group.member_count}/{group.max_members}</span>
                <span className="status-online">Public</span>
              </div>
              <button 
                onClick={() => joinGroup(group.id)}
                className="btn btn-secondary"
                disabled={group.member_count >= group.max_members}
              >
                {group.member_count >= group.max_members ? 'Full' : 'Join Group'}
              </button>
            </div>
          ))}
        </div>
        
        {groups.filter(group => !group.is_member).length === 0 && (
          <p className="text-secondary">No available groups. Create one to get started!</p>
        )}
      </div>
    </div>
  );
};

// Placeholder components for other pages
// Study Rooms Component with Real-time Features
const StudyRooms = () => {
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    loadMyGroups();
  }, []);

  const loadMyGroups = async () => {
    try {
      const response = await axios.get(`${API}/groups/my`);
      setGroups(response.data.groups);
    } catch (error) {
      console.error('Error loading groups:', error);
    } finally {
      setLoading(false);
    }
  };

  const enterStudyRoom = (group) => {
    setSelectedGroup(group);
  };

  const leaveStudyRoom = () => {
    setSelectedGroup(null);
  };

  if (selectedGroup) {
    return (
      <StudyRoom 
        groupId={selectedGroup.id} 
        user={user} 
        onLeave={leaveStudyRoom} 
      />
    );
  }

  return (
    <div className="fade-in" role="main">
      <div className="card">
        <h2 className="card-title">Study Rooms</h2>
        <div className="card-content">
          <p>Real-time collaborative study rooms with live chat and shared tools!</p>
          
          {loading ? (
            <p>Loading your study groups...</p>
          ) : groups.length > 0 ? (
            <div className="groups-grid">
              {groups.map(group => (
                <div key={group.id} className="group-card">
                  <h4>{group.name}</h4>
                  <p className="group-subject">{group.subject}</p>
                  <p className="group-description">{group.description}</p>
                  <div className="group-info">
                    <span>Members: {group.members?.length || 0}/{group.max_members}</span>
                  </div>
                  <button 
                    onClick={() => enterStudyRoom(group)}
                    className="btn btn-primary"
                  >
                    Enter Study Room
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>You haven't joined any study groups yet.</p>
              <Link to="/groups" className="btn btn-primary">
                Browse Study Groups
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Quiz Arena Component with Live Quiz Features
const QuizArena = () => {
  const [showJoinForm, setShowJoinForm] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [roomCode, setRoomCode] = useState('');
  const [activeQuiz, setActiveQuiz] = useState(null);
  const [newRoom, setNewRoom] = useState({
    name: '',
    assessment_id: '',
    max_participants: 20
  });
  const [assessments, setAssessments] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    loadAssessments();
  }, []);

  const loadAssessments = async () => {
    try {
      const response = await axios.get(`${API}/assessments`);
      setAssessments(response.data.assessments);
    } catch (error) {
      console.error('Error loading assessments:', error);
    }
  };

  const joinQuizRoom = async (e) => {
    e.preventDefault();
    if (!roomCode.trim()) return;

    try {
      const response = await axios.post(`${API}/quiz/rooms/${roomCode}/join`);
      setActiveQuiz(roomCode);
    } catch (error) {
      console.error('Error joining quiz room:', error);
      alert('Failed to join quiz room. Please check the room code.');
    }
  };

  const createQuizRoom = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post(`${API}/quiz/rooms`, {
        assessment_id: newRoom.assessment_id,
        room_name: newRoom.name,
        max_participants: newRoom.max_participants
      });
      
      const createdRoom = response.data.room;
      setActiveQuiz(createdRoom.room_code);
      setShowCreateForm(false);
    } catch (error) {
      console.error('Error creating quiz room:', error);
      alert('Failed to create quiz room.');
    }
  };

  const exitQuiz = () => {
    setActiveQuiz(null);
    setRoomCode('');
    setShowJoinForm(false);
    setShowCreateForm(false);
  };

  if (activeQuiz) {
    return (
      <LiveQuiz 
        roomCode={activeQuiz} 
        user={user} 
        onExit={exitQuiz} 
      />
    );
  }

  return (
    <div className="fade-in" role="main">
      <div className="card">
        <h2 className="card-title">Quiz Arena</h2>
        <div className="card-content">
          <p>Competitive quizzes and live battles with real-time synchronization!</p>
          
          <div className="quiz-actions">
            <button 
              onClick={() => setShowJoinForm(!showJoinForm)}
              className="btn btn-primary"
            >
              Join Quiz Room
            </button>
            
            {user?.role === 'teacher' && (
              <button 
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="btn btn-secondary"
              >
                Create Quiz Room
              </button>
            )}
          </div>

          {showJoinForm && (
            <form onSubmit={joinQuizRoom} className="quiz-form">
              <h3>Join Quiz Room</h3>
              <div className="form-group">
                <label>Room Code:</label>
                <input
                  type="text"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value)}
                  placeholder="Enter 6-digit room code"
                  maxLength={6}
                  required
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">
                  Join Room
                </button>
                <button 
                  type="button" 
                  onClick={() => setShowJoinForm(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {showCreateForm && (
            <form onSubmit={createQuizRoom} className="quiz-form">
              <h3>Create Quiz Room</h3>
              <div className="form-group">
                <label>Room Name:</label>
                <input
                  type="text"
                  value={newRoom.name}
                  onChange={(e) => setNewRoom({...newRoom, name: e.target.value})}
                  required
                />
              </div>
              <div className="form-group">
                <label>Select Assessment:</label>
                <select
                  value={newRoom.assessment_id}
                  onChange={(e) => setNewRoom({...newRoom, assessment_id: e.target.value})}
                  required
                >
                  <option value="">Choose an assessment...</option>
                  {assessments.map(assessment => (
                    <option key={assessment.id} value={assessment.id}>
                      {assessment.title} ({assessment.subject})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Max Participants:</label>
                <input
                  type="number"
                  value={newRoom.max_participants}
                  onChange={(e) => setNewRoom({...newRoom, max_participants: parseInt(e.target.value)})}
                  min={2}
                  max={100}
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">
                  Create Room
                </button>
                <button 
                  type="button" 
                  onClick={() => setShowCreateForm(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

const Analytics = () => {
  const { user } = useAuth();
  const [viewMode, setViewMode] = useState('basic'); // basic or advanced
  
  return (
    <div className="fade-in" role="main">
      <div className="analytics-header">
        <h2 className="card-title">Learning Analytics</h2>
        <div className="view-toggle">
          <button 
            className={`btn ${viewMode === 'basic' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setViewMode('basic')}
          >
            Basic View
          </button>
          <button 
            className={`btn ${viewMode === 'advanced' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setViewMode('advanced')}
          >
            Advanced Analytics
          </button>
        </div>
      </div>

      {viewMode === 'basic' ? (
        <div className="card">
          <div className="card-content">
            <p>Track your learning progress with AI-powered insights!</p>
            <div className="progress-bar mb-16">
              <div className="progress-fill" style={{width: "75%"}}></div>
            </div>
            <p className="text-secondary">Overall Progress: 75%</p>
            <div className="analytics-summary">
              <div className="summary-item">
                <span className="summary-label">Study Streak:</span>
                <span className="summary-value">{user?.study_streak || 0} days</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">XP Points:</span>
                <span className="summary-value">{user?.xp_points || 0}</span>
              </div>
              <div className="summary-item">
                <span className="summary-label">Level:</span>
                <span className="summary-value">{user?.level || 1}</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <AdvancedAnalytics user={user} />
      )}
    </div>
  );
};

const HelpQueue = () => (
  <div className="fade-in" role="main">
    <div className="card">
      <h2 className="card-title">Help Queue</h2>
      <div className="card-content">
        <p>Get help from teachers and peers when you need it!</p>
        <button className="btn btn-primary">Request Help</button>
      </div>
    </div>
  </div>
);

const Settings = () => (
  <div className="fade-in" role="main">
    <div className="card">
      <h2 className="card-title">Settings</h2>
      <div className="card-content">
        <p>Customize your StarGuide experience!</p>
        <button className="btn btn-secondary">Update Preferences</button>
      </div>
    </div>
  </div>
);

// Quiz Room Wrapper Component
const QuizRoomWrapper = () => {
  const { roomCode } = useParams();
  const { user } = useAuth();
  
  return (
    <LiveQuiz 
      roomCode={roomCode} 
      user={user} 
      onExit={() => window.history.back()} 
    />
  );
};

// Study Room Wrapper Component  
const StudyRoomWrapper = () => {
  const { groupId } = useParams();
  const { user } = useAuth();
  
  return (
    <StudyRoom 
      groupId={groupId} 
      user={user} 
      onLeave={() => window.history.back()} 
    />
  );
};

// Main App Component
function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { notifications, removeNotification } = useAchievements();

  // Close mobile menu on window resize
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setIsMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isMobileMenuOpen]);

  return (
    <AuthProvider>
      <div className="App">
        <BrowserRouter>
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Protected Routes */}
            <Route path="/*" element={
              <ProtectedRoute>
                <Header isMobileOpen={isMobileMenuOpen} setIsMobileOpen={setIsMobileMenuOpen} />
                <div className="layout-container">
                  <Navigation isMobileOpen={isMobileMenuOpen} setIsMobileOpen={setIsMobileMenuOpen} />
                  <main className="main-content">
                    <Routes>
                      <Route path="/" element={<Navigate to="/dashboard" />} />
                      <Route path="/dashboard" element={<Dashboard />} />
                      <Route path="/study" element={<StudyRooms />} />
                      <Route path="/study/:groupId" element={<StudyRoomWrapper />} />
                      <Route path="/quiz" element={<QuizArena />} />
                      <Route path="/quiz/:roomCode" element={<QuizRoomWrapper />} />
                      <Route path="/groups" element={<StudyGroups />} />
                      <Route path="/ai-helper" element={<AIHelper />} />
                      <Route path="/analytics" element={<Analytics />} />
                      <Route path="/help" element={<HelpQueue />} />
                      <Route path="/settings" element={<Settings />} />
                    </Routes>
                  </main>
                  <RightSidebar />
                </div>
              </ProtectedRoute>
            } />
          </Routes>
        </BrowserRouter>
        
        {/* Achievement Notifications */}
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
    </AuthProvider>
  );
}

export default App;