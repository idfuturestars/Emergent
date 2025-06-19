import React, { createContext, useContext, useEffect, useState } from 'react';
import io from 'socket.io-client';
import { useAuth } from './AuthContext';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      // Initialize socket connection
      const newSocket = io(process.env.REACT_APP_BACKEND_URL, {
        auth: {
          userId: user.id,
          username: user.username
        }
      });

      newSocket.on('connect', () => {
        console.log('Connected to server');
        setConnected(true);
      });

      newSocket.on('disconnect', () => {
        console.log('Disconnected from server');
        setConnected(false);
      });

      newSocket.on('users_online', (users) => {
        setOnlineUsers(users);
      });

      newSocket.on('user_joined', (userData) => {
        setOnlineUsers(prev => [...prev, userData]);
      });

      newSocket.on('user_left', (userId) => {
        setOnlineUsers(prev => prev.filter(u => u.id !== userId));
      });

      setSocket(newSocket);

      return () => {
        newSocket.close();
        setSocket(null);
        setConnected(false);
      };
    }
  }, [user]);

  // Study Groups Events
  const joinStudyGroup = (groupId) => {
    if (socket) {
      socket.emit('join_study_group', { groupId });
    }
  };

  const leaveStudyGroup = (groupId) => {
    if (socket) {
      socket.emit('leave_study_group', { groupId });
    }
  };

  const sendGroupMessage = (groupId, message) => {
    if (socket) {
      socket.emit('group_message', { groupId, message });
    }
  };

  // Quiz Events
  const joinQuizRoom = (roomId) => {
    if (socket) {
      socket.emit('join_quiz_room', { roomId });
    }
  };

  const leaveQuizRoom = (roomId) => {
    if (socket) {
      socket.emit('leave_quiz_room', { roomId });
    }
  };

  const submitQuizAnswer = (roomId, questionId, answer) => {
    if (socket) {
      socket.emit('submit_quiz_answer', { roomId, questionId, answer });
    }
  };

  // Notifications
  const sendNotification = (userId, notification) => {
    if (socket) {
      socket.emit('send_notification', { userId, notification });
    }
  };

  const value = {
    socket,
    connected,
    onlineUsers,
    joinStudyGroup,
    leaveStudyGroup,
    sendGroupMessage,
    joinQuizRoom,
    leaveQuizRoom,
    submitQuizAnswer,
    sendNotification
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};