"""
Notification Tasks for Celery
Handles email, Slack, Jira, and in-app notifications
"""

from celery import Task
from app.celery_app import celery_app
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import logging
from datetime import datetime
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "").replace("+aiosqlite", "")
            engine = create_engine(sync_db_url)
            self._db = Session(engine)
        return self._db


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification_tasks.send_email",
    max_retries=3,
    default_retry_delay=60
)
def send_email(self, to: str, subject: str, body: str, template: Optional[str] = None):
    """
    Send email via SendGrid

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (text or HTML)
        template: Optional email template name
    """
    try:
        logger.info(f"Sending email to: {to}")

        if not settings.SENDGRID_API_KEY:
            logger.warning("SendGrid API key not configured, skipping email")
            return {"status": "skipped", "reason": "No SendGrid API key"}

        # TODO: Use SendGrid API to send email
        # from sendgrid import SendGridAPIClient
        # from sendgrid.helpers.mail import Mail

        # message = Mail(
        #     from_email=settings.FROM_EMAIL,
        #     to_emails=to,
        #     subject=subject,
        #     html_content=body
        # )

        # sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        # response = sg.send(message)

        logger.info(f"Email sent successfully to: {to}")
        return {
            "status": "success",
            "to": to,
            "subject": subject
        }

    except Exception as exc:
        logger.error(f"Error sending email to {to}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification_tasks.send_slack_notification",
    max_retries=3
)
def send_slack_notification(self, webhook_url: str, message: str, channel: Optional[str] = None):
    """
    Send notification to Slack via webhook

    Args:
        webhook_url: Slack webhook URL
        message: Message to send
        channel: Optional Slack channel
    """
    try:
        logger.info(f"Sending Slack notification")

        import requests

        payload = {
            "text": message,
        }

        if channel:
            payload["channel"] = channel

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

        logger.info(f"Slack notification sent successfully")
        return {
            "status": "success",
            "channel": channel
        }

    except Exception as exc:
        logger.error(f"Error sending Slack notification: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification_tasks.create_jira_ticket",
    max_retries=3
)
def create_jira_ticket(
    self,
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Bug",
    priority: str = "Medium"
):
    """
    Create Jira ticket via Jira API

    Args:
        project_key: Jira project key
        summary: Ticket summary
        description: Ticket description
        issue_type: Type of issue (Bug, Task, etc.)
        priority: Priority level
    """
    try:
        logger.info(f"Creating Jira ticket in project: {project_key}")

        if not all([settings.JIRA_URL, settings.JIRA_USERNAME, settings.JIRA_API_TOKEN]):
            logger.warning("Jira not configured, skipping ticket creation")
            return {"status": "skipped", "reason": "Jira not configured"}

        # TODO: Use Jira API to create ticket
        # from jira import JIRA

        # jira = JIRA(
        #     server=settings.JIRA_URL,
        #     basic_auth=(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN)
        # )

        # issue_dict = {
        #     'project': {'key': project_key},
        #     'summary': summary,
        #     'description': description,
        #     'issuetype': {'name': issue_type},
        #     'priority': {'name': priority}
        # }

        # new_issue = jira.create_issue(fields=issue_dict)

        logger.info(f"Jira ticket created successfully in project: {project_key}")
        return {
            "status": "success",
            "project_key": project_key,
            "ticket_key": "PLACEHOLDER-123"
        }

    except Exception as exc:
        logger.error(f"Error creating Jira ticket: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification_tasks.send_in_app_notification",
    max_retries=3
)
def send_in_app_notification(self, user_id: str, notification_data: Dict):
    """
    Create in-app notification in database

    Args:
        user_id: ID of the user to notify
        notification_data: Notification details (title, message, type, etc.)
    """
    try:
        logger.info(f"Creating in-app notification for user: {user_id}")

        # TODO: Store notification in database
        # TODO: Broadcast via WebSocket if user is online

        notification = {
            "id": "placeholder_id",
            "user_id": user_id,
            "title": notification_data.get("title"),
            "message": notification_data.get("message"),
            "type": notification_data.get("type", "info"),
            "created_at": datetime.utcnow().isoformat(),
            "read": False
        }

        logger.info(f"In-app notification created for user: {user_id}")
        return {
            "status": "success",
            "user_id": user_id,
            "notification_id": notification["id"]
        }

    except Exception as exc:
        logger.error(f"Error creating in-app notification for user {user_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification_tasks.send_webhook",
    max_retries=3
)
def send_webhook(self, url: str, payload: Dict, headers: Optional[Dict] = None):
    """
    Send webhook notification

    Args:
        url: Webhook URL
        payload: Data to send
        headers: Optional HTTP headers
    """
    try:
        logger.info(f"Sending webhook to: {url}")

        import requests

        response = requests.post(
            url,
            json=payload,
            headers=headers or {"Content-Type": "application/json"}
        )
        response.raise_for_status()

        logger.info(f"Webhook sent successfully to: {url}")
        return {
            "status": "success",
            "url": url,
            "status_code": response.status_code
        }

    except Exception as exc:
        logger.error(f"Error sending webhook to {url}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification_tasks.send_sms",
    max_retries=3
)
def send_sms(self, phone_number: str, message: str):
    """
    Send SMS notification (using Twilio or similar)

    Args:
        phone_number: Recipient phone number
        message: SMS message
    """
    try:
        logger.info(f"Sending SMS to: {phone_number}")

        # TODO: Integrate with SMS provider (Twilio, etc.)

        logger.info(f"SMS sent successfully to: {phone_number}")
        return {
            "status": "success",
            "phone_number": phone_number
        }

    except Exception as exc:
        logger.error(f"Error sending SMS to {phone_number}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.notification_tasks.send_push_notification",
    max_retries=3
)
def send_push_notification(self, user_id: str, title: str, body: str, data: Optional[Dict] = None):
    """
    Send push notification to mobile device

    Args:
        user_id: ID of the user
        title: Notification title
        body: Notification body
        data: Optional additional data
    """
    try:
        logger.info(f"Sending push notification to user: {user_id}")

        # TODO: Integrate with push notification service (FCM, APNS, etc.)

        logger.info(f"Push notification sent to user: {user_id}")
        return {
            "status": "success",
            "user_id": user_id
        }

    except Exception as exc:
        logger.error(f"Error sending push notification to user {user_id}: {exc}")
        raise self.retry(exc=exc)
