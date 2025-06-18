import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Star Logo Component
const StarLogo = () => (
  <svg className="logo" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <path 
      d="M50 5 L60 35 L90 45 L60 55 L50 85 L40 55 L10 45 L40 35 Z" 
      fill="white" 
      stroke="#4CAF50" 
      strokeWidth="1"
    />
    <circle cx="50" cy="45" r="8" fill="#4CAF50" opacity="0.8"/>
  </svg>
);

// Navigation Icons (simplified)
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

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { path: "/", label: "Dashboard", icon: DashboardIcon },
    { path: "/study", label: "Study Rooms", icon: StudyIcon },
    { path: "/quiz", label: "Quiz Arena", icon: QuizIcon },
    { path: "/groups", label: "Study Groups", icon: GroupIcon },
    { path: "/ai-helper", label: "AI Helper", icon: AIIcon },
    { path: "/analytics", label: "Analytics", icon: AnalyticsIcon },
    { path: "/settings", label: "Settings", icon: SettingsIcon },
  ];

  return (
    <nav className="left-sidebar">
      <ul className="nav-menu">
        {navItems.map((item) => {
          const IconComponent = item.icon;
          return (
            <li key={item.path} className="nav-item">
              <Link 
                to={item.path} 
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                <IconComponent />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
};

// Header Component
const Header = () => (
  <header className="header">
    <div className="header-left">
      <StarLogo />
      <div className="brand-text">
        <div className="app-name">StarGuide</div>
        <div className="tagline">powered by IDFS PathwayIQ™</div>
      </div>
    </div>
    <div className="header-right">
      <button className="btn btn-secondary">Profile</button>
      <button className="btn btn-primary">Login</button>
    </div>
  </header>
);

// Right Sidebar Component
const RightSidebar = () => (
  <aside className="right-sidebar">
    <div className="card">
      <h3 className="card-title">Quick Stats</h3>
      <div className="card-content">
        <div className="flex justify-between mb-16">
          <span>Study Streak</span>
          <span className="text-success">7 days</span>
        </div>
        <div className="flex justify-between mb-16">
          <span>XP Points</span>
          <span className="text-success">1,250</span>
        </div>
        <div className="flex justify-between">
          <span>Level</span>
          <span className="text-success">12</span>
        </div>
      </div>
    </div>
    
    <div className="card">
      <h3 className="card-title">Active Users</h3>
      <div className="card-content">
        <div className="flex justify-between mb-16">
          <span>Online Now</span>
          <span className="status-online">• 24</span>
        </div>
        <div className="flex justify-between mb-16">
          <span>In Study Rooms</span>
          <span className="status-online">• 12</span>
        </div>
        <div className="flex justify-between">
          <span>Taking Quizzes</span>
          <span className="status-online">• 8</span>
        </div>
      </div>
    </div>
    
    <div className="card">
      <h3 className="card-title">Upcoming</h3>
      <div className="card-content">
        <div className="mb-16">
          <div className="text-primary">Math Quiz</div>
          <div className="text-secondary">2:30 PM Today</div>
        </div>
        <div>
          <div className="text-primary">Study Group</div>
          <div className="text-secondary">4:00 PM Today</div>
        </div>
      </div>
    </div>
  </aside>
);

// Page Components
const Dashboard = () => {
  const [apiStatus, setApiStatus] = useState("Checking...");

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
    checkApi();
  }, []);

  return (
    <div className="fade-in">
      <div className="card">
        <h2 className="card-title">Welcome to StarGuide</h2>
        <div className="card-content">
          <p className="mb-16">Your AI-powered learning companion is ready to help you achieve your academic goals.</p>
          <div className="flex gap-12">
            <button className="btn btn-primary">Start Learning</button>
            <button className="btn btn-secondary">Take Tour</button>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h3 className="card-title">System Status</h3>
        <div className="card-content">
          <div className="flex justify-between mb-16">
            <span>API Connection</span>
            <span className={apiStatus === "Hello World" ? "status-online" : "status-offline"}>
              {apiStatus}
            </span>
          </div>
          <div className="flex justify-between mb-16">
            <span>Database</span>
            <span className="status-online">Connected</span>
          </div>
          <div className="flex justify-between">
            <span>Real-time Features</span>
            <span className="status-offline">Coming Soon</span>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h3 className="card-title">Recent Activity</h3>
        <div className="card-content">
          <p>No recent activity to display. Start your learning journey!</p>
        </div>
      </div>
    </div>
  );
};

const StudyRooms = () => (
  <div className="fade-in">
    <div className="card">
      <h2 className="card-title">Study Rooms</h2>
      <div className="card-content">
        <p>Real-time collaborative study rooms coming soon!</p>
        <button className="btn btn-primary">Create Room</button>
      </div>
    </div>
  </div>
);

const QuizArena = () => (
  <div className="fade-in">
    <div className="card">
      <h2 className="card-title">Quiz Arena</h2>
      <div className="card-content">
        <p>Competitive quizzes and live battles coming soon!</p>
        <button className="btn btn-primary">Join Quiz</button>
      </div>
    </div>
  </div>
);

const StudyGroups = () => (
  <div className="fade-in">
    <div className="card">
      <h2 className="card-title">Study Groups</h2>
      <div className="card-content">
        <p>Connect with peers and form study groups!</p>
        <button className="btn btn-primary">Create Group</button>
      </div>
    </div>
  </div>
);

const AIHelper = () => (
  <div className="fade-in">
    <div className="card">
      <h2 className="card-title">AI Helper</h2>
      <div className="card-content">
        <p>Your intelligent tutor powered by advanced AI!</p>
        <button className="btn btn-primary">Chat with AI</button>
      </div>
    </div>
  </div>
);

const Analytics = () => (
  <div className="fade-in">
    <div className="card">
      <h2 className="card-title">Analytics</h2>
      <div className="card-content">
        <p>Track your learning progress and performance!</p>
        <div className="progress-bar mb-16">
          <div className="progress-fill" style={{width: "65%"}}></div>
        </div>
        <p className="text-secondary">Overall Progress: 65%</p>
      </div>
    </div>
  </div>
);

const Settings = () => (
  <div className="fade-in">
    <div className="card">
      <h2 className="card-title">Settings</h2>
      <div className="card-content">
        <p>Customize your StarGuide experience!</p>
        <button className="btn btn-secondary">Preferences</button>
      </div>
    </div>
  </div>
);

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Header />
        <div className="layout-container">
          <Navigation />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/study" element={<StudyRooms />} />
              <Route path="/quiz" element={<QuizArena />} />
              <Route path="/groups" element={<StudyGroups />} />
              <Route path="/ai-helper" element={<AIHelper />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
          <RightSidebar />
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;