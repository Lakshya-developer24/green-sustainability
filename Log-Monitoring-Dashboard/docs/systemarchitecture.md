# System Architecture Document
## E-Commerce Observability Platform
**Version 1.1 | April 2025**

---

## 1. Architecture Overview

The system is composed of two logical layers running on a single AWS EC2 instance: the **Application Layer**, which handles user-facing API requests and generates structured logs, and the **Observability Layer**, which collects, stores, and visualizes those logs in near real time.

All four services (backend, Loki, Promtail, Grafana) are containerized and orchestrated with Docker Compose. Supabase (hosted PostgreSQL) runs externally as the cloud database, keeping the EC2 instance stateless with respect to business data.

---

## 2. End-to-End Request and Log Flow

### 2.1 Request Flow (Happy Path)

1. Client sends an HTTP request to the public EC2 IP on port 3000
2. Docker routes the request to the backend container
3. Express middleware measures response time and builds the log object
4. The route handler queries Supabase via the `pg` driver using a parameterized SQL query
5. The handler sends the HTTP response to the client
6. The logger serializes the log object to stdout as a single JSON line

### 2.2 Log Collection Flow

1. Docker captures the container's stdout stream
2. Promtail reads the stream via the Docker socket (`/var/run/docker.sock`)
3. Promtail extracts the `level` label using a regex pipeline stage on the JSON body
4. Promtail batches log entries and pushes them to Loki's push API (port 3100)
5. Loki stores the log entry indexed by its labels (`container`, `level`, `job`)
6. Grafana queries Loki using LogQL and renders the result in the dashboard

### 2.3 CI/CD Deployment Flow

1. Developer pushes code to the main branch on GitHub
2. GitHub sends a webhook notification to Jenkins on port 8080
3. Jenkins checks out the latest code
4. Jenkins builds a new Docker image and pushes it to Docker Hub
5. Jenkins SSH-es into the EC2 instance
6. Jenkins runs `docker-compose pull` and `docker-compose up -d` on the EC2 instance
7. The backend container restarts with the new image; all other containers remain running

---

## 3. Container Architecture

### 3.1 Docker Network

All containers share a single Docker bridge network named `observability-net`. Containers communicate by service name (DNS-resolved internally). Only ports 3000 and 3001 are exposed to the host and, through EC2 Security Groups, to the internet.

### 3.2 Container Specifications

| Container | Image                   | Port            | Volumes                        | Dependencies        |
|-----------|-------------------------|-----------------|--------------------------------|---------------------|
| backend   | custom (node:18-alpine) | 3000:3000       | None (stateless)               | Supabase (external) |
| loki      | grafana/loki:2.9.0      | 3100 (internal) | loki-data:/loki                | None                |
| promtail  | grafana/promtail:2.9.0  | 9080 (internal) | /var/run/docker.sock (bind)    | loki                |
| grafana   | grafana/grafana:10.2.0  | 3001:3000       | grafana-data:/var/lib/grafana  | loki                |
| jenkins   | jenkins/jenkins:lts     | 8080:8080       | jenkins-home:/var/jenkins_home | None                |

---

## 4. Backend Application Architecture

### 4.1 Folder Structure
ecommerce-backend/
├── src/
│   ├── config/
│   │   └── db.js                  # Supabase PostgreSQL connection pool (pg)
│   ├── models/
│   │   ├── userModel.js           # SQL queries for users table
│   │   ├── productModel.js        # SQL queries for products table
│   │   └── orderModel.js          # SQL queries for orders table
│   ├── routes/
│   │   ├── auth.js                # POST /signup, POST /login
│   │   ├── products.js            # GET /products
│   │   └── orders.js              # POST /order
│   ├── middleware/
│   │   └── requestLogger.js       # Attaches req.startTime for response_time calc
│   ├── utils/
│   │   └── logger.js              # Custom JSON stdout logger
│   └── app.js                     # Express app wiring and middleware registration
├── server.js                      # Entry point, starts HTTP server
├── Dockerfile                     # node:18-alpine production image
├── docker-compose.yml             # Full stack orchestration
├── .env                           # Local secrets (never committed)
├── .env.example                   # Template with no real values (committed)
├── Jenkinsfile                    # Declarative CI/CD pipeline
└── configs/
├── loki-config.yaml           # Loki single-binary configuration
└── promtail-config.yaml       # Promtail Docker scrape configuration

