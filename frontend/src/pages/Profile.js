import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  UserCircleIcon,
  CogIcon,
  TrophyIcon,
  SparklesIcon,
  AcademicCapIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    bio: user?.bio || '',
    school: user?.school || '',
    grade_level: user?.grade_level || ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSave = async () => {
    // TODO: Implement profile update API call
    setIsEditing(false);
  };

  const achievements = [
    { name: 'First Steps', description: 'Completed first lesson', earned: true, rarity: 'common' },
    { name: 'AI Whisperer', description: 'Had 10 AI conversations', earned: true, rarity: 'rare' },
    { name: 'Knowledge Seeker', description: 'Answered 100 questions', earned: false, rarity: 'epic' },
    { name: 'Master Learner', description: 'Reached level 10', earned: false, rarity: 'legendary' }
  ];

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-8 rounded-xl"
      >
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-6">
            <div className="w-24 h-24 bg-gradient-to-br from-space-400 to-cosmic-400 rounded-2xl flex items-center justify-center ai-avatar">
              <span className="text-3xl font-bold text-white">
                {user?.full_name?.charAt(0) || 'U'}
              </span>
            </div>
            
            <div>
              {isEditing ? (
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="form-input text-2xl font-bold text-white bg-transparent border-b border-gray-600 focus:border-space-400 focus:outline-none"
                />
              ) : (
                <h1 className="text-3xl font-bold text-white">{user?.full_name}</h1>
              )}
              
              <p className="text-gray-300 mt-1">
                Level {user?.progress?.current_level || 1} • {user?.role || 'Student'}
              </p>
              
              {isEditing ? (
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleChange}
                  placeholder="Tell us about yourself..."
                  className="form-input mt-2 w-full text-gray-300 bg-transparent border border-gray-600 rounded-lg focus:border-space-400 focus:outline-none"
                  rows="2"
                />
              ) : (
                <p className="text-gray-300 mt-2">
                  {user?.bio || 'No bio available'}
                </p>
              )}
            </div>
          </div>

          <button
            onClick={() => isEditing ? handleSave() : setIsEditing(true)}
            className="bg-gradient-to-r from-space-500 to-cosmic-500 text-white px-6 py-2 rounded-lg hover:shadow-neon transition-all duration-300 neon-button flex items-center space-x-2"
          >
            <PencilIcon className="w-4 h-4" />
            <span>{isEditing ? 'Save' : 'Edit'}</span>
          </button>
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
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          {
            name: 'Total XP',
            value: user?.progress?.total_xp || 0,
            icon: SparklesIcon,
            color: 'from-purple-500 to-pink-500'
          },
          {
            name: 'Current Level',
            value: user?.progress?.current_level || 1,
            icon: TrophyIcon,
            color: 'from-yellow-500 to-orange-500'
          },
          {
            name: 'Streak Days',
            value: user?.progress?.streak_days || 0,
            icon: TrophyIcon,
            color: 'from-red-500 to-pink-500'
          },
          {
            name: 'Accuracy',
            value: `${Math.round((user?.stats?.accuracy_rate || 0) * 100)}%`,
            icon: AcademicCapIcon,
            color: 'from-green-500 to-emerald-500'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card p-6 rounded-xl text-center"
          >
            <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-lg flex items-center justify-center mx-auto mb-4`}>
              <stat.icon className="w-6 h-6 text-white" />
            </div>
            <p className="text-2xl font-bold text-white">{stat.value}</p>
            <p className="text-sm text-gray-400">{stat.name}</p>
          </motion.div>
        ))}
      </div>

      {/* Profile Details & Achievements */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Details */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card p-6 rounded-xl"
        >
          <h2 className="text-xl font-semibold text-white mb-6">Profile Details</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Email</label>
              <p className="text-white">{user?.email}</p>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Username</label>
              <p className="text-white">{user?.username}</p>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">School</label>
              {isEditing ? (
                <input
                  type="text"
                  name="school"
                  value={formData.school}
                  onChange={handleChange}
                  className="form-input w-full text-white bg-transparent border border-gray-600 rounded-lg focus:border-space-400 focus:outline-none"
                />
              ) : (
                <p className="text-white">{user?.school || 'Not specified'}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Grade Level</label>
              {isEditing ? (
                <select
                  name="grade_level"
                  value={formData.grade_level}
                  onChange={handleChange}
                  className="form-input w-full text-white bg-gray-800 border border-gray-600 rounded-lg focus:border-space-400 focus:outline-none"
                >
                  <option value="">Select Grade</option>
                  <option value="K-2">K-2</option>
                  <option value="3-5">3-5</option>
                  <option value="6-8">6-8</option>
                  <option value="9-12">9-12</option>
                  <option value="college">College</option>
                  <option value="adult">Adult Learning</option>
                </select>
              ) : (
                <p className="text-white">{user?.grade_level || 'Not specified'}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Member Since</label>
              <p className="text-white">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Achievements */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card p-6 rounded-xl"
        >
          <h2 className="text-xl font-semibold text-white mb-6">Achievements</h2>
          <div className="space-y-3">
            {achievements.map((achievement, index) => (
              <div
                key={achievement.name}
                className={`glass p-4 rounded-lg flex items-center space-x-4 ${
                  achievement.earned ? 'border border-yellow-500/30' : 'opacity-50'
                }`}
              >
                <div className={`w-12 h-12 rounded-lg flex items-center justify-center achievement-badge ${achievement.rarity}`}>
                  <TrophyIcon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white">{achievement.name}</h3>
                  <p className="text-sm text-gray-400">{achievement.description}</p>
                </div>
                {achievement.earned && (
                  <div className="text-xs text-yellow-400 font-medium">
                    Earned
                  </div>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Profile;