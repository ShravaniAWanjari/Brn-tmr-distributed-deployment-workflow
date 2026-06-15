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
1. **Jenkins Could Not Find the Repository Branch**
   * *Error*: `couldn't find remote ref refs/heads/master`
   * *Cause*: The repository uses the `main` branch but Jenkins was configured to use `master` by default.
   * *Fix*: Change the branch specifier configuration in Jenkins to `*/main`.
2. **Jenkins Workspace Became Corrupted**
   * *Error*: `fatal: not in a git directory`
   * *Cause*: Workspace ownership changed between the `root` and `jenkins` users, leaving the workspace in an invalid state.
   * *Fix*: Delete the affected workspace directory and allow Jenkins to re-clone the repository.
3. **Jenkins Controller Could Build But Agent Could Not (Docker command not found)**
   * *Error*: `docker: not found`
   * *Cause*: The default Jenkins inbound agent image does not include Docker.
   * *Fix*: Create a custom Jenkins agent image with `docker.io`, `git`, `curl`, and `ansible` pre-installed.
4. **Docker Permission Denied Inside Jenkins Agent**
   * *Error*: `permission denied while trying to connect to the Docker daemon socket`
   * *Cause*: The Jenkins agent container lacks permission to access the mounted `/var/run/docker.sock`.
   * *Fix*: Mount the Docker socket and pass the host Docker group ID to the agent container using `--group-add <docker-group-id>` (e.g., `--group-add 1001`).
5. **localhost Health Check Fails inside Jenkins Agent**
   * *Error*: `curl localhost:8000/health` connection error.
   * *Cause*: Inside a container, `localhost` refers to the container itself, not the host machine.
   * *Fix*: Change the endpoint to `http://host.docker.internal:8000/health`.
6. **Jenkins Agent Connected Successfully But Deployment Failed (Ansible not found)**
   * *Error*: `ansible-playbook: not found`
   * *Cause*: The Jenkins agent image does not contain Ansible.
   * *Fix*: Install Ansible inside the custom Jenkins agent image and rebuild it.
7. **Pipeline Runs on Jenkins Controller Instead of Agent**
   * *Cause*: Using `agent any` in the Jenkinsfile.
   * *Fix*: Use `agent { label 'docker-agent' }` in the Jenkinsfile to force builds onto the custom Jenkins Agent.
8. **Jenkins Agent Connected but Docker Commands Fail**
   * *Check*: Run `docker exec -it docker-agent bash` and then `docker ps` to debug. If this fails, the agent cannot access Docker. Fix Docker socket access before debugging the pipeline further.

## Key Takeaways & Lessons Learned
- **Separate Responsibilities**: The Jenkins Controller and Jenkins Agent should have separate responsibilities.
- **Docker Access & Permissions**: Installing Docker is not enough; host permissions (like access to `/var/run/docker.sock` and group membership) must be configured correctly.
- **Container Networking**: Container networking behaves differently from host networking (e.g., `localhost` inside a container refers to the container itself, not the host).
- **Deployment Health Checks**: Health checks should be treated as an essential part of the deployment process, not as an optional step.
- **Root Cause Analysis**: Infrastructure issues are often caused by permissions, networking, or environment differences rather than application code.
- **Incremental Verification**: Verifying each stage independently (Build, Deploy, Health Check, and Monitoring) makes debugging much easier.
- **Pipeline Integrity**: A successful build does not mean a successful deployment; verifying the final state of the running container is crucial.
