import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  TrophyIcon,
  PlusIcon,
  PlayIcon,
  UserIcon,
  ClockIcon,
  FireIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';

const QuizArena = () => {
  const [activeRooms, setActiveRooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchActiveRooms();
    // Refresh every 10 seconds
    const interval = setInterval(fetchActiveRooms, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchActiveRooms = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/v1/quizzes/active-rooms`);
      setActiveRooms(response.data.active_rooms);
    } catch (error) {
      console.error('Failed to fetch active rooms:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card p-6 rounded-xl"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl flex items-center justify-center">
              <TrophyIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Quiz Arena</h1>
              <p className="text-gray-300">Battle in live quiz competitions</p>
            </div>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-3 rounded-lg hover:shadow-neon transition-all duration-300 neon-button flex items-center space-x-2"
          >
            <PlusIcon className="w-5 h-5" />
            <span>Create Room</span>
          </button>
        </div>
      </motion.div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card p-6 rounded-xl"
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <PlayIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{activeRooms.length}</p>
              <p className="text-sm text-gray-400">Active Rooms</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card p-6 rounded-xl"
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
              <UserIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">
                {activeRooms.reduce((sum, room) => sum + room.current_participants, 0)}
              </p>
              <p className="text-sm text-gray-400">Players Online</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glass-card p-6 rounded-xl"
        >
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-lg flex items-center justify-center">
              <FireIcon className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">Hot</p>
              <p className="text-sm text-gray-400">Battles Today</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Active Rooms */}
      <div className="glass-card p-6 rounded-xl">
        <h2 className="text-xl font-semibold text-white mb-6">Join a Live Quiz Battle</h2>
        
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : activeRooms.length === 0 ? (
          <div className="text-center py-12">
            <TrophyIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-white mb-2">No active quiz rooms</h3>
            <p className="text-gray-400 mb-6">
              Be the first to create a quiz room and challenge others!
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white px-6 py-3 rounded-lg hover:shadow-neon transition-all duration-300 neon-button"
            >
              Create First Room
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeRooms.map((room, index) => (
              <motion.div
                key={room.room_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass border border-gray-600 hover:border-yellow-400 p-6 rounded-xl transition-all duration-300 hover:shadow-neon"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-white mb-1">{room.title}</h3>
                    <p className="text-sm text-gray-400">{room.subject}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    room.difficulty === 'beginner' ? 'bg-green-500/20 text-green-400' :
                    room.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {room.difficulty}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm text-gray-400 mb-4">
                  <div className="flex items-center space-x-1">
                    <UserIcon className="w-4 h-4" />
                    <span>{room.current_participants}/{room.max_participants}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ClockIcon className="w-4 h-4" />
                    <span>{new Date(room.created_at).toLocaleTimeString()}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between mb-4">
                  <div className="text-xs text-gray-400">
                    Created by <span className="text-white">{room.creator_name}</span>
                  </div>
                  <div className="text-xs font-medium text-yellow-400">
                    Room: {room.room_code}
                  </div>
                </div>

                <button className="w-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white py-2 px-4 rounded-lg font-medium hover:shadow-neon transition-all duration-300 neon-button">
                  Join Battle
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuizArena;