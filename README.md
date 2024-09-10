# CipherTalk

Snapgram is a dynamic chat application designed to facilitate user communication through a real-time chat system. This application consists of a robust backend developed with FastAPI and a responsive frontend created using Next.js with TypeScript and Vite.

## Table of Contents

- [CipherTalk](#CipherTalk)
  - [Table of Contents](#table-of-contents)
  - [Screenshots](#screenshots)
  - [Features](#features)
    - [Authentication](#authentication)
    - [Chat Functionalities](#chat-functionalities)
      - [One-on-One Chat](#one-on-one-chat)
      - [Group Chat](#group-chat)
      - [Real-Time Notifications](#real-time-notifications)
    - [Pages](#pages)
      - [Login Page](#login-page)
      - [Chat Page](#chat-page)
      - [Profile Settings](#profile-settings)
  - [Built with](#built-with)
  - [Licence](#licence)

## Screenshots

Home page
![Home page](./public/previews/home.png)

Login page
![Login page](./public/previews/login.png)

Chat Page
![Chat Page](./public/previews/chat.png)

Profile Settings
![Profile Settings](./public/previews/profile.png)

## Features

### Authentication

- Robust user authentication flow in the backend with FastAPI.
- Secured login system with options for email and password.
- Automated email verification during the registration process using Mailtrap.

### Chat Functionalities

#### One-on-One Chat

- Users can initiate private chats with other users.
- Chat history is stored and can be retrieved anytime.

#### Group Chat

- Users can create group chats.
- Functionality to add or remove participants.
- Real-time updates in group chats for all participants.

#### Real-Time Notifications

- Notifications for new messages, chat invitations, and more.
- Real-time updates without needing to refresh the page.

### Pages

#### Login Page

- Simple and secure login interface.
- Option for password recovery and email verification resend.

#### Chat Page

- Real-time chat functionality.
- Supports sending text, images, and files.

#### Profile Settings

- Users can update their profile information.
- Settings to manage account security and chat preferences.

## Built with

- [Next.js 14](https://nextjs.org)
- [FastAPI](https://fastapi.tiangolo.com/)
- [TypeScript](https://www.typescriptlang.org)
- [Vite](https://vitejs.dev)
- [MongoDB](https://mongodb.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Socket.io](https://socket.io)
- [Vercel](https://vercel.com) (Frontend Deployment)
- [Heroku](https://heroku.com) (Backend Deployment)
- [Mailtrap](https://mailtrap.io)

## Licence

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
