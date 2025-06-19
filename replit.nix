# IDFS StarGuide - Complete Educational Platform

A comprehensive AI-powered educational platform with real-time collaboration, quiz battles, and advanced analytics.

## 🚀 Quick Start on Replit

### Automatic Setup
1. Fork this repl
2. Click the **Run** button
3. The platform will automatically install dependencies and start both frontend and backend
4. Visit the web view to access the application

### Manual Setup (if needed)

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python server.py
```

#### Frontend Setup
```bash
cd frontend
yarn install
yarn start
```

## 🔧 Configuration

### Environment Variables
The application requires the following API keys (add them in Replit's Secrets):

#### Required API Keys:
- `OPENAI_API_KEY` - OpenAI API key for GPT models
- `CLAUDE_API_KEY` - Anthropic Claude API key
- `GEMINI_API_KEY` - Google Gemini API key

#### Optional Configuration:
- `JWT_SECRET` - Custom JWT secret (auto-generated if not provided)
- `PASSWORD_SALT` - Custom password salt (auto-generated if not provided)
- `DB_NAME` - MongoDB database name (defaults to "starguide_db")

### Adding API Keys in Replit:
1. Click on "Secrets" tab in the left sidebar
2. Add each API key as a new secret:
   - Key: `OPENAI_API_KEY`
   - Value: `your_openai_api_key_here`
3. Repeat for `CLAUDE_API_KEY` and `GEMINI_API_KEY`
4. Restart the repl

## 🎯 Features

### ✅ Implemented Features:
- **Authentication System** - JWT-based with role management
- **AI Tutoring** - OpenAI GPT-4o, Claude Sonnet, Gemini 2.0
- **Real-time Study Rooms** - Socket.IO powered collaboration
- **Live Quiz Arena** - Synchronized quiz battles
- **Study Groups** - Public/private group management
- **Advanced Analytics** - ML-powered insights and predictions
- **Achievement System** - Gamification with badges and XP
- **Help Queue** - Student-teacher interaction system
- **Mobile Responsive** - Optimized for all devices
- **File Upload** - Image handling with base64 storage

### 🤖 AI Integration:
- **3 AI Providers**: OpenAI, Anthropic Claude, Google Gemini
- **Smart Conversations**: Context-aware responses
- **Quick Actions**: Pre-built prompts for common tasks
- **Usage Tracking**: Token usage monitoring

### 🎮 Gamification:
- **XP System**: Points for learning activities
- **Achievements**: Unlockable badges and rewards
- **Leaderboards**: Student rankings and progress
- **Streaks**: Daily learning streaks

## 🏗️ Architecture

### Frontend (React)
- **Framework**: React 19.0.0
- **Styling**: Tailwind CSS with custom animations
- **State Management**: React Context with performance optimization
- **Real-time**: Socket.IO client
- **Routing**: React Router v7

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Database**: MongoDB with Motor async driver
- **Real-time**: Socket.IO server
- **Authentication**: JWT with bcrypt hashing
- **AI Integration**: Multiple provider support

### Database Schema:
- **Users**: Authentication and profile data
- **Study Groups**: Group management and membership
- **Assessments**: Quiz and test data
- **Chat Messages**: Real-time conversation history
- **Achievements**: Gamification data

## 🌐 API Endpoints

### Authentication:
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### AI Features:
- `POST /api/ai/chat` - AI conversation
- `POST /api/ai/generate-questions` - AI question generation

### Study Features:
- `GET /api/groups` - Get study groups
- `POST /api/groups` - Create study group
- `GET /api/assessments` - Get assessments
- `POST /api/assessments` - Create assessment

### Real-time Events:
- `join_room` - Join study room
- `send_message` - Send chat message
- `quiz_answer` - Submit quiz answer

## 📱 Mobile Support

The platform is fully responsive and optimized for:
- **Desktop**: Full-featured experience
- **Tablet**: Optimized layouts
- **Mobile**: Touch-friendly interface with gesture support

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt with salt
- **Input Validation**: Pydantic models
- **CORS Protection**: Configured for security
- **Rate Limiting**: Built-in API protection

## 🚀 Performance Optimizations

- **React Memoization**: useCallback and useMemo
- **Lazy Loading**: Component code splitting
- **Caching**: Intelligent data caching
- **Compression**: Optimized bundle sizes
- **CDN Ready**: Static asset optimization

## 📊 Analytics & Insights

- **Learning Analytics**: Study pattern analysis
- **Progress Tracking**: Individual and group progress
- **AI Predictions**: ML-powered learning recommendations
- **Usage Statistics**: Platform usage metrics

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface
- **Smooth Animations**: CSS3 and JavaScript animations
- **Dark Theme**: Eye-friendly dark color scheme
- **Accessibility**: WCAG compliant design
- **Responsive**: Mobile-first approach

## 🛠️ Development

### File Structure:
```
/app/
├── backend/           # FastAPI backend
│   ├── server.py     # Main application
│   ├── requirements.txt
│   └── .env          # Environment variables
├── frontend/         # React frontend
│   ├── src/
│   │   ├── App.js    # Main component
│   │   ├── App.css   # Styles
│   │   └── components/
│   ├── package.json
│   └── .env          # Frontend environment
└── .replit          # Replit configuration
```

### Adding New Features:
1. **Backend**: Add endpoints in `backend/server.py`
2. **Frontend**: Add components in `frontend/src/components/`
3. **Styling**: Update `frontend/src/App.css`
4. **Real-time**: Add Socket.IO events in both frontend and backend

## 🔄 Updates & Maintenance

### Updating Dependencies:
```bash
# Backend
cd backend && pip install -r requirements.txt --upgrade

# Frontend  
cd frontend && yarn upgrade
```

### Database Updates:
The MongoDB schema is flexible and automatically adapts to new data structures.

## 📞 Support

For issues or questions:
1. Check the browser console for error messages
2. Verify all API keys are correctly set in Secrets
3. Ensure MongoDB is running (handled automatically in Replit)
4. Check that all dependencies are installed

## 🏆 Achievement System

Students earn XP and badges for:
- **Daily Login**: Consistency rewards
- **Quiz Completion**: Knowledge testing
- **AI Interactions**: Learning assistance usage
- **Study Group Participation**: Collaboration
- **Help Queue Assistance**: Peer teaching

## 🌟 Advanced Features

### Real-time Collaboration:
- **Live Chat**: Instant messaging in study rooms
- **Screen Sharing**: Virtual study sessions
- **Presence Indicators**: Online user tracking
- **Synchronized Quizzes**: Real-time quiz battles

### AI-Powered Learning:
- **Personalized Tutoring**: Adaptive AI responses
- **Question Generation**: Auto-created assessments
- **Study Recommendations**: ML-powered suggestions
- **Progress Predictions**: Learning outcome forecasts

---

**IDFS StarGuide** - Transforming education through AI and collaboration.