### 4.2 Database Connection (Supabase via pg)

The backend connects to Supabase using the standard PostgreSQL connection string provided in the Supabase dashboard under **Settings → Database → Connection string (URI mode)**.

`src/config/db.js` creates a `pg.Pool` instance using the `DATABASE_URL` environment variable. All route handlers import this pool and execute parameterized SQL queries directly.
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
### 4.3 Middleware Chain

Every request passes through the following middleware in order:

1. `requestLogger` middleware — records `req.startTime = Date.now()`
2. Express router — matches route and calls handler
3. Route handler — executes SQL query via `pg`, calls `logger.info()` / `logger.warn()` / `logger.error()`
4. Response sent to client

The `response_time` field is calculated as `Date.now() - req.startTime` at the point the log is emitted.

---

## 5. Logging Architecture

### 5.1 Log Pipeline

The logging pipeline is push-based with no persistent storage on disk:
Backend stdout → Docker log driver → Promtail Docker scraper → Loki push API → Grafana LogQL query
### 5.2 Label Taxonomy

| Label     | Example           | How it is set                                                 |
|-----------|-------------------|---------------------------------------------------------------|
| job       | docker            | Static label in Promtail config                               |
| container | ecommerce-backend | Extracted from Docker container name by Promtail              |
| level     | ERROR             | Extracted from JSON log body by Promtail regex pipeline stage |

### 5.3 Promtail Pipeline Stage

Promtail uses a JSON pipeline stage to parse the log body and promote the `level` field to a stream label. This enables LogQL label-based filtering in Grafana without full-text scanning.

Example LogQL queries:

```logql
# Show only errors
{container="ecommerce-backend"} | json | level="ERROR"

# Show all logs for the /order endpoint
{container="ecommerce-backend"} |= "/order"

# Show warnings with full parsed fields
{container="ecommerce-backend"} | json | level="WARN"
```

---

## 6. Security Considerations

### 6.1 Secrets Management

- The Supabase `DATABASE_URL` is stored in a `.env` file on EC2, never committed to git
- Docker Hub credentials are stored in Jenkins Credentials Manager
- EC2 SSH private key is stored in Jenkins as an SSH credential
- A `.env.example` file is committed to the repository as a template with no real values

### 6.2 Network Security

- EC2 Security Group inbound rules open only ports 22 (SSH), 3000 (API), 3001 (Grafana), and 8080 (Jenkins)
- Loki (3100) and Promtail (9080) are not exposed outside the Docker network
- Grafana anonymous access is disabled; login is required
- Jenkins port 8080 should be restricted to your IP address in the Security Group

### 6.3 Password Security

- User passwords are hashed with `bcryptjs` using a salt round of 10 before storage in Supabase
- Plain-text passwords are never logged
- SQL queries use parameterized statements (`$1`, `$2`) to prevent SQL injection

---

## 7. Scalability Notes

This architecture is intentionally single-node for learning purposes. The following changes would be required to scale to production:

- Replace Docker Compose with Kubernetes (EKS) for horizontal scaling
- Replace single-binary Loki with a distributed Loki deployment backed by S3 object storage
- Upgrade Supabase from the free tier to a Pro plan with connection pooling via PgBouncer
- Add an Application Load Balancer (ALB) in front of the backend for traffic distribution
- Replace Jenkins on EC2 with a managed CI/CD service such as GitHub Actions or AWS CodePipeline