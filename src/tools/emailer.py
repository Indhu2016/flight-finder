"""
Advanced email notification system with comprehensive formatting and security.

This module provides robust email functionality with support for multiple templates,
security features, and professional-grade email formatting following SOLID principles.
"""

import smtplib
import ssl
import socket
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.utils import formataddr
from email import encoders
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from abc import ABC, abstractmethod

from src.tools.formatters import html_table, RouteFormatter, FormattingOptions, OutputFormat
from src.tools.security import validate_email, sanitize_city_name, validate_date
from src.config import ConfigurationManager

logger = logging.getLogger(__name__)


class EmailTemplate(Enum):
    """Available email templates."""
    ROUTE_SUMMARY = "route_summary"
    ITINERARY = "itinerary"
    PRICE_ALERT = "price_alert"
    BOOKING_CONFIRMATION = "booking_confirmation"
    TRAVEL_REMINDER = "travel_reminder"
    ERROR_NOTIFICATION = "error_notification"


class EmailPriority(Enum):
    """Email priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class EmailRecipient:
    """Email recipient information."""
    email: str
    name: Optional[str] = None
    type: str = "to"  # to, cc, bcc
    
    def __post_init__(self):
        """Validate email address."""
        if not validate_email(self.email):
            raise ValueError(f"Invalid email address: {self.email}")
    
    @property
    def formatted_address(self) -> str:
        """Get formatted email address."""
        if self.name:
            return formataddr((self.name, self.email))
        return self.email


@dataclass
class EmailAttachment:
    """Email attachment information."""
    filename: str
    content: Union[str, bytes]
    mime_type: str = "application/octet-stream"
    
    @property
    def size_mb(self) -> float:
        """Get attachment size in MB."""
        if isinstance(self.content, str):
            return len(self.content.encode('utf-8')) / (1024 * 1024)
        return len(self.content) / (1024 * 1024)


@dataclass
class EmailMessage:
    """Comprehensive email message structure."""
    recipients: List[EmailRecipient]
    subject: str
    template: EmailTemplate
    data: Dict[str, Any] = field(default_factory=dict)
    priority: EmailPriority = EmailPriority.NORMAL
    attachments: List[EmailAttachment] = field(default_factory=list)
    reply_to: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    @property
    def to_recipients(self) -> List[EmailRecipient]:
        """Get 'to' recipients."""
        return [r for r in self.recipients if r.type == "to"]
    
    @property
    def cc_recipients(self) -> List[EmailRecipient]:
        """Get 'cc' recipients."""
        return [r for r in self.recipients if r.type == "cc"]
    
    @property
    def bcc_recipients(self) -> List[EmailRecipient]:
        """Get 'bcc' recipients."""
        return [r for r in self.recipients if r.type == "bcc"]
    
    @property
    def all_email_addresses(self) -> List[str]:
        """Get all email addresses."""
        return [r.email for r in self.recipients]
    
    @property
    def total_attachment_size_mb(self) -> float:
        """Get total attachment size in MB."""
        return sum(att.size_mb for att in self.attachments)


class BaseEmailRenderer(ABC):
    """Abstract base class for email template renderers."""
    
    def __init__(self, template: EmailTemplate):
        self.template = template
    
    @abstractmethod
    def render_subject(self, data: Dict[str, Any]) -> str:
        """Render email subject line."""
        pass
    
    @abstractmethod
    def render_plain_text(self, data: Dict[str, Any]) -> str:
        """Render plain text email body."""
        pass
    
    @abstractmethod
    def render_html(self, data: Dict[str, Any]) -> str:
        """Render HTML email body."""
        pass
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate template data."""
        return True


