import React from 'react';
import { motion } from 'framer-motion';
import { 
  Bars3Icon,
  BellIcon,
  MagnifyingGlassIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { useSocket } from '../contexts/SocketContext';

const Header = ({ setSidebarOpen }) => {
  const { user } = useAuth();
  const { connected, onlineUsers } = useSocket();

  return (
    <header className="glass-card sticky top-0 z-30 px-6 py-4 border-b border-gray-800/50">
      <div className="flex items-center justify-between">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 transition-colors"
          >
            <Bars3Icon className="w-6 h-6" />
          </button>

          {/* Search */}
          <div className="hidden md:block relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search lessons, topics..."
              className="form-input pl-10 pr-4 py-2 w-80 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-space-500"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="hidden md:flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-400' : 'bg-red-400'}`}></div>
            <span className="text-sm text-gray-400">
              {connected ? `${onlineUsers.length} online` : 'Offline'}
            </span>
          </div>

          {/* Notifications */}
          <button className="relative p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/50 transition-colors">
            <BellIcon className="w-6 h-6" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-cosmic-500 rounded-full"></span>
          </button>

          {/* User Menu */}
          <div className="flex items-center space-x-3">
            <div className="hidden md:block text-right">
              <p className="text-sm font-medium text-white">{user?.full_name}</p>
              <p className="text-xs text-gray-400">
                {user?.stats?.accuracy_rate ? `${Math.round(user.stats.accuracy_rate * 100)}% accuracy` : 'New learner'}
              </p>
            </div>
            
            <div className="w-10 h-10 bg-gradient-to-br from-space-400 to-cosmic-400 rounded-full flex items-center justify-center ai-avatar">
              <span className="text-sm font-semibold text-white">
                {user?.full_name?.charAt(0) || 'U'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;