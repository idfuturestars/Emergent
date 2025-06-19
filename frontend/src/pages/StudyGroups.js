import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  UserGroupIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  UserIcon,
  ClockIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline';
import axios from 'axios';
import LoadingSpinner from '../components/LoadingSpinner';

const StudyGroups = () => {
  const [activeTab, setActiveTab] = useState('my-groups');
  const [groups, setGroups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchGroups();
  }, [activeTab]);

  const fetchGroups = async () => {
    setLoading(true);
    try {
      const endpoint = activeTab === 'my-groups' 
        ? '/api/v1/groups/my-groups'
        : '/api/v1/groups/discover';
      
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}${endpoint}`);
      setGroups(response.data);
    } catch (error) {
      console.error('Failed to fetch groups:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredGroups = groups.filter(group =>
    group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    group.subject.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            <div className="w-12 h-12 bg-gradient-to-br from-space-500 to-cosmic-500 rounded-xl flex items-center justify-center">
              <UserGroupIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Study Groups</h1>
              <p className="text-gray-300">Learn together with your peers</p>
            </div>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-gradient-to-r from-space-500 to-cosmic-500 text-white px-6 py-3 rounded-lg hover:shadow-neon transition-all duration-300 neon-button flex items-center space-x-2"
          >
            <PlusIcon className="w-5 h-5" />
            <span>Create Group</span>
          </button>
        </div>
      </motion.div>

      {/* Tabs and Search */}
      <div className="glass-card p-6 rounded-xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          {/* Tabs */}
          <div className="flex space-x-1 bg-gray-800/50 rounded-lg p-1">
            {[
              { id: 'my-groups', label: 'My Groups' },
              { id: 'discover', label: 'Discover' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-6 py-2 rounded-md font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-space-500 to-cosmic-500 text-white shadow-neon'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search groups..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input pl-10 pr-4 py-2 w-64 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-space-500"
            />
          </div>
        </div>
      </div>

      {/* Groups Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full flex items-center justify-center py-12">
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredGroups.length === 0 ? (
          <div className="col-span-full glass-card p-12 rounded-xl text-center">
            <UserGroupIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-white mb-2">
              {activeTab === 'my-groups' ? 'No groups joined yet' : 'No groups found'}
            </h3>
            <p className="text-gray-400 mb-6">
              {activeTab === 'my-groups' 
                ? 'Create or join a study group to start collaborating with others.'
                : 'Try adjusting your search terms or create a new group.'
              }
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-space-500 to-cosmic-500 text-white px-6 py-3 rounded-lg hover:shadow-neon transition-all duration-300 neon-button"
            >
              Create Your First Group
            </button>
          </div>
        ) : (
          filteredGroups.map((group, index) => (
            <motion.div
              key={group.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-card p-6 rounded-xl hover:shadow-neon transition-all duration-300 group cursor-pointer"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-stellar-400 to-cosmic-400 rounded-lg flex items-center justify-center">
                    <AcademicCapIcon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white group-hover:text-space-400 transition-colors">
                      {group.name}
                    </h3>
                    <p className="text-sm text-gray-400">{group.subject}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  group.group_type === 'public' 
                    ? 'bg-green-500/20 text-green-400' 
                    : 'bg-yellow-500/20 text-yellow-400'
                }`}>
                  {group.group_type}
                </span>
              </div>

              <p className="text-gray-300 text-sm mb-4 line-clamp-2">
                {group.description || 'No description available.'}
              </p>

              <div className="flex items-center justify-between text-sm text-gray-400 mb-4">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-1">
                    <UserIcon className="w-4 h-4" />
                    <span>{group.member_count}/{group.max_members}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <ClockIcon className="w-4 h-4" />
                    <span>{new Date(group.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              <div className="flex space-x-2">
                {group.is_member ? (
                  <button className="flex-1 bg-gradient-to-r from-green-500 to-emerald-500 text-white py-2 px-4 rounded-lg font-medium">
                    Enter Group
                  </button>
                ) : (
                  <button className="flex-1 bg-gradient-to-r from-space-500 to-cosmic-500 text-white py-2 px-4 rounded-lg font-medium hover:shadow-neon transition-all duration-300 neon-button">
                    Join Group
                  </button>
                )}
              </div>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default StudyGroups;