# Agentic-IAM

Agentic-IAM — نظام إدارة الهوية والصلاحيات مخصّص للأعمال المعتمدة على الوكلاء (agent-centric).
المشروع مكتوب بـ Python ويجمع بين واجهة إدارة محلية عبر Streamlit، خدمات المصادقة والتفويض، إدارة الجلسات، سجل المراجعة (audit), وأدوات نشر وتشغيل محلية وسحابية.

---

## نظرة سريعة (Arabic)

- واجهة Streamlit لإدارة الوكلاء ومراقبة الحالة
- مصادقة وتفويض جاهزة (authentication & authorization)
- إدارة الجلسات، التوثيق، وإدارة بيانات الاعتماد
- تسجيل تدقيق وامتثال (audit & compliance)
- أدوات CLI لمساعدات قائمة على الذكاء الاصطناعي
- سكربتات تشغيل ونشر محلية وملفات مساعدة للنشر على Azure/Docker

## Quick Overview (English)

Agentic-IAM is a full-stack Python project providing identity & access management for agent workflows, including:

- Streamlit admin dashboard
- API entry points and orchestrator
- Audit logging and compliance helpers
- Deployment scripts and Azure artifacts

---

## Getting Started

Prerequisites:

- Python 3.9+
- Git
- (Optional) Docker for containerized runs

Clone and prepare:

```bash
git clone <your-github-repo-url>
cd Agentic-IAM-main
python -m venv .venv
```

Activate and install:

PowerShell:

```powershell
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Run the dashboard locally:

```bash
python run_gui.py
```

Or use the provided Windows launcher:

```bat
run_dashboard.bat
```

Open your browser at `http://localhost:8501`.

---

## Important Commands

- Create bootstrap admin account:

```bash
python setup_admin.py
```

- Run quick local checks:

```bash
python test_setup.py
```

- Run full test suite (if pytest installed):

```bash
pytest
```

---

## Configuration

Main configuration: `config/settings.py`.
Key settings to review for production:

- `ENVIRONMENT` — development|staging|production
- `SECRET_KEY` / `ENCRYPTION_KEY` — DO NOT commit real secrets
- `API_HOST`, `API_PORT`
- `LOG_LEVEL`, `ENABLE_AUDIT_LOGGING`, `ENABLE_MTLS`

Use environment variables or secret stores (Key Vault) in production.

---

## Docker & Deployment

The repository includes Dockerfiles and Azure deployment artifacts (`azure.yaml`, infra Bicep files).

To build locally with Docker:

```bash
docker build -t agentic-iam:local .
docker run -p 8501:8501 agentic-iam:local
```

For Azure or production deployment, review `AZURE_DEPLOYMENT_GUIDE.md` and `infra/`.

---

## Files of Interest

- `app.py` — Streamlit dashboard entry
- `main.py` — orchestrator for API + UI
- `run_gui.py`, `run_dashboard.bat` — launchers
- `config/settings.py` — configuration defaults
- `deploy-to-azure.ps1`, `azure.yaml`, `infra/` — deployment helpers

---

## Contributing

1. Fork the repository and create a feature branch.
2. Make changes and add tests where applicable.
3. Run tests locally.
4. Open a Pull Request with a clear description and reference issues.

Please follow conventional commits for clear history (e.g., `feat:`, `fix:`, `docs:`).

---

## Security & Secrets

- Never commit plain secrets. Use environment variables or secret managers.
- Rotate keys and review `security_report.json` and `SECURITY_TESTING.md` before production.

---

## License

MIT

---

## Contact

If you want me to draft a GitHub release, open a PR, or translate this README fully to English only, tell me which and I will proceed.