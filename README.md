# FastAPI Task Manager

A lightweight, asynchronous task management API built with FastAPI and PostgreSQL. 
It provides user authentication, role-based access control, and a simple task tracking system. 

This project serves as a solid foundation for a personal productivity tool or a boilerplate for setting up standard FastAPI backends. Redis is used to cache heavy operations and keep responses fast.

## Features
- **User Authentication:** JWT-based auth with access and refresh tokens.
- **Roles:** Basic role system (Admin / User). Admins have permission to manage other accounts and tasks.
- **Tasks:** Secure CRUD operations where regular users can only see and modify their own tasks.
- **Caching:** Redis integration to cache repeating queries (like task counts) and reduce database load.

## Tech Stack
- Python 3.10+
- FastAPI
- PostgreSQL (with SQLAlchemy & asyncpg)
- Redis 
- Alembic (database migrations)

## Quick Start

The easiest way to run the project is via Docker Compose.

1. Clone the repository and navigate into the folder.
2. Set up your environment variables based on the template:
   ```bash
   cp .env.example .env
   ```
3. Spin up the containers:
   ```bash
   docker-compose up -d --build
   ```

The API will be available at `http://localhost:8000`. 
You can view the interactive Swagger documentation and test the endpoints at `http://localhost:8000/docs`.