class ItineraryRenderer(BaseEmailRenderer):
    """Renderer for travel itinerary emails."""
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate itinerary data."""
        required_fields = ["origin", "destination", "date", "routes"]
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False
        return True
    
    def render_subject(self, data: Dict[str, Any]) -> str:
        """Render itinerary subject."""
        origin = sanitize_city_name(data.get("origin", "Unknown"))
        destination = sanitize_city_name(data.get("destination", "Unknown"))
        date = data.get("date", "Unknown")
        
        return f"Your travel options: {origin} → {destination} ({date})"
    
    def render_plain_text(self, data: Dict[str, Any]) -> str:
        """Render plain text itinerary."""
        origin = sanitize_city_name(data.get("origin", "Unknown"))
        destination = sanitize_city_name(data.get("destination", "Unknown"))
        date = data.get("date", "Unknown")
        routes = data.get("routes", [])
        
        # Use the advanced formatter for plain text
        formatter = RouteFormatter(FormattingOptions(
            detail_level="detailed",
            max_routes=5,
            include_analytics=True
        ))
        
        body = f"Best routes for {origin} → {destination} on {date}\n\n"
        body += formatter.format_routes(routes)
        body += f"\n\nGenerated by Smart Travel Optimizer at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return body
    
    def render_html(self, data: Dict[str, Any]) -> str:
        """Render HTML itinerary."""
        origin = sanitize_city_name(data.get("origin", "Unknown"))
        destination = sanitize_city_name(data.get("destination", "Unknown"))
        date = data.get("date", "Unknown")
        routes = data.get("routes", [])
        
        # Use the HTML formatter
        formatter = RouteFormatter(FormattingOptions(
            format_type=OutputFormat.HTML,
            max_routes=5,
            include_analytics=True
        ))
        
        routes_html = formatter.format_routes(routes)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Travel Itinerary</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; 
                    color: #333; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px;
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center; 
                    border-radius: 10px 10px 0 0;
                    margin: -20px -20px 20px -20px;
                }}
                .header h1 {{ margin: 0; font-size: 2em; }}
                .header h2 {{ margin: 10px 0 0 0; font-weight: 300; }}
                .content {{ padding: 20px 0; }}
                .footer {{ 
                    background-color: #f8f9fa; 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 0.9em; 
                    color: #666;
                    border-radius: 0 0 10px 10px;
                    margin: 20px -20px -20px -20px;
                }}
                .timestamp {{ font-style: italic; margin-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌍 Travel Itinerary</h1>
                <h2>{origin} → {destination}</h2>
                <p>Travel Date: {date}</p>
            </div>
            
            <div class="content">
                {routes_html}
            </div>
            
            <div class="footer">
                <p><strong>Smart Travel Optimizer</strong></p>
                <div class="timestamp">
                    Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


class RouteSummaryRenderer(BaseEmailRenderer):
    """Renderer for route summary emails."""
    
    def render_subject(self, data: Dict[str, Any]) -> str:
        """Render route summary subject."""
        origin = data.get("origin", "Unknown")
        destination = data.get("destination", "Unknown")
        route_count = len(data.get("routes", []))
        
        return f"Travel Routes: {origin} → {destination} ({route_count} options found)"
    
    def render_plain_text(self, data: Dict[str, Any]) -> str:
        """Render plain text route summary."""
        formatter = RouteFormatter(FormattingOptions(
            detail_level="summary",
            max_routes=10,
            include_analytics=True,
            highlight_best=True
        ))
        
        return formatter.format_routes(data.get("routes", []))
    
    def render_html(self, data: Dict[str, Any]) -> str:
        """Render HTML route summary."""
        formatter = RouteFormatter(FormattingOptions(
            format_type=OutputFormat.HTML,
            detail_level="detailed",
            max_routes=10,
            include_analytics=True,
            highlight_best=True
        ))
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Route Summary</title>
        </head>
        <body>
            <h1>🛫 Route Summary</h1>
            {formatter.format_routes(data.get("routes", []))}
            <hr>
            <p><em>Generated by Smart Travel Optimizer</em></p>
        </body>
        </html>
        """


