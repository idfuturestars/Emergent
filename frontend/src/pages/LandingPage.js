import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  SparklesIcon, 
  AcademicCapIcon, 
  ChartBarIcon, 
  UserGroupIcon,
  BeakerIcon,
  RocketLaunchIcon
} from '@heroicons/react/24/outline';

const LandingPage = () => {
  const features = [
    {
      icon: SparklesIcon,
      title: 'Multi-AI Tutor',
      description: 'Learn with OpenAI GPT-4, Claude 3, and Gemini Pro - choose the AI that works best for you.',
      gradient: 'from-space-500 to-space-700'
    },
    {
      icon: AcademicCapIcon,
      title: 'Adaptive Learning',
      description: 'Personalized assessments that adapt to your skill level and learning pace.',
      gradient: 'from-cosmic-500 to-cosmic-700'
    },
    {
      icon: ChartBarIcon,
      title: 'Progress Analytics',
      description: 'Track your learning journey with detailed analytics and performance insights.',
      gradient: 'from-stellar-500 to-stellar-700'
    },
    {
      icon: UserGroupIcon,
      title: 'Study Groups',
      description: 'Collaborate with peers in real-time study rooms and group learning sessions.',
      gradient: 'from-space-600 to-cosmic-600'
    },
    {
      icon: BeakerIcon,
      title: 'Quiz Arena',
      description: 'Battle in live quiz competitions and test your knowledge against others.',
      gradient: 'from-cosmic-600 to-stellar-600'
    },
    {
      icon: RocketLaunchIcon,
      title: 'Gamified Learning',
      description: 'Earn XP, unlock achievements, and level up as you master new concepts.',
      gradient: 'from-stellar-600 to-space-600'
    }
  ];

  return (
    <div className="min-h-screen bg-space-gradient relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 constellation-bg opacity-60"></div>
      
      {/* Floating Elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-space-500/20 rounded-full blur-xl float-animation"></div>
      <div className="absolute top-40 right-20 w-24 h-24 bg-cosmic-500/20 rounded-full blur-xl float-animation"></div>
      <div className="absolute bottom-20 left-1/4 w-40 h-40 bg-stellar-500/20 rounded-full blur-xl float-animation"></div>

      {/* Navigation */}
      <nav className="relative z-10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-3"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-space-500 to-cosmic-500 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white glow-text">StarGuide</h1>
          </motion.div>

          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-4"
          >
            <Link 
              to="/login" 
              className="text-gray-300 hover:text-white transition-colors"
            >
              Sign In
            </Link>
            <Link 
              to="/register" 
              className="bg-gradient-to-r from-space-500 to-cosmic-500 text-white px-6 py-2 rounded-lg hover:shadow-neon transition-all duration-300 neon-button"
            >
              Get Started
            </Link>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 text-shadow">
              Learn with{' '}
              <span className="bg-gradient-to-r from-space-400 via-cosmic-400 to-stellar-400 bg-clip-text text-transparent">
                AI-Powered
              </span>
              {' '}Precision
            </h1>
            
            <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Master any subject with our revolutionary AI tutoring platform. Featuring multiple AI models, 
              adaptive learning, and real-time collaboration - your journey to academic excellence starts here.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link 
                to="/register" 
                className="bg-gradient-to-r from-space-500 to-cosmic-500 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:shadow-neon transition-all duration-300 neon-button transform hover:scale-105"
              >
                Start Learning Free
              </Link>
              <button className="text-white border border-gray-600 px-8 py-4 rounded-xl text-lg font-semibold hover:border-space-400 transition-all duration-300 glass">
                Watch Demo
              </button>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mt-20 grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-3xl mx-auto"
          >
            <div className="glass-card p-6 rounded-xl">
              <div className="text-3xl font-bold text-space-400 mb-2">10K+</div>
              <div className="text-gray-300">Active Learners</div>
            </div>
            <div className="glass-card p-6 rounded-xl">
              <div className="text-3xl font-bold text-cosmic-400 mb-2">3</div>
              <div className="text-gray-300">AI Models</div>
            </div>
            <div className="glass-card p-6 rounded-xl">
              <div className="text-3xl font-bold text-stellar-400 mb-2">98%</div>
              <div className="text-gray-300">Success Rate</div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-10 px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Everything You Need to{' '}
              <span className="bg-gradient-to-r from-space-400 to-cosmic-400 bg-clip-text text-transparent">
                Excel
              </span>
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              Our comprehensive platform combines cutting-edge AI technology with proven learning methodologies.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                className="glass-card p-8 rounded-xl hover:shadow-neon transition-all duration-300 group"
              >
                <div className={`w-12 h-12 bg-gradient-to-br ${feature.gradient} rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white mb-4">{feature.title}</h3>
                <p className="text-gray-300 leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="relative z-10 px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="glass p-12 rounded-2xl"
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready to Transform Your Learning?
            </h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of students already achieving their academic goals with StarGuide.
            </p>
            <Link 
              to="/register" 
              className="inline-block bg-gradient-to-r from-space-500 to-cosmic-500 text-white px-10 py-4 rounded-xl text-lg font-semibold hover:shadow-neon transition-all duration-300 neon-button transform hover:scale-105"
            >
              Start Your Journey Today
            </Link>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-8 border-t border-gray-800">
        <div className="max-w-7xl mx-auto text-center text-gray-400">
          <p>&copy; 2024 StarGuide AI Mentor. Empowering minds across the galaxy.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;