# 🚀 Smart Travel Optimizer

An **agentic AI system** that finds optimal travel routes with minimal time, cost efficiency, big luggage allowance, and max 1–2 connections. Features both CLI and web interfaces with built-in security.

## 🛡️ Security Features

- Input validation and sanitization
- Email validation
- SMTP security with timeout
- SQL injection prevention
- XSS protection
- Security scanning with Bandit, Safety, and pip-audit
- Pre-commit hooks for security checks

## 🚀 Quick Start

### ⚡ Super Quick (2 minutes with Mock Data)
```bash
cp .env.example .env
pip install -r requirements.txt
python main.py --origin "Stuttgart" --destination "Vienna" --date "2025-10-01"
```

### 🔑 With Real API Keys
1. **📖 Read the guides**:
   - **[QUICK_START.md](QUICK_START.md)** - 5-minute setup
   - **[docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md)** - Detailed instructions

2. **🪟 Windows Users**: Run `.\setup-api-keys.ps1`
3. **🐧 Linux/Mac Users**: Run `./setup-api-keys.sh`

### 1. Environment Setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env with your SMTP and API credentials
# See docs/API_KEYS_SETUP.md for detailed instructions
```

### 3. Run Application

#### CLI Usage
```bash
python main.py --origin "Stuttgart" --destination "Vienna" --date "2025-10-01" --bags 2 --max-connections 2 --email you@example.com
```

#### Web Interface
```bash
streamlit run streamlit_app.py
```

#### Docker
```bash
docker-compose up -d
```

## 🧪 Development

### Setup Development Environment
```bash
make setup-dev
# or manually:
pip install -r requirements-dev.txt
pre-commit install
```

### Available Commands
```bash
make help              # Show all available commands
make test              # Run tests
make test-cov          # Run tests with coverage
make security          # Run security scans
make lint              # Run linting
make format            # Format code
make sonar             # Run SonarQube analysis
make clean             # Clean generated files
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run security tests only
pytest -m security
```

### Security Scanning

#### Local Security Scans
```bash
# All security scans
make security

# Individual scans
bandit -r src/ main.py streamlit_app.py
safety check
pip-audit
```

#### SonarQube Analysis
```bash
# Start SonarQube locally
docker-compose up sonarqube -d

# Run analysis
make sonar
# or
sonar-scanner
```

## 🏗️ Architecture

This is an **agentic AI system** with:

- **Autonomous Decision Making**: Smart provider selection and error handling
- **Tool Integration**: Multiple travel APIs, filtering, and scoring tools  
- **Goal-Oriented Behavior**: Multi-criteria optimization for travel routes
- **Security-First Design**: Input validation, sanitization, and monitoring

### Project Structure
```
├── src/
│   ├── agents/          # Core AI agents
│   ├── tools/           # Tool implementations
│   │   ├── providers/   # Travel data providers
│   │   └── security.py  # Security utilities
│   ├── ragdb/          # Knowledge base
│   └── prompts/        # AI prompts
├── tests/              # Test suite
├── data/               # Sample data
├── .github/workflows/  # CI/CD pipelines
└── docs/              # Documentation
```

## 📋 Requirements

- Python 3.8+
- Node.js 16+ (for tooling)
- SonarQube (optional, for code quality)

## 🔒 Security Considerations

- Never commit `.env` files
- Use strong, unique API keys
- Rotate credentials regularly  
- Enable 2FA on all accounts
- Review security scan reports
- Keep dependencies updated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and security scans
5. Submit a pull request

## 📜 License

MIT License - see LICENSE file for details.
