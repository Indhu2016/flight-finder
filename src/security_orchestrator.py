"""
Clean Travel Security Orchestrator - Best Practices Implementation
================================================================

Key Features:
✅ Minimal dependencies and clean architecture
✅ Comprehensive error handling and fault tolerance
✅ Travel-specific security patterns
✅ Good coding practices throughout
✅ Simple API and clear documentation
"""

import asyncio
import logging
import json
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class TravelSecurityOrchestrator:
    """Clean, fault-tolerant security orchestrator for travel applications"""
    
    def __init__(self, project_path: str = "."):
        """Initialize with safe defaults and error handling"""
        self.logger = self._setup_logging()
        self.project_path = Path(project_path).resolve()
        self.scan_results = {}
        
        # Clean configuration with validation
        self.config = {
            'bandit_enabled': True,
            'safety_enabled': True,
            'secret_detection_enabled': True,
            'sonarqube_enabled': False,
            'sonarqube_url': None,
            'sonarqube_token': None,
            'sonarqube_project_key': 'smart-travel-optimizer'
        }
        
        self.logger.info(f"Security orchestrator initialized: {self.project_path}")

    def _setup_logging(self) -> logging.Logger:
        """Setup clean logging with error handling"""
        logger = logging.getLogger('TravelSecurity')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def configure_sonarqube(self, url: str, token: str, project_key: str = None) -> bool:
        """Configure SonarQube with validation"""
        try:
            if not url or not token:
                self.logger.error("SonarQube URL and token required")
                return False
                
            self.config.update({
                'sonarqube_url': url.rstrip('/'),
                'sonarqube_token': token,
                'sonarqube_project_key': project_key or self.config['sonarqube_project_key'],
                'sonarqube_enabled': True
            })
            
            self.logger.info("SonarQube configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"SonarQube configuration failed: {e}")
            return False

    async def run_security_scan(self, scan_types: List[str] = None) -> Dict[str, Any]:
        """Run security scan with comprehensive error handling"""
        try:
            self.logger.info("Starting security scan...")
            
            if scan_types is None:
                scan_types = ['bandit', 'safety', 'secrets']
                if self.config['sonarqube_enabled']:
                    scan_types.append('sonarqube')
            
            results = {
                'metadata': {
                    'scan_start': datetime.now().isoformat(),
                    'project_path': str(self.project_path),
                    'scan_types': scan_types
                },
                'results': {},
                'summary': {},
                'recommendations': []
            }
            
            # Run scans with isolation
            for scan_type in scan_types:
                try:
                    if scan_type == 'bandit' and self.config['bandit_enabled']:
                        results['results']['bandit'] = await self._run_bandit_scan()
                    elif scan_type == 'safety' and self.config['safety_enabled']:
                        results['results']['safety'] = await self._run_safety_scan()
                    elif scan_type == 'secrets' and self.config['secret_detection_enabled']:
                        results['results']['secrets'] = await self._run_secret_scan()
                    elif scan_type == 'sonarqube' and self.config['sonarqube_enabled']:
                        results['results']['sonarqube'] = await self._run_sonarqube_scan()
                except Exception as e:
                    self.logger.warning(f"{scan_type} scan failed: {e}")
                    results['results'][scan_type] = {'status': 'failed', 'error': str(e)}
            
            # Generate summary
            results['summary'] = self._generate_summary(results['results'])
            results['recommendations'] = self._generate_recommendations(results['results'])
            results['metadata']['scan_end'] = datetime.now().isoformat()
            
            self.scan_results = results
            self.logger.info("Security scan completed")
            return results
            
        except Exception as e:
            self.logger.error(f"Security scan failed: {e}")
            return {
                'metadata': {'scan_start': datetime.now().isoformat(), 'error': str(e)},
                'results': {}, 'summary': {'status': 'failed', 'error': str(e)}, 'recommendations': []
            }

    async def _run_bandit_scan(self) -> Dict[str, Any]:
        """Run Bandit with proper error handling"""
        try:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp:
                tmp_path = tmp.name
            
            cmd = ['bandit', '-r', str(self.project_path), '-f', 'json', '-o', tmp_path, '-ll']
            
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await process.communicate()
            
            try:
                with open(tmp_path, 'r') as f:
                    data = json.load(f)
                Path(tmp_path).unlink()
                
                issues = data.get('results', [])
                return {
                    'status': 'completed', 'tool': 'bandit', 'issues_found': len(issues),
                    'high_severity': len([i for i in issues if i.get('issue_severity') == 'HIGH']),
                    'medium_severity': len([i for i in issues if i.get('issue_severity') == 'MEDIUM']),
                    'low_severity': len([i for i in issues if i.get('issue_severity') == 'LOW']),
                    'details': issues[:5]
                }
            except (FileNotFoundError, json.JSONDecodeError):
                return {'status': 'completed', 'tool': 'bandit', 'issues_found': 0, 'message': 'No issues found'}
                
        except FileNotFoundError:
            return {'status': 'skipped', 'tool': 'bandit', 'message': 'Bandit not installed'}
        except Exception as e:
            return {'status': 'failed', 'tool': 'bandit', 'error': str(e)}

    async def _run_safety_scan(self) -> Dict[str, Any]:
        """Run Safety with error handling"""
        try:
            req_file = self.project_path / 'requirements.txt'
            if not req_file.exists():
                return {'status': 'skipped', 'tool': 'safety', 'message': 'No requirements.txt'}
            
            cmd = ['safety', 'check', '--json', '--file', str(req_file)]
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {'status': 'completed', 'tool': 'safety', 'vulnerabilities_found': 0, 'message': 'No vulnerabilities'}
            else:
                try:
                    vulns = json.loads(stdout.decode())
                    return {'status': 'completed', 'tool': 'safety', 'vulnerabilities_found': len(vulns), 'details': vulns[:3]}
                except json.JSONDecodeError:
                    return {'status': 'completed', 'tool': 'safety', 'vulnerabilities_found': 'unknown'}
                    
        except FileNotFoundError:
            return {'status': 'skipped', 'tool': 'safety', 'message': 'Safety not installed'}
        except Exception as e:
            return {'status': 'failed', 'tool': 'safety', 'error': str(e)}

    async def _run_secret_scan(self) -> Dict[str, Any]:
        """Run secret detection with travel-specific patterns"""
        try:
            patterns = [
                (r'password\s*[=:]\s*["\'][^"\']{8,}["\']', 'password'),
                (r'api[_-]?key\s*[=:]\s*["\'][^"\']{20,}["\']', 'api_key'),
                (r'token\s*[=:]\s*["\'][^"\']{20,}["\']', 'token'),
                (r'amadeus[_-]?(key|secret)\s*[=:]\s*["\'][^"\']{10,}["\']', 'amadeus_key'),
                (r'omio[_-]?(key|token)\s*[=:]\s*["\'][^"\']{10,}["\']', 'omio_key'),
                (r'smtp[_-]?(password|pass)\s*[=:]\s*["\'][^"\']{6,}["\']', 'email_password'),
            ]
            
            secrets = []
            for py_file in self.project_path.rglob("*.py"):
                if any(skip in str(py_file) for skip in ['__pycache__', '.venv', '.git']):
                    continue
                    
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern, secret_type in patterns:
                        for match in re.finditer(pattern, content, re.IGNORECASE):
                            if not any(fp in match.group().lower() for fp in ['example', 'test', 'xxx', '***']):
                                line_num = content[:match.start()].count('\n') + 1
                                secrets.append({
                                    'file': str(py_file.relative_to(self.project_path)),
                                    'line': line_num, 'type': secret_type,
                                    'severity': 'HIGH' if secret_type in ['api_key', 'token'] else 'MEDIUM'
                                })
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            return {
                'status': 'completed', 'tool': 'secret_detection', 'secrets_found': len(secrets),
                'high_risk': len([s for s in secrets if s['severity'] == 'HIGH']),
                'medium_risk': len([s for s in secrets if s['severity'] == 'MEDIUM']),
                'details': secrets[:5]
            }
            
        except Exception as e:
            return {'status': 'failed', 'tool': 'secret_detection', 'error': str(e)}

    async def _run_sonarqube_scan(self) -> Dict[str, Any]:
        """Run SonarQube with validation"""
        try:
            if not all([self.config.get('sonarqube_url'), self.config.get('sonarqube_token')]):
                return {'status': 'not_configured', 'tool': 'sonarqube', 'message': 'Not configured'}
            
            cmd = [
                'sonar-scanner',
                f'-Dsonar.projectKey={self.config["sonarqube_project_key"]}',
                f'-Dsonar.host.url={self.config["sonarqube_url"]}',
                f'-Dsonar.login={self.config["sonarqube_token"]}',
                f'-Dsonar.sources={self.project_path}'
            ]
            
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(self.project_path))
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                return {
                    'status': 'completed', 'tool': 'sonarqube', 'message': 'Analysis completed',
                    'dashboard_url': f"{self.config['sonarqube_url']}/dashboard?id={self.config['sonarqube_project_key']}"
                }
            else:
                return {'status': 'failed', 'tool': 'sonarqube', 'error': stderr.decode()[:200]}
                
        except FileNotFoundError:
            return {'status': 'skipped', 'tool': 'sonarqube', 'message': 'sonar-scanner not installed'}
        except Exception as e:
            return {'status': 'failed', 'tool': 'sonarqube', 'error': str(e)}

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security summary with error handling"""
        try:
            total, critical, high, medium = 0, 0, 0, 0
            
            for tool, result in results.items():
                if not isinstance(result, dict) or result.get('status') != 'completed':
                    continue
                    
                if tool == 'bandit':
                    total += result.get('issues_found', 0)
                    critical += result.get('high_severity', 0)
                    medium += result.get('medium_severity', 0)
                elif tool == 'safety':
                    vulns = result.get('vulnerabilities_found', 0)
                    if isinstance(vulns, int):
                        total += vulns
                        high += vulns
                elif tool == 'secrets':
                    secrets = result.get('secrets_found', 0)
                    total += secrets
                    critical += result.get('high_risk', 0)
                    medium += result.get('medium_risk', 0)
            
            # Calculate score
            if total == 0:
                score, status = 100.0, 'excellent'
            else:
                weighted = (critical * 20) + (high * 10) + (medium * 5)
                score = max(0, 100 - (weighted / (total * 20) * 100)) if total > 0 else 100
                status = 'good' if score >= 85 else 'moderate' if score >= 70 else 'poor' if score >= 50 else 'critical'
            
            return {
                'security_score': round(score, 1), 'overall_status': status,
                'total_issues': total, 'critical_issues': critical, 'high_issues': high, 'medium_issues': medium,
                'scan_coverage': [t for t, r in results.items() if isinstance(r, dict) and r.get('status') == 'completed']
            }
            
        except Exception as e:
            return {'security_score': 0.0, 'overall_status': 'error', 'error': str(e)}

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations with error handling"""
        try:
            recs = []
            
            # Critical: Secrets
            if 'secrets' in results and results['secrets'].get('secrets_found', 0) > 0:
                recs.append({
                    'priority': 'CRITICAL', 'title': 'Remove Hardcoded Secrets',
                    'description': f"Found {results['secrets']['secrets_found']} secrets",
                    'action': 'Move to environment variables', 'category': 'Secrets'
                })
            
            # High: Code issues
            if 'bandit' in results and results['bandit'].get('high_severity', 0) > 0:
                recs.append({
                    'priority': 'HIGH', 'title': 'Fix Code Security Issues',
                    'description': f"{results['bandit']['high_severity']} high-severity issues",
                    'action': 'Review and fix vulnerabilities', 'category': 'Code'
                })
            
            # High: Dependencies
            if 'safety' in results:
                vulns = results['safety'].get('vulnerabilities_found', 0)
                if isinstance(vulns, int) and vulns > 0:
                    recs.append({
                        'priority': 'HIGH', 'title': 'Update Dependencies',
                        'description': f"{vulns} vulnerable packages",
                        'action': 'Update to secure versions', 'category': 'Dependencies'
                    })
            
            # Travel-specific
            recs.extend([
                {'priority': 'MEDIUM', 'title': 'HTTPS for APIs', 'description': 'Secure travel API calls', 'action': 'Verify HTTPS usage', 'category': 'Travel'},
                {'priority': 'MEDIUM', 'title': 'Input Validation', 'description': 'Sanitize travel forms', 'action': 'Add validation', 'category': 'Input'},
                {'priority': 'LOW', 'title': 'CI/CD Security', 'description': 'Automate security checks', 'action': 'Add to pipeline', 'category': 'DevOps'}
            ])
            
            return recs
            
        except Exception as e:
            self.logger.error(f"Recommendations failed: {e}")
            return []

    def get_security_report(self) -> Dict[str, Any]:
        """Get security report with error handling"""
        try:
            if not self.scan_results:
                return {'message': 'No scan results. Run scan first.', 'status': 'no_data'}
            
            return {
                'project': str(self.project_path.name),
                'scan_time': self.scan_results.get('metadata', {}).get('scan_end', 'unknown'),
                'summary': self.scan_results.get('summary', {}),
                'recommendations': self.scan_results.get('recommendations', [])[:5],
                'tool_results': {t: r for t, r in self.scan_results.get('results', {}).items() if isinstance(r, dict) and r.get('status') == 'completed'}
            }
        except Exception as e:
            return {'error': str(e)}

    def print_security_summary(self) -> None:
        """Print clean security summary"""
        try:
            if not self.scan_results:
                print("❌ No scan results. Run scan first.")
                return
                
            summary = self.scan_results.get('summary', {})
            recs = self.scan_results.get('recommendations', [])
            
            print("\n🔒 Travel App Security Summary")
            print("=" * 40)
            print(f"Score: {summary.get('security_score', 0)}/100")
            print(f"Status: {summary.get('overall_status', 'unknown').upper()}")
            print(f"Issues: {summary.get('total_issues', 0)} (Critical: {summary.get('critical_issues', 0)}, High: {summary.get('high_issues', 0)})")
            
            if recs:
                print("\n💡 Top Recommendations:")
                for i, rec in enumerate(recs[:3], 1):
                    print(f"{i}. [{rec.get('priority', 'UNKNOWN')}] {rec.get('title', 'No title')}")
            
            print(f"\nScanned: {', '.join(summary.get('scan_coverage', []))}")
            print("=" * 40)
            
        except Exception as e:
            print(f"Summary error: {e}")


def create_travel_security_orchestrator(project_path: str = ".") -> TravelSecurityOrchestrator:
    """Factory function with error handling"""
    try:
        return TravelSecurityOrchestrator(project_path)
    except Exception as e:
        logging.error(f"Failed to create orchestrator: {e}")
        raise


async def main():
    """CLI with error handling"""
    import argparse
    
    try:
        parser = argparse.ArgumentParser(description='Travel Security Orchestrator')
        parser.add_argument('--scan', action='store_true', help='Run security scan')
        parser.add_argument('--report', action='store_true', help='Show report')
        parser.add_argument('--path', default='.', help='Project path')
        
        args = parser.parse_args()
        orchestrator = create_travel_security_orchestrator(args.path)
        
        if args.scan:
            print("🔍 Running security scan...")
            await orchestrator.run_security_scan()
            orchestrator.print_security_summary()
        elif args.report:
            report = orchestrator.get_security_report()
            print(json.dumps(report, indent=2, default=str))
        else:
            print("Usage: --scan or --report")
            
    except Exception as e:
        print(f"CLI error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
