# StarGuide Platform - Replit Setup Guide

## 📦 Project Package Location

**Current Package**: `/app/starguide-complete.tar.gz` (272 KB)

## 🗂️ Complete Project Structure

```
starguide/
├── backend/                          # FastAPI Backend
│   ├── server.py                     # Main FastAPI application with all endpoints
│   ├── adaptive_engine.py            # Adaptive assessment engine (K-PhD+)
│   ├── question_bank_seeder.py       # Question database seeder
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Backend environment variables
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── pages/                    # All feature pages
│   │   │   ├── Dashboard.js          # Main dashboard
│   │   │   ├── SkillScan.js          # Standard assessment
│   │   │   ├── AdaptiveSkillScan.js  # NEW: K-PhD+ adaptive assessment
│   │   │   ├── StarMentor.js         # AI tutoring system
│   │   │   ├── GalaxyQuests.js       # Learning adventures
│   │   │   ├── LearningPods.js       # Study groups
│   │   │   ├── Trajectory.js         # Progress analytics
│   │   │   ├── StarRankings.js       # Leaderboards
│   │   │   ├── StarBadges.js         # Achievement system
│   │   │   ├── SOSStation.js         # Help request system
│   │   │   ├── MissionIntel.js       # Knowledge base
│   │   │   ├── Login.js              # Authentication
│   │   │   └── Register.js           # User registration
│   │   ├── components/               # Reusable components
│   │   │   ├── Layout.js             # Main layout with navigation
│   │   │   ├── StarLogo.js           # StarGuide logo component
│   │   │   └── LoadingScreen.js      # Loading states
│   │   ├── contexts/
│   │   │   └── AuthContext.js        # Authentication context
│   │   ├── App.js                    # Main React app
│   │   ├── index.js                  # React entry point
│   │   ├── App.css                   # Application styles
│   │   └── index.css                 # Global styles (StarGuide theme)
│   ├── public/                       # Static assets
│   ├── package.json                  # Frontend dependencies
│   ├── tailwind.config.js            # Tailwind CSS config
│   ├── postcss.config.js             # PostCSS config
│   └── .env                          # Frontend environment variables
├── test_result.md                    # Complete testing documentation
├── README.md                         # Project documentation
└── backend_test.py                   # Backend testing script
```

## 🚀 Replit Setup Instructions

### Step 1: Download Project Package
```bash
# The complete project is packaged in:
/app/starguide-complete.tar.gz
```

### Step 2: Create New Replit Project
1. Go to https://replit.com
2. Create new Repl → "Import from GitHub" or "Upload"
3. Upload the `starguide-complete.tar.gz` file
4. Extract: `tar -xzf starguide-complete.tar.gz`

### Step 3: Backend Setup (Python)
```bash
cd backend
pip install -r requirements.txt
```

**Backend Environment Variables (.env)**:
```env
MONGO_URL="mongodb://localhost:27017"
DB_NAME="starguide_db" 
OPENAI_API_KEY="your_openai_api_key_here"
JWT_SECRET="starguide-secret-key-2025"
REDIS_URL="redis://localhost:6379"
```

### Step 4: Frontend Setup (Node.js)
```bash
cd frontend
yarn install
# or
npm install
```

**Frontend Environment Variables (.env)**:
```env
REACT_APP_BACKEND_URL="http://localhost:8001"
```

### Step 5: Database Setup
```bash
# Install MongoDB (if not available in Replit)
cd backend
python question_bank_seeder.py  # Seeds K-PhD+ question bank
```

### Step 6: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
# or
npm start
```

## 🔧 Replit Configuration

### replit.nix (if needed)
```nix
{ pkgs }: {
  deps = [
    pkgs.nodejs-18_x
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.yarn
    pkgs.mongodb
  ];
}
```

### .replit
```toml
modules = ["nodejs-18", "python-3.10"]

[nix]
channel = "stable-23_05"

[[ports]]
localPort = 3000
externalPort = 80

[[ports]]
localPort = 8001
externalPort = 8001

[deployment]
run = ["bash", "-c", "cd backend && python server.py & cd frontend && yarn start"]
build = ["bash", "-c", "cd backend && pip install -r requirements.txt && cd ../frontend && yarn install"]
```

## 🎯 Key Features Available

### ✅ Complete Adaptive Assessment System
- **K-PhD+ Questions**: From kindergarten through doctoral level
- **Think-Aloud Mode**: AI analyzes reasoning process  
- **AI Assistance Tracking**: Monitors help usage with transparency
- **Real-time Adaptation**: Questions adjust based on performance
- **Advanced Analytics**: Detailed learning insights

### ✅ Full Educational Platform
- **10 Core Features**: All StarGuide features implemented
- **Authentication**: Role-based access (Student/Teacher/Admin)
- **AI Tutoring**: OpenAI GPT-4 integration
- **Study Groups**: Collaborative learning
- **Gamification**: XP, levels, badges, leaderboards

### ✅ Modern Tech Stack
- **Backend**: FastAPI + MongoDB + OpenAI API
- **Frontend**: React + Tailwind CSS + Axios
- **Theme**: Exact black (#0a0a0a) StarGuide specification

## 🔑 Demo Accounts

```
Student: student@starguide.com / demo123
Teacher: teacher@starguide.com / demo123
Admin: admin@starguide.com / demo123
```

## 🎮 Testing the Adaptive Assessment

1. Login with demo account
2. Navigate to "SkillScan™"
3. Choose "Adaptive SkillScan™" (yellow star icon)
4. Configure assessment (Mathematics, Grade 8, Diagnostic)
5. Enable Think-Aloud mode and AI tracking
6. Experience questions that adapt to your skill level
7. View comprehensive analytics and recommendations

## 🏆 Production Ready Features

- **Mobile Responsive**: Works on all devices
- **Error Handling**: Graceful error management
- **Performance Optimized**: Fast loading and smooth UX
- **Scalable Architecture**: Ready for enterprise deployment
- **Security**: JWT authentication, input validation
- **Testing**: Comprehensive frontend and backend testing completed

## 🔧 Troubleshooting

### Common Issues:
1. **Authentication Error**: Update bcrypt to version 4.0.1
2. **CORS Issues**: Check REACT_APP_BACKEND_URL in frontend/.env
3. **MongoDB Connection**: Ensure MongoDB is running on port 27017
4. **OpenAI API**: Add valid API key to backend/.env

### Dependencies:
- **Python 3.8+** for backend
- **Node.js 16+** for frontend  
- **MongoDB** for database
- **OpenAI API Key** for AI features

## 🎯 Next Steps After Setup

1. **Test Adaptive Assessment**: Experience the K-PhD+ system
2. **Customize Content**: Add more questions for specific subjects
3. **Configure Integrations**: Set up additional AI providers
4. **Deploy Production**: Configure for live deployment
5. **Scale Features**: Add more from the 6-phase roadmap

Your StarGuide platform is now ready for deployment on Replit with the complete adaptive assessment system!