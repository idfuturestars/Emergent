import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  ChartBarIcon,
  TrophyIcon,
  ClockIcon,
  SparklesIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';

const Analytics = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [progressData, setProgressData] = useState([]);
  const [aiUsageData, setAiUsageData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      const [dashboardResponse, progressResponse, aiUsageResponse] = await Promise.all([
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/v1/analytics/dashboard`),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/v1/analytics/progress-chart?days=30`),
        axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/v1/analytics/ai-usage?days=30`)
      ]);
      
      setDashboardData(dashboardResponse.data);
      setProgressData(progressResponse.data.chart_data);
      setAiUsageData(aiUsageResponse.data);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 rounded-xl"
      >
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-space-500 to-cosmic-500 rounded-xl flex items-center justify-center">
            <ChartBarIcon className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Learning Analytics</h1>
            <p className="text-gray-300">Track your progress and performance</p>
          </div>
        </div>
      </motion.div>

      {/* Weekly Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          {
            name: 'Study Time',
            value: `${dashboardData?.weekly_stats?.total_study_time || 0}m`,
            icon: ClockIcon,
            color: 'from-blue-500 to-cyan-500',
            change: '+12% vs last week'
          },
          {
            name: 'Questions Answered',
            value: dashboardData?.weekly_stats?.questions_answered || 0,
            icon: AcademicCapIcon,
            color: 'from-green-500 to-emerald-500',
            change: '+8 vs last week'
          },
          {
            name: 'Accuracy Rate',
            value: `${Math.round((dashboardData?.weekly_stats?.accuracy_rate || 0) * 100)}%`,
            icon: TrophyIcon,
            color: 'from-yellow-500 to-orange-500',
            change: '+5% vs last week'
          },
          {
            name: 'AI Interactions',
            value: dashboardData?.weekly_stats?.ai_interactions || 0,
            icon: SparklesIcon,
            color: 'from-purple-500 to-pink-500',
            change: '+15 vs last week'
          }
        ].map((stat, index) => (
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

      {/* Progress Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card p-6 rounded-xl"
      >
        <h2 className="text-xl font-semibold text-white mb-6">30-Day Progress</h2>
        <div className="h-64 flex items-center justify-center">
          <p className="text-gray-400">Chart visualization would go here</p>
        </div>
      </motion.div>

      {/* Subject Performance & AI Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Subject Performance */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6 rounded-xl"
        >
          <h2 className="text-xl font-semibold text-white mb-6">Subject Performance</h2>
          <div className="space-y-4">
            {Object.entries(dashboardData?.subject_performance || {}).map(([subject, data]) => (
              <div key={subject} className="glass p-4 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white capitalize">{subject}</span>
                  <span className="text-sm text-gray-400">{data.sessions} sessions</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                  <div 
                    className="progress-bar h-2 rounded-full"
                    style={{ width: `${Math.round(data.accuracy * 100)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-sm text-gray-400">
                  <span>{Math.round(data.accuracy * 100)}% accuracy</span>
                  <span>{data.correct_answers}/{data.total_questions} correct</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* AI Usage */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-card p-6 rounded-xl"
        >
          <h2 className="text-xl font-semibold text-white mb-6">AI Usage Stats</h2>
          <div className="space-y-4">
            <div className="glass p-4 rounded-lg">
              <div className="text-center">
                <p className="text-3xl font-bold text-white mb-1">
                  {aiUsageData?.total_interactions || 0}
                </p>
                <p className="text-sm text-gray-400">Total AI Conversations</p>
              </div>
            </div>
            
            <div className="glass p-4 rounded-lg">
              <div className="text-center">
                <p className="text-3xl font-bold text-white mb-1">
                  {aiUsageData?.total_tokens_used || 0}
                </p>
                <p className="text-sm text-gray-400">Tokens Used</p>
              </div>
            </div>

            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-300">Model Usage</h3>
              {Object.entries(aiUsageData?.model_breakdown || {}).map(([model, data]) => (
                <div key={model} className="flex items-center justify-between py-2">
                  <span className="text-sm text-white capitalize">{model.replace('-', ' ')}</span>
                  <span className="text-sm text-gray-400">{data.interactions} uses</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Recent Achievements */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="glass-card p-6 rounded-xl"
      >
        <h2 className="text-xl font-semibold text-white mb-6">Recent Achievements</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {dashboardData?.recent_achievements?.map((achievement, index) => (
            <div key={achievement.id} className="glass p-4 rounded-lg flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center achievement-badge">
                <TrophyIcon className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">{achievement.achievement_id}</p>
                <p className="text-xs text-gray-400">+{achievement.xp_earned} XP</p>
              </div>
            </div>
          )) || (
            <div className="col-span-full text-center py-8">
              <TrophyIcon className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-400">No achievements yet</p>
              <p className="text-sm text-gray-500">Keep learning to unlock achievements!</p>
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default Analytics;