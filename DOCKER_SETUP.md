# Docker Setup Guide

This guide explains how to run the SEC Edgar Regulatory Document Explorer using Docker.

## Prerequisites

- Docker Engine 20.10+ and Docker Compose v2.0+
- At least 4GB of available RAM
- Environment variables configured (see below)

## Quick Start

### 1. Set Up Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cd backend
cp .env.example .env
# Edit .env with your actual credentials
```

Required variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anonymous key
- `DATABASE_URL`: PostgreSQL connection string
- `GEMINI_API_KEY`: Google Gemini API key for embeddings

### 2. Build and Start All Services

From the project root directory:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f weaviate
```

### 3. Access the Application

Once all services are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Weaviate**: http://localhost:8080

## Architecture

The Docker setup includes three services:

### 1. Weaviate (Vector Database)
- **Port**: 8080 (HTTP), 50051 (gRPC)
- **Purpose**: Stores document embeddings for semantic search
- **Data Persistence**: Uses named volume `weaviate_data`

### 2. Backend (FastAPI)
- **Port**: 8000
- **Purpose**: REST API for document management and search
- **Features**:
  - SEC Edgar document retrieval
  - Document chunking and embedding
  - Semantic search with RAG
  - PostgreSQL for metadata storage
  - Weaviate for vector storage

### 3. Frontend (React + Nginx)
- **Port**: 3000
- **Purpose**: Web UI for document exploration
- **Features**:
  - Document browsing and filtering
  - Semantic search interface
  - Modern, responsive design
  - API proxy through Nginx

## Common Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Start with rebuild
docker-compose up -d --build
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100
```

### Rebuild Services
```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild without cache
docker-compose build --no-cache
```

### Execute Commands in Containers
```bash
# Backend shell
docker-compose exec backend bash

# Run Python script
docker-compose exec backend python reset_weaviate.py

# Frontend shell
docker-compose exec frontend sh
```

## Development Workflow

### Hot Reload

The backend includes volume mounting for hot reload during development:
- Changes to `backend/app/` are automatically reflected
- Uvicorn runs with `--reload` flag

For frontend changes:
1. Edit source files in `frontend/src/`
2. Rebuild the frontend service:
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

Alternatively, for faster frontend development, run Vite locally:
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

Run database operations:
```bash
# Initialize database
docker-compose exec backend python -c "from app.database import init_db; init_db()"

# Reset Weaviate
docker-compose exec backend python reset_weaviate.py
```

## Networking

All services communicate through a custom bridge network `app-network`:
- Services can reach each other using service names as hostnames
- Backend connects to Weaviate at `http://weaviate:8080`
- Frontend proxies API requests to `http://backend:8000`

## Health Checks

All services include health checks:
- **Weaviate**: Checks ready endpoint every 30s
- **Backend**: Checks root endpoint every 30s
- **Frontend**: Checks Nginx every 30s

View health status:
```bash
docker-compose ps
```

## Troubleshooting

### Backend Can't Connect to Weaviate
1. Check if Weaviate is healthy: `docker-compose ps`
2. Wait for Weaviate to be ready (can take 30-40s on first start)
3. Check logs: `docker-compose logs weaviate`

### Backend Startup Errors
1. Verify environment variables: `docker-compose config`
2. Check database connectivity
3. View logs: `docker-compose logs backend`

### Frontend Shows 404 on API Calls
1. Verify backend is running: `curl http://localhost:8000`
2. Check Nginx proxy configuration
3. View logs: `docker-compose logs frontend`

### Port Already in Use
If ports 3000, 8000, or 8080 are already in use, modify `docker-compose.yml`:
```yaml
ports:
  - "3001:80"  # Change 3000 to 3001
```

### Permission Denied Errors
On Linux, you may need to fix file permissions:
```bash
sudo chown -R $USER:$USER .
```

## Production Deployment

For production use:

1. **Use production environment files**:
   - Remove `--reload` from backend CMD
   - Set proper CORS origins
   - Use secrets management for API keys

2. **Configure reverse proxy**:
   - Use Nginx or Traefik in front of services
   - Set up SSL/TLS certificates
   - Configure proper security headers

3. **Scale services**:
   ```bash
   docker-compose up -d --scale backend=3
   ```

4. **Monitor resources**:
   ```bash
   docker stats
   ```

5. **Backup volumes**:
   ```bash
   docker run --rm -v weaviate_data:/data -v $(pwd):/backup \
     alpine tar czf /backup/weaviate_backup.tar.gz /data
   ```

## Clean Up

Remove all containers, networks, and volumes:
```bash
# Stop and remove containers and networks
docker-compose down

# Remove volumes too (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Complete cleanup
docker system prune -a --volumes
```

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Weaviate Documentation](https://weaviate.io/developers/weaviate)
- [React Documentation](https://react.dev/)