class EmailRendererFactory:
    """Factory for creating email template renderers."""
    
    _renderers = {
        EmailTemplate.ITINERARY: ItineraryRenderer,
        EmailTemplate.ROUTE_SUMMARY: RouteSummaryRenderer,
    }
    
    @classmethod
    def create_renderer(cls, template: EmailTemplate) -> BaseEmailRenderer:
        """Create renderer for the specified template."""
        renderer_class = cls._renderers.get(template, RouteSummaryRenderer)
        return renderer_class(template)
    
    @classmethod
    def register_renderer(cls, template: EmailTemplate, renderer_class: type):
        """Register a custom renderer."""
        cls._renderers[template] = renderer_class


class SmartEmailService:
    """Advanced email service with enterprise-grade features."""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config = config_manager
        self.sent_count = 0
        self.failed_count = 0
        self.smtp_config = config_manager.get_smtp_config()
        
        # Validate SMTP configuration
        if not self._validate_smtp_config():
            logger.warning("SMTP configuration incomplete. Email service disabled.")
    
    def _validate_smtp_config(self) -> bool:
        """Validate SMTP configuration."""
        required_fields = ['host', 'port', 'username', 'password']
        smtp_dict = self.smtp_config.__dict__
        
        for field in required_fields:
            if not smtp_dict.get(field):
                logger.error(f"Missing SMTP configuration: {field}")
                return False
        
        return True
    
    def send_email(self, message: EmailMessage) -> bool:
        """Send a comprehensive email message."""
        if not self._validate_smtp_config():
            logger.error("Cannot send email: SMTP not configured")
            return False
        
        try:
            # Validate message
            if not self._validate_message(message):
                return False
            
            # Render email content
            renderer = EmailRendererFactory.create_renderer(message.template)
            
            if not renderer.validate_data(message.data):
                logger.error("Email template data validation failed")
                return False
            
            # Create MIME message
            mime_message = self._create_mime_message(message, renderer)
            
            # Send via SMTP
            self._send_via_smtp(mime_message, message.all_email_addresses)
            
            self.sent_count += 1
            logger.info(f"Email sent successfully to {len(message.all_email_addresses)} recipients")
            return True
            
        except Exception as e:
            self.failed_count += 1
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _validate_message(self, message: EmailMessage) -> bool:
        """Validate email message."""
        if not message.recipients:
            logger.error("No recipients specified")
            return False
        
        if len(message.recipients) > 50:  # Reasonable limit
            logger.error(f"Too many recipients: {len(message.recipients)}")
            return False
        
        if message.total_attachment_size_mb > 25:  # 25MB limit
            logger.error(f"Attachments too large: {message.total_attachment_size_mb}MB")
            return False
        
        return True
    
    def _create_mime_message(self, message: EmailMessage, renderer: BaseEmailRenderer) -> MIMEMultipart:
        """Create MIME message."""
        # Render content
        subject = renderer.render_subject(message.data)
        plain_body = renderer.render_plain_text(message.data)
        html_body = renderer.render_html(message.data)
        
        # Create multipart message
        mime_msg = MIMEMultipart("alternative")
        
        # Set headers
        mime_msg["From"] = formataddr((
            self.smtp_config.from_name, 
            self.smtp_config.username
        ))
        
        if message.to_recipients:
            mime_msg["To"] = ", ".join([r.formatted_address for r in message.to_recipients])
        
        if message.cc_recipients:
            mime_msg["Cc"] = ", ".join([r.formatted_address for r in message.cc_recipients])
        
        mime_msg["Subject"] = subject
        
        if message.reply_to:
            mime_msg["Reply-To"] = message.reply_to
        
        # Set priority
        if message.priority == EmailPriority.HIGH:
            mime_msg["X-Priority"] = "1"
            mime_msg["X-MSMail-Priority"] = "High"
        elif message.priority == EmailPriority.URGENT:
            mime_msg["X-Priority"] = "1"
            mime_msg["X-MSMail-Priority"] = "High"
            mime_msg["Importance"] = "high"
        elif message.priority == EmailPriority.LOW:
            mime_msg["X-Priority"] = "5"
            mime_msg["X-MSMail-Priority"] = "Low"
        
        # Add custom headers
        for key, value in message.custom_headers.items():
            mime_msg[key] = value
        
        # Add body parts
        mime_msg.attach(MIMEText(plain_body, "plain"))
        mime_msg.attach(MIMEText(html_body, "html"))
        
        # Add attachments
        for attachment in message.attachments:
            self._add_attachment(mime_msg, attachment)
        
        return mime_msg
    
    def _add_attachment(self, mime_msg: MIMEMultipart, attachment: EmailAttachment):
        """Add attachment to MIME message."""
        part = MIMEBase("application", "octet-stream")
        
        if isinstance(attachment.content, str):
            part.set_payload(attachment.content.encode('utf-8'))
        else:
            part.set_payload(attachment.content)
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {attachment.filename}"
        )
        
        mime_msg.attach(part)
    
    def _send_via_smtp(self, mime_message: MIMEMultipart, recipients: List[str]):
        """Send MIME message via SMTP."""
        context = ssl.create_default_context()
        
        with smtplib.SMTP(self.smtp_config.host, self.smtp_config.port, timeout=30) as server:
            server.starttls(context=context)
            server.login(self.smtp_config.username, self.smtp_config.password)
            server.sendmail(self.smtp_config.username, recipients, mime_message.as_string())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get email service statistics."""
        total_attempts = self.sent_count + self.failed_count
        success_rate = (self.sent_count / total_attempts) if total_attempts > 0 else 0.0
        
        return {
            "sent_count": self.sent_count,
            "failed_count": self.failed_count,
            "success_rate": round(success_rate, 3),
            "smtp_configured": self._validate_smtp_config()
        }


# Enhanced legacy compatibility function
def send_itinerary_email(to_email: str, origin: str, destination: str, date: str, routes: List[Dict[str, Any]]):
    """Enhanced legacy function with modern implementation."""
    try:
        # Security validations
        if not validate_email(to_email):
            raise ValueError("Invalid email address format")
        
        clean_origin = sanitize_city_name(origin)
        clean_destination = sanitize_city_name(destination)
        
        if not validate_date(date):
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        
        # Create email service
        config_manager = ConfigurationManager()
        email_service = SmartEmailService(config_manager)
        
        # Create recipient
        recipient = EmailRecipient(email=to_email)
        
        # Prepare message data
        data = {
            "origin": clean_origin,
            "destination": clean_destination,
            "date": date,
            "routes": routes[:5]  # Limit routes for email size
        }
        
        # Create message
        message = EmailMessage(
            recipients=[recipient],
            subject="",  # Will be generated by renderer
            template=EmailTemplate.ITINERARY,
            data=data,
            priority=EmailPriority.NORMAL
        )
        
        # Send email
        success = email_service.send_email(message)
        
        if success:
            logger.info(f"Email sent successfully to {to_email}")
        else:
            logger.error(f"Failed to send email to {to_email}")
            
        return success
        
    except Exception as e:
        logger.error(f"Error in send_itinerary_email: {e}")
        raise


# Convenience functions
def create_itinerary_email(recipient: str, origin: str, destination: str, 
                          date: str, routes: List[Dict[str, Any]]) -> EmailMessage:
    """Create an itinerary email message."""
    return EmailMessage(
        recipients=[EmailRecipient(email=recipient)],
        subject="",  # Generated by renderer
        template=EmailTemplate.ITINERARY,
        data={
            "origin": origin,
            "destination": destination,
            "date": date,
            "routes": routes
        }
    )


def create_route_summary_email(recipients: List[str], routes: List[Dict[str, Any]], 
                              origin: str = "", destination: str = "") -> EmailMessage:
    """Create a route summary email message."""
    return EmailMessage(
        recipients=[EmailRecipient(email=email) for email in recipients],
        subject="",  # Generated by renderer
        template=EmailTemplate.ROUTE_SUMMARY,
        data={
            "origin": origin,
            "destination": destination,
            "routes": routes
        }
    )
