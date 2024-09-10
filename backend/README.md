# Backend API Server
## Introduction
This repository contains the backend API server built with FastAPI. It handles user authentication, chat functionalities, and supports real-time message handling. MongoDB is used as the database, and it integrates with Mailtrap for email services.
## Prerequisites
- Python 3.11+
- pip
- MongoDB
## Getting Started
### Clone the Repository
To get started with the project, clone the repository using:
```bash
git clone https://github.com/Dhruv-mak/CipherTalk
cd CipherTalk/backend
```
### Set Up the Environment
1. Create a virtual environment:
```bash
python -m venv venv
```
2. Activate the virtual environment:
- For Windows:
```bash
.\venv\Scripts\activate
```
- For Unix or MacOS:
```bash
source venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
### Configure the Application
Copy the .env.sample file to .env and update it with the correct values:
```bash
cp .env.sample .env
```
Fill in the .env file with your details:
```
MAILTRAP_SMTP_USER="<your-mailtrap-user>"
MAILTRAP_SMTP_PASS="<your-mailtrap-password>"
ACCESS_TOKEN_SECRET="<your-access-token-secret>"
ACCESS_TOKEN_EXPIRE_MINUTES="<access-token-expire-time-in-minutes>"
REFRESH_TOKEN_SECRET="<your-refresh-token-secret>"
REFRESH_TOKEN_EXPIRY="<refresh-token-expiry-time>"
DATABASE_URI="<your-mongodb-uri>"
```
### Running the Server
To run the server, execute:
```bash
uvicorn main:app --reload
```
## API Endpoints
Placeholder for API endpoints description.
### User Authentication
- /register: Register a new user.
- /login: Authenticate a user and return a token.
- /verify-email/{verification_token}: Verify user email.
- More endpoints related to authentication...
### Chat Functionalities
- /chats: Retrieve all chats for the authenticated user.
- /chats/users: Get available users for chat.
- More chat related endpoints...
## Features
- User authentication and management.
- Real-time chat functionalities.
- End-to-End encryption
- Group chat management.
- Integration with Mailtrap for email services.
## Contributing
Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.
## License
[MIT]()
