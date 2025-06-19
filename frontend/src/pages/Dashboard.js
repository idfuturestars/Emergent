import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  TrophyIcon,
  FireIcon,
  ChartBarIcon,
  UserGroupIcon,
  SparklesIcon,
  PlayIcon,
  ClockIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dailyChallenge, setDailyChallenge] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [dashboardResponse, challengeResponse] = await Promise.all([
          axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/v1/analytics/dashboard`),
          axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/v1/learning/daily-challenge`)
        ]);
        
        setDashboardData(dashboardResponse.data);
        setDailyChallenge(challengeResponse.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  const stats = [
    {
      name: 'Current Level',
      value: user?.progress?.current_level || 1,
      icon: TrophyIcon,
      color: 'from-yellow-400 to-orange-500',
      change: '+2 this week'
    },
    {
      name: 'Learning Streak',
      value: `${user?.progress?.streak_days || 0} days`,
      icon: FireIcon,
      color: 'from-red-400 to-pink-500',
      change: user?.progress?.streak_days > 0 ? 'Keep it up!' : 'Start today!'
    },
    {
      name: 'Accuracy Rate',
      value: `${Math.round((user?.stats?.accuracy_rate || 0) * 100)}%`,
      icon: ChartBarIcon,
      color: 'from-green-400 to-blue-500',
      change: '+5% this week'
    },
    {
      name: 'Total XP',
      value: user?.progress?.total_xp || 0,
      icon: SparklesIcon,
      color: 'from-purple-400 to-pink-500',
      change: '+250 this week'
    }
  ];

  const quickActions = [
    {
      name: 'AI Tutor Chat',
      description: 'Get instant help with any question',
      icon: SparklesIcon,
      href: '/app/ai-tutor',
      color: 'from-space-500 to-cosmic-500'
    },
    {
      name: 'Join Study Group',
      description: 'Learn together with peers',
      icon: UserGroupIcon,
      href: '/app/study-groups',
      color: 'from-cosmic-500 to-stellar-500'
    },
    {
      name: 'Take Quiz',
      description: 'Test your knowledge',
      icon: PlayIcon,
      href: '/app/quiz-arena',
      color: 'from-stellar-500 to-space-500'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8 rounded-2xl"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Welcome back, {user?.full_name?.split(' ')[0] || 'Learner'}! 🚀
            </h1>
            <p className="text-gray-300">
              Ready to continue your learning journey? Let's achieve great things today.
            </p>
          </div>
          <div className="hidden md:block">
            <div className="w-24 h-24 bg-gradient-to-br from-space-500 to-cosmic-500 rounded-2xl flex items-center justify-center ai-avatar">
              <SparklesIcon className="w-12 h-12 text-white" />
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>Level {user?.progress?.current_level || 1} Progress</span>
            <span>{user?.progress?.total_xp || 0} XP</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(((user?.progress?.total_xp || 0) % 100), 100)}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className="progress-bar h-3 rounded-full"
            ></motion.div>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6 rounded-xl hover:shadow-neon transition-all duration-300"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400 mb-1">{stat.name}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className="text-xs text-green-400 mt-1">{stat.change}</p>
              </div>
              <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-lg flex items-center justify-center`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Daily Challenge */}
      {dailyChallenge && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6 rounded-xl border border-yellow-500/30"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
                <ClockIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Daily Challenge</h3>
                <p className="text-sm text-gray-400">{dailyChallenge.title}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-yellow-400 font-medium">+{dailyChallenge.xp_reward} XP</p>
              <p className="text-xs text-gray-400">{dailyChallenge.time_limit_minutes} minutes</p>
            </div>
          </div>
          
          <p className="text-gray-300 mb-4">{dailyChallenge.description}</p>
          
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-400">
              {dailyChallenge.total_participants} participants • {Math.round(dailyChallenge.completion_rate * 100)}% completion rate
            </div>
            <Link
              to="/app/daily-challenge"
              className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-2 rounded-lg hover:shadow-neon transition-all duration-300 neon-button"
            >
              {dailyChallenge.has_completed ? 'View Results' : 'Start Challenge'}
            </Link>
          </div>
        </motion.div>
      )}

      {/* Quick Actions & Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4">Quick Actions</h2>
          <div className="space-y-4">
            {quickActions.map((action, index) => (
              <Link
                key={action.name}
                to={action.href}
                className="glass-card p-4 rounded-xl hover:shadow-neon transition-all duration-300 block group"
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 bg-gradient-to-br ${action.color} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                    <action.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">{action.name}</h3>
                    <p className="text-sm text-gray-400">{action.description}</p>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {dashboardData?.recent_sessions?.slice(0, 5).map((session, index) => (
              <div key={session.id} className="glass-card p-4 rounded-xl">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-space-400 to-cosmic-400 rounded-lg flex items-center justify-center">
                      <AcademicCapIcon className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">
                        {session.subject} - {session.type}
                      </p>
                      <p className="text-xs text-gray-400">
                        {Math.round(session.accuracy * 100)}% accuracy • {session.xp_earned} XP
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-gray-400">
                    {new Date(session.started_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            )) || (
              <div className="glass-card p-8 rounded-xl text-center">
                <AcademicCapIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-400">No recent activity</p>
                <p className="text-sm text-gray-500 mt-2">Start learning to see your progress here!</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;