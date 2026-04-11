# E-Commerce Observability Platform

A complete Node.js API built using an Express backend connected to a Supabase PostgreSQL database, featuring a full-scale Observability pipeline powered by Loki, Promtail, and Grafana run entirely through Docker Compose.

## 🚀 Features
- **API Dashboard**: Integrated interactive HTML tester active on `localhost:3000/`.
- **Repository Pattern Architecture**: Strict db layer isolation built natively with `pg.Pool` overriding basic Mongoose architectures natively.
- **Micro-Delays & Random Faults**: `/products` natively waits variable intervals, and `/order` dynamically drops payments to create measurable API faults needed to test system visibility.
- **Custom JSON Logger**: Strict structural single-line JSON formatting directly to standard out (`stdout`). 
- **Promtail Interception**: Docker socket scraping isolating logs via native JSON regex to lift embedded metadata payloads (`level`, `endpoint`, etc.) into Grafana streams natively without requiring full text searches.

## 📦 Project Structure
```text
Log-Monitoring-Dashboard/
├── ecommerce-backend/
│   ├── src/                 # Express backend source configuration
│   ├── configs/             # Directory containing Loki & Promtail yaml definitions
│   ├── Dockerfile           # Backend containerization rules mapping to node:18-alpine
│   ├── docker-compose.yml   # Platform Orchestrator networking bridging the 4 systems
│   └── Jenkinsfile          # End-to-End declarative pipeline scripts
├── .env                     # Local URL dependencies utilizing Postgres encoded passwords 
└── README.md                # this file!
```

## 🛠 Prerequisites
1. **Node.js**: `v18+` capability for local manual run evaluations.
2. **Supabase Postgres**: A Postgres database where you've executed the schema defined in `database.sql`.
3. **Docker**: Access to a standard Docker daemon context (`docker-compose`).

## ⚙️ Local Operation Guide
1. Create your `.env` containing your database variable inside the repository root ensuring the password utilizes URL encoding (`@` = `%40`):
   ```env
   DATABASE_URL=postgresql://postgres:Supabase%402026@db.xxxxxxx.supabase.co:5432/postgres
   ```
2. Navigate context and boot the system orchestrator. This spans the private networking bridges and natively constructs everything in approximately ten seconds.
   ```bash
   cd ecommerce-backend
   docker-compose up -d --build
   ```

## 📊 Accessing Your Observability Stack
### 1. The Native App Environment
- **URL**: [http://localhost:3000/](http://localhost:3000/)
- Interact with the interactive GUI here. Ensure you click **Get Products** and **Submit Order** multiple times to ensure you trigger system failures!

### 2. The Grafana Dashboard Analytics
- **URL**: [http://localhost:3001/](http://localhost:3001/)
- Log in utilizing your current configured credentials (e.g. `admin` / `Abcd@1234`).
- **Connecting Loki Internally**:  
  1. Head to Data Sources -> "Add Data Source" -> select "Loki".
  2. Input the cross-container URL parameter: `http://loki:3100`.
  3. Validate & Save Settings.
- **Locating And Grouping Traces**:
  Navigate utilizing the "Explore" browser and leverage `LogQL` queries!
  ```logql
  # Discover all traffic moving inside the backend
  {container="ecommerce-backend"}

  # Filter utilizing our Promtail regex injection parameters for pure errors
  {container="ecommerce-backend", level="ERROR"}
  ```

## 🔄 CI/CD Automation Design (Jenkins)
Also dynamically included in the folder is a `Jenkinsfile` for your EC2 execution. When triggered by a branch push, this sequentially targets:
- Constructing out new backend Docker architectures incremented linearly.
- Authorizations mapping to pushing images inside the standard Docker Hub.
- Internal executions SSH'ing into your root EC2 host to trigger `docker-compose pull backend && docker-compose up -d --no-deps backend`, dynamically hot-reloading *only* your updated Node scripts seamlessly!
