#!/usr/bin/env make
# ============================================================================
# Smart Travel Optimizer - Makefile
# Agentic AI Travel Route Optimization System
# ============================================================================

.PHONY: help setup install test security lint format clean run sonar docker
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m 
RESET := \033[0m

help:  ## Show this help message
	@echo "$(BLUE)Smart Travel Optimizer - Available Commands$(RESET)"
	@echo "=============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Setup and Installation
setup:  ## Setup complete development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	npm install
	npm run python:install-dev
	npm run prepare
	mkdir -p reports
	@echo "$(GREEN)Setup complete!$(RESET)"

install:  ## Install production dependencies only
	npm run python:install

install-dev:  ## Install development dependencies
	npm run python:install-dev

# Development
dev:  ## Start development server
	npm run dev

start:  ## Start production server
	npm run start

# Testing
test:  ## Run all tests
	npm run test

test-watch:  ## Run tests in watch mode
	npm run test:watch

test-cov:  ## Run tests with coverage reporting
	npm run test:coverage

# Code Quality
lint:  ## Run all linters
	npm run lint

format:  ## Format all code
	npm run format

# Security
security:  ## Run all security scans
	@echo "$(YELLOW)Running comprehensive security analysis...$(RESET)"
	npm run security

security-sonar:  ## Run SonarQube security scan
	npm run security:sonar

security-python:  ## Run Python-specific security scans
	npm run security:python

# SonarQube
sonar:  ## Run SonarQube analysis
	npm run sonar

sonar-local:  ## Run SonarQube using Docker
	npm run sonar:local

# Maintenance
clean:  ## Clean all generated files
	npm run clean
	npm run clean:reports

clean-all: clean  ## Deep clean including dependencies
	rm -rf node_modules/
	rm -rf .venv/

# CI/CD
ci:  ## Run CI pipeline locally
	npm run ci

pre-commit:  ## Run pre-commit hooks
	npm run precommit

# Docker
docker-build:  ## Build Docker image
	docker-compose build

docker-up:  ## Start services with Docker
	docker-compose up -d

docker-down:  ## Stop Docker services
	docker-compose down

docker-logs:  ## View Docker logs
	docker-compose logs -f

# Utilities
check-deps:  ## Check for dependency updates
	npm outdated
	pip list --outdated

update-deps:  ## Update dependencies (use with caution)
	npm update
	pip install --upgrade -r requirements-dev.txt

# Project Status
status:  ## Show project status
	@echo "$(BLUE)Project Status$(RESET)"
	@echo "=============="
	@echo "Python: $$(python --version 2>&1)"
	@echo "Node.js: $$(node --version 2>&1)"
	@echo "npm: $$(npm --version 2>&1)"
	@echo "Git: $$(git --version 2>&1)"
	@echo ""
	@echo "$(GREEN)Project ready for development!$(RESET)"
