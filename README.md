# Agentic-IAM

Agentic-IAM is a Python-based identity and access management project for agent-centric workloads. It includes authentication, authorization, session handling, audit logging, credential management, and a Streamlit dashboard for local administration.

## What is included

- Streamlit dashboard for managing agents and reviewing status
- Authentication and authorization helpers
- Session and credential management utilities
- Audit and compliance logging
- AI assistant CLI scripts for guided help
- Local database-backed configuration and startup scripts

## Repository layout

- `app.py` - Streamlit dashboard entry point
- `main.py` - Platform orchestrator for API and dashboard startup
- `run_gui.py` - Convenience launcher for the dashboard
- `run_dashboard.bat` - Windows launcher for the dashboard
- `setup_admin.py` - Bootstrap admin account setup
- `check_all.ps1` - PowerShell quality gate script
- `requirements.txt` - Python dependencies

## Requirements

- Python 3.9 or newer
- PowerShell 5.1 or Command Prompt on Windows
- Git for cloning and updates

## Quick start

### 1. Clone the repository

```bash
git clone <your-github-repo-url>
cd Agentic-IAM-main
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the dashboard

```bash
python run_gui.py
```

Or on Windows:

```bat
run_dashboard.bat
```

Then open:

```text
http://localhost:8501
```

## Bootstrap admin account

The project does not ship with hard-coded demo credentials. Create the first admin account locally:

```bash
python setup_admin.py
```

Optional environment variable:

```bash
set AGENTIC_IAM_ADMIN_PASSWORD=YourStrongPasswordHere
```

## Configuration

The main configuration object is in `config/settings.py`. Common settings include:

- `ENVIRONMENT`
- `DEBUG`
- `API_HOST`
- `API_PORT`
- `LOG_LEVEL`
- `SECRET_KEY`
- `ENCRYPTION_KEY`
- `ENABLE_MTLS`
- `ENABLE_AUDIT_LOGGING`

The defaults are intended for local development. Production deployments should override secrets and review TLS, database, and audit settings before use.

## Testing

Run the local checks:

```bash
python test_setup.py
```

On Windows, you can also use:

```powershell
.\check_all.ps1
```

If you have pytest installed, run the test suite directly:

```bash
pytest
```

## Security notes

- Do not commit real secrets to the repository.
- Use environment variables or secret storage for production values.
- Review `SECRET_KEY` and `ENCRYPTION_KEY` before deploying.
- Enable mTLS only after certificates and endpoints are configured correctly.

## Launch options

- `python run_gui.py` for the dashboard
- `python app.py` for the Streamlit app entry point
- `python main.py` for the broader platform orchestrator

## Contributing

1. Create a feature branch.
2. Make focused changes.
3. Run tests locally.
4. Open a pull request with a short summary of the change.

## License

MIT