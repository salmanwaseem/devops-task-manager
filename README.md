# DevOps Task Manager — Mid-Term Lab

An original beginner-friendly app demonstrating **Nginx (frontend), Flask (API), PostgreSQL (database), Dockerfiles, Docker Compose, a named Docker volume, and Selenium browser tests**.

## Requirements
- Windows 10/11 + WSL 2 + Docker Desktop running
- VS Code (recommended)
- PowerShell
- Optional later: Python 3.10+, Chrome, Git, and an AWS account

## Start the app (Windows PowerShell)
1. Extract the project. In VS Code choose **File > Open Folder** and select `devops-task-manager`.
2. From the VS Code terminal, in the folder containing `docker-compose.yml`:

   ```powershell
   Copy-Item .env.example .env
   docker compose up -d --build
   docker compose ps
   ```

3. Open **http://localhost:8080**. Add, complete, and delete tasks.
4. Visit **http://localhost:8080/health** to confirm `"status": "ok"`.

The first build downloads and installs base images and Python packages. It can take a while on the first run.

## What the files do
- `frontend/index.html`, `styles.css`, `app.js`: browser interface
- `frontend/nginx.conf`: web server and proxy to Flask API
- `backend/app.py`: Flask REST API for tasks; queries PostgreSQL
- `db/init.sql`: creates the `tasks` database table during first DB setup
- `backend/Dockerfile`, `frontend/Dockerfile`: build custom images
- `docker-compose.yml`: launches and networks the three services
- `.env.example`: example configuration. Copy to `.env`; never commit `.env`.
- `tests/test_app.py`: Selenium browser checks

## What to screenshot for the exam
- Docker `hello-world` output, Docker version
- Both Dockerfiles in VS Code
- `docker compose up -d --build` output
- `docker compose ps` showing `db`, `api`, `web`
- Task Manager app with some tasks added
- `docker volume ls` and persistence demo later

## Named volume persistence demo
1. Add a task in the browser.
2. Run `docker compose down` **without `-v`**.
3. Run `docker compose up -d`.
4. Refresh the browser: the task should still be there.

`docker compose down -v` removes the named database volume, so avoid it when demonstrating persistence.

## Selenium later
With Python and Chrome installed, open PowerShell in the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r tests/requirements.txt
New-Item -ItemType Directory -Force reports | Out-Null
python -m pytest tests -v --html=reports/report.html --self-contained-html
```

## Troubleshooting
- **Docker error during connect**: open Docker Desktop and wait for the engine.
- **Port 8080 occupied**: edit `.env` to use `WEB_PORT=8081`, then open http://localhost:8081.
- **Database or API not ready**: inspect `docker compose ps` and `docker compose logs api`.
- **You see `no configuration file provided`**: use PowerShell `Get-Location` to ensure you are in the project root.
- **You see `Dockerfile` missing**: ensure the complete ZIP was extracted and the files are in their expected folders.

## AWS deployment later
The exam target group uses port **80**. On EC2, set `WEB_PORT=80` in the server's `.env` file before running Docker Compose. Use a strong unique DB password on AWS. Do **not** expose the PostgreSQL port publicly. The lab guide's architecture stores a separate DB volume per EC2 instance, so new instances will not share tasks; this is a classroom demonstration rather than a production shared database design.

## Concept check
- Docker image = packaged app built from a Dockerfile.
- Container = running instance of an image.
- Docker Compose = defines and runs related containers together.
- Named volume = persistent DB files, even when DB container is recreated.
- `/health` = reports app and database health for AWS load balancer checks.
