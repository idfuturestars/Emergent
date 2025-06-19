import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  SparklesIcon,
  HomeIcon,
  ChatBubbleLeftRightIcon,
  UserGroupIcon,
  TrophyIcon,
  ChartBarIcon,
  UserCircleIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: '/app/dashboard', icon: HomeIcon },
    { name: 'AI Tutor', href: '/app/ai-tutor', icon: ChatBubbleLeftRightIcon },
    { name: 'Study Groups', href: '/app/study-groups', icon: UserGroupIcon },
    { name: 'Quiz Arena', href: '/app/quiz-arena', icon: TrophyIcon },
    { name: 'Analytics', href: '/app/analytics', icon: ChartBarIcon },
    { name: 'Profile', href: '/app/profile', icon: UserCircleIcon },
  ];

  const isActive = (path) => location.pathname === path;

  const handleLogout = async () => {
    await logout();
  };

  return (
    <>
      {/* Mobile backdrop */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
            onClick={() => setOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ x: open ? 0 : '-100%' }}
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-dark-900/95 backdrop-blur-xl border-r border-gray-800 lg:translate-x-0 lg:static lg:inset-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center h-16 px-6 border-b border-gray-800">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-space-500 to-cosmic-500 rounded-lg flex items-center justify-center ai-avatar">
                <SparklesIcon className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white glow-text">StarGuide</span>
            </div>
          </div>

          {/* User Info */}
          <div className="p-6 border-b border-gray-800">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-space-400 to-cosmic-400 rounded-full flex items-center justify-center">
                <span className="text-sm font-semibold text-white">
                  {user?.full_name?.charAt(0) || 'U'}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-white">{user?.full_name}</p>
                <p className="text-xs text-gray-400">Level {user?.progress?.current_level || 1}</p>
              </div>
            </div>
            
            {/* XP Progress */}
            <div className="mt-4">
              <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>XP Progress</span>
                <span>{user?.progress?.total_xp || 0} XP</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="progress-bar h-2 rounded-full"
                  style={{ width: `${Math.min(((user?.progress?.total_xp || 0) % 100), 100)}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setOpen(false)}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 group ${
                    active
                      ? 'bg-gradient-to-r from-space-500/20 to-cosmic-500/20 text-white border border-space-500/30 shadow-neon'
                      : 'text-gray-300 hover:text-white hover:bg-gray-800/50'
                  }`}
                >
                  <Icon className={`w-5 h-5 mr-3 ${active ? 'text-space-400' : 'text-gray-400 group-hover:text-gray-300'}`} />
                  {item.name}
                  {active && (
                    <motion.div
                      layoutId="activeTab"
                      className="ml-auto w-2 h-2 bg-space-400 rounded-full"
                    />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-800 space-y-2">
            <Link
              to="/app/settings"
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-300 rounded-lg hover:text-white hover:bg-gray-800/50 transition-colors"
            >
              <Cog6ToothIcon className="w-5 h-5 mr-3 text-gray-400" />
              Settings
            </Link>
            
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-2 text-sm font-medium text-gray-300 rounded-lg hover:text-white hover:bg-red-500/20 transition-colors"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5 mr-3 text-gray-400" />
              Sign Out
            </button>
          </div>
        </div>
      </motion.div>
    </>
  );
};

export default Sidebar;