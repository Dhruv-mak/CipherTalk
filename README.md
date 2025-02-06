# CipherTalk - Real-Time Secure Chat Application 🚀

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Socket.io](https://img.shields.io/badge/Socket.io-010101?style=for-the-badge&logo=socket.io&logoColor=white)](https://socket.io/)

CipherTalk is a modern, secure, and feature-rich chat application built with a focus on real-time communication and user experience. It leverages the power of FastAPI, React, and WebSocket technology to deliver seamless messaging capabilities.

## 🌟 Features

### Authentication & Security
- JWT-based authentication with access and refresh tokens
- Secure password hashing using bcrypt
- Email verification system
- Password reset functionality
- HTTP-only cookie implementation for enhanced security

### Chat Functionality
- Real-time messaging using Socket.IO
- One-on-one private conversations
- Group chat support with admin controls
- File sharing capabilities
- Typing indicators
- Read receipts
- Message history

### User Experience
- Modern, responsive UI built with React and TailwindCSS
- Real-time updates and notifications
- Intuitive group management
- User search functionality
- Avatar support
- Clean and intuitive interface

### Monitoring & Performance
- Grafana dashboard integration
- MongoDB performance monitoring
- Real-time database metrics
- System health monitoring
- Resource usage tracking

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **MongoDB**: NoSQL database for flexible data storage
- **Socket.IO**: Real-time bidirectional event-based communication
- **JWT**: Token-based authentication
- **Bcrypt**: Password hashing
- **Mailtrap**: Email testing service

### Frontend
- **React**: UI library for building user interfaces
- **TailwindCSS**: Utility-first CSS framework
- **Socket.IO Client**: Real-time communication
- **React Query**: Server state management
- **React Router**: Navigation management

### Monitoring
- **Grafana**: Analytics and monitoring platform
- **MongoDB Metrics**: Database performance tracking
- **System Metrics**: Resource utilization monitoring

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 14+
- MongoDB
- Grafana

### Environment Variables
```env
ACCESS_TOKEN_SECRET=your_access_token_secret
REFRESH_TOKEN_SECRET=your_refresh_token_secret
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRY=7
MONGODB_URL=your_mongodb_url
MAILTRAP_SMTP_USER=your_mailtrap_user
MAILTRAP_SMTP_PASS=your_mailtrap_password
```

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/ciphertalk.git
cd ciphertalk
```

2. Set up the backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

3. Set up the frontend
```bash
cd frontend
npm install
npm run dev
```

4. Set up Grafana monitoring
```bash
docker-compose up -d
```

## 📊 Monitoring Dashboard

The Grafana dashboard provides real-time insights into:
- MongoDB read/write operations
- Query performance metrics
- Connection pool status
- System resource utilization
- Error rates and types
- User activity patterns

## 🔒 Security Features

- **JWT Authentication**: Secure token-based user authentication
- **HTTP-Only Cookies**: Prevention of XSS attacks
- **Password Hashing**: Secure storage of user credentials
- **Email Verification**: User validation through email
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: Prevention of injection attacks

## 🔄 API Documentation

The API documentation is automatically generated using FastAPI's built-in Swagger UI and can be accessed at `/docs` when running the server.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For any queries or support, please reach out to [dhruv.makwana5004@gmail.com](mailto:dhruv.makwana5004@gmail.com)