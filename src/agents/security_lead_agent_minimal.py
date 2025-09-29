"""Travel Security Agent - Minimal Security Analysis"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ReviewStatus(Enum):
    APPROVED = "APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"
    CRITICAL_ISSUES = "CRITICAL_ISSUES"


class NodeStatus(Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkflowNode(Enum):
    SECURITY_LEAD = "security_lead"
    REVIEW_COMPLETE = "review_complete"


@dataclass
class ReviewFeedback:
    """Security review feedback"""
    status: ReviewStatus
    summary: str
    issues: List[str]
    current_node: WorkflowNode
    next_node: WorkflowNode
    security_score: float = 0.0
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass  
class State:
    """Workflow state"""
    task_description: str
    current_node: WorkflowNode
    security_lead_status: NodeStatus
    feedback: Optional[ReviewFeedback]
    messages: List[str]
    code_content: str = ""


class SecurityLeadAgent:
    """Minimal security lead agent for travel apps"""
    
    def __init__(self, project_path: str = "."):
        self.logger = logging.getLogger('SecurityLeadAgent')
        self.project_path = project_path
        
        # Initialize security orchestrator
        try:
            from ..security_orchestrator import create_travel_security_orchestrator
            self.orchestrator = create_travel_security_orchestrator(project_path)
            self.logger.info("Security orchestrator initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            self.orchestrator = None

        self.logger.info(f"Security Lead Agent initialized for: {project_path}")

    async def analyze_security(self, state: State) -> ReviewFeedback:
        """Analyze code for security issues"""
        self.logger.info("Starting security analysis...")
        
        try:
            # Run security scan
            if self.orchestrator:
                self.logger.info("Starting security scan...")
                scan_results = await self.orchestrator.run_security_scan()
                self.logger.info("Security scan completed")
            else:
                scan_results = {'summary': {'total_issues': 0}}
                
            # Analyze results
            issues = []
            recommendations = []
            
            # Basic code analysis
            code = state.code_content.lower()
            
            # Check for secrets
            if any(pattern in code for pattern in ['password=', 'api_key=', 'token=']):
                issues.append("Found hardcoded credentials")
                recommendations.append("Move secrets to environment variables")
            
            # Check for HTTP usage
            if 'http://' in code and any(api in code for api in ['amadeus', 'omio']):
                issues.append("Insecure API calls detected")
                recommendations.append("Use HTTPS for all API calls")
            
            # Check input validation
            if 'request.' in code and 'validate' not in code:
                issues.append("Missing input validation")
                recommendations.append("Add input validation and sanitization")
            
            # Determine status
            total_issues = scan_results.get('summary', {}).get('total_issues', len(issues))
            
            if total_issues == 0:
                status = ReviewStatus.APPROVED
                summary = "No security issues found"
            elif total_issues > 2:
                status = ReviewStatus.CRITICAL_ISSUES  
                summary = f"Found {total_issues} security issues requiring attention"
            else:
                status = ReviewStatus.NEEDS_REVISION
                summary = f"Found {total_issues} security issues for review"
            
            # Calculate security score
            security_score = max(0, 100 - total_issues * 20)
            
            # Create feedback
            feedback = ReviewFeedback(
                status=status,
                summary=summary,
                issues=issues,
                current_node=WorkflowNode.SECURITY_LEAD,
                next_node=WorkflowNode.REVIEW_COMPLETE,
                security_score=security_score,
                recommendations=recommendations
            )
            
            self.logger.info(f"Security analysis completed - Status: {status}")
            return feedback
            
        except Exception as e:
            self.logger.error(f"Security analysis failed: {e}")
            return ReviewFeedback(
                status=ReviewStatus.CRITICAL_ISSUES,
                summary=f"Security analysis failed: {e}",
                issues=[f"Analysis error: {e}"],
                current_node=WorkflowNode.SECURITY_LEAD,
                next_node=WorkflowNode.REVIEW_COMPLETE,
                security_score=0.0,
                recommendations=["Fix analysis errors and retry"]
            )

    async def generate_security_report(self, feedback: ReviewFeedback) -> str:
        """Generate simple security report"""
        return f"""
Travel App Security Report
=========================

Status: {feedback.status.value}
Security Score: {feedback.security_score}/100

Summary: {feedback.summary}

Issues Found ({len(feedback.issues)}):
{chr(10).join(f"- {issue}" for issue in feedback.issues)}

Recommendations ({len(feedback.recommendations)}):
{chr(10).join(f"- {rec}" for rec in feedback.recommendations)}

Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()


# Create agent function for external use
def create_security_lead_agent(project_path: str = ".") -> SecurityLeadAgent:
    """Create security lead agent instance"""
    return SecurityLeadAgent(project_path)
