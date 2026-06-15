# Brain Tumor Classification - CI/CD Deployment Platform

## Overview
This project deploys a brain tumor classification API using:
- **FastAPI** (Inference service)
- **Docker** (Containerization engine)
- **Jenkins** (CI/CD Controller)
- **Jenkins Agent** (Pipeline execution node)
- **Ansible** (Deployment automation)
- **Prometheus** (Metrics collection)
- **Grafana** (Monitoring dashboard)

The goal is to automatically build, deploy, and verify the application whenever the pipeline is triggered.

## Architecture
```text
GitHub → Jenkins Controller → Jenkins Agent → Docker Build → Ansible Deploy → FastAPI Container → Health Check
                                                                                  └─→ Prometheus ─→ Grafana
```

## Components
*   **GitHub**: Stores source code, Dockerfiles, Jenkinsfile, and Ansible playbooks.
*   **Jenkins Controller**: Stores jobs, stores pipeline configurations, and assigns work to agents. It tracks build history but does not build Docker images.
*   **Jenkins Agent**: Clones the repository, builds Docker images, runs Ansible playbooks, and executes pipeline stages. All pipeline work runs here.
*   **Docker**: Used for building images, running containers, and managing deployments.
*   **Ansible**: Used for configuration tasks, removing old containers, building/pulling images, starting new containers, and running deployment tasks.
*   **Prometheus**: Collects metrics from the application (e.g., request count, response time, error rate).
*   **Grafana**: Displays metrics stored by Prometheus for monitoring dashboards.

## Pipeline Flow
1. **Checkout**: Jenkins Agent clones the repository.
   ```bash
   git clone <repository>
   ```
2. **Build Image**: Docker image is built.
   ```bash
   docker build -t brain-tumor-api ./backend
   ```
3. **Verify Image**: Checks that the image exists.
   ```bash
   docker images
   ```
4. **Deploy**: Ansible runs the deployment playbook (`ansible-playbook deploy.yml`) to remove old containers, build/pull the image, start the container, and wait for startup.
5. **Health Check**: Verify the application is running.
   ```bash
   curl http://host.docker.internal:8000/health
   ```
   *Expected response:*
   ```json
   {
     "status": "ok",
     "service": "brain_tumor_classification"
   }
   ```

## Running the Project
*   **Start Infrastructure**:
    ```bash
    docker start jenkins
    docker start prometheus-dev
    docker start grafana
    ```
*   **Start Application**:
    ```bash
    docker start brain-tumor-api
    ```
*   **Check Application**:
    ```bash
    curl http://localhost:8000/health
    ```
*   **Monitoring Endpoints**:
    *   Prometheus: `http://localhost:9090`
    *   Grafana: `http://localhost:3001`
    *   Jenkins: `http://localhost:8080`

## Common Issues & Fixes
1. **Docker command not found** (`docker: not found`)
   * *Cause*: Docker is not installed inside the Jenkins Agent.
   * *Fix*: Install Docker in the agent image and rebuild it.
2. **Permission denied for Docker socket** (`permission denied while trying to connect to Docker daemon`)
   * *Cause*: Agent user does not have permission to access `/var/run/docker.sock`.
   * *Fix*: Add the Docker socket group to the container via `--group-add <docker-group-id>`.
3. **localhost health check fails** (`curl localhost:8000` fails inside Jenkins Agent)
   * *Cause*: Inside a container, `localhost` refers to the container itself, not the host machine.
   * *Fix*: Use `host.docker.internal` instead: `curl http://host.docker.internal:8000/health`.
4. **Pipeline runs on Jenkins Controller**
   * *Cause*: Using `agent any` may run the pipeline on the controller.
   * *Fix*: Use `agent { label 'docker-agent' }` to force builds onto the Jenkins Agent.
5. **Jenkins Agent is connected but builds fail**
   * *Check*: Run `docker exec -it docker-agent bash` followed by `docker ps`. If it fails, the agent cannot access Docker. Fix Docker access before debugging the pipeline.

## Lessons Learned
- Controller and Agent should be separate.
- Agent needs Docker access, not just Docker installed.
- `localhost` inside a container is not the host machine.
- Health checks should always be part of deployment.
- A successful build does not mean a successful deployment.
- Verify each stage separately: Build, Deploy, Health Check, and Monitoring.
