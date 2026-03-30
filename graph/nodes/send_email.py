import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from graph.state import State

logger = logging.getLogger(__name__)


def send_email(state: State) -> dict:
    """通过 Gmail SMTP 发送邮件。"""
    sender = os.environ["GMAIL_ADDRESS"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = "woodywang20000822@gmail.com"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = state["subject"]
    msg["From"] = sender
    msg["To"] = recipient

    # 纯文本备用 + HTML 正文
    msg.attach(MIMEText(state["markdown_content"], "plain", "utf-8"))
    msg.attach(MIMEText(state["html_content"], "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    logger.info("邮件已发送: %s -> %s", state["subject"], recipient)
    return {}
