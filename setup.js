#!/usr/bin/env node

/**
 * Smart Travel Optimizer - Setup Script
 * Automated setup for development environment
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function execCommand(command, description) {
  log(`\n${colors.cyan}→ ${description}${colors.reset}`);
  try {
    execSync(command, { stdio: 'inherit' });
    log(`${colors.green}✓ ${description} completed${colors.reset}`);
  } catch (error) {
    log(`${colors.red}✗ ${description} failed${colors.reset}`);
    throw error;
  }
}

function checkRequirements() {
  log(`\n${colors.blue}Checking system requirements...${colors.reset}`);
  
  try {
    execSync('python --version', { stdio: 'pipe' });
    log(`${colors.green}✓ Python is installed${colors.reset}`);
  } catch {
    log(`${colors.red}✗ Python is not installed${colors.reset}`);
    process.exit(1);
  }

  try {
    execSync('node --version', { stdio: 'pipe' });
    log(`${colors.green}✓ Node.js is installed${colors.reset}`);
  } catch {
    log(`${colors.red}✗ Node.js is not installed${colors.reset}`);
    process.exit(1);
  }

  try {
    execSync('sonar-scanner --version', { stdio: 'pipe' });
    log(`${colors.green}✓ SonarScanner is installed${colors.reset}`);
  } catch {
    log(`${colors.yellow}⚠ SonarScanner not found - install manually or use Docker${colors.reset}`);
  }
}

function createDirectories() {
  const dirs = ['reports', 'logs', 'docs'];
  dirs.forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      log(`${colors.green}✓ Created directory: ${dir}${colors.reset}`);
    }
  });
}

function setupEnvironment() {
  if (!fs.existsSync('.env')) {
    if (fs.existsSync('.env.example')) {
      fs.copyFileSync('.env.example', '.env');
      log(`${colors.green}✓ Created .env from .env.example${colors.reset}`);
    }
  }
}

async function main() {
  log(`${colors.bright}${colors.blue}
╔═══════════════════════════════════════════════════════════════╗
║               Smart Travel Optimizer Setup                   ║
║               Agentic AI Travel Route Optimizer              ║
╚═══════════════════════════════════════════════════════════════╝
${colors.reset}`);

  try {
    checkRequirements();
    createDirectories();
    setupEnvironment();

    execCommand('npm install', 'Installing Node.js dependencies');
    execCommand('pip install -r requirements-dev.txt', 'Installing Python dependencies');
    
    try {
      execCommand('pre-commit install', 'Installing pre-commit hooks');
    } catch {
      log(`${colors.yellow}⚠ Pre-commit installation failed - you may need to install it manually${colors.reset}`);
    }

    log(`\n${colors.green}${colors.bright}🎉 Setup completed successfully!${colors.reset}`);
    log(`\n${colors.cyan}Next steps:${colors.reset}`);
    log(`  1. Edit .env file with your API credentials`);
    log(`  2. Run: ${colors.yellow}npm run dev${colors.reset} to start development`);
    log(`  3. Run: ${colors.yellow}npm run security${colors.reset} to run security scans`);
    log(`  4. Run: ${colors.yellow}npm run test${colors.reset} to run tests`);
    log(`\n${colors.blue}Available commands:${colors.reset}`);
    log(`  ${colors.yellow}npm run dev${colors.reset}        - Start development server`);
    log(`  ${colors.yellow}npm run test${colors.reset}       - Run tests`);
    log(`  ${colors.yellow}npm run security${colors.reset}   - Run security scans`);
    log(`  ${colors.yellow}npm run sonar${colors.reset}      - Run SonarQube analysis`);
    log(`  ${colors.yellow}make help${colors.reset}          - Show all available commands`);

  } catch (error) {
    log(`\n${colors.red}Setup failed: ${error.message}${colors.reset}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main };
