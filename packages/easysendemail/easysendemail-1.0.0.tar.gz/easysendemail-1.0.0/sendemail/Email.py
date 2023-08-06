# coding: utf8

from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEBase, MIMEMultipart
from email.utils import parseaddr, formataddr
import smtplib


class SendEmail:
    def __init__(self, sender, receiver, smtp, password, port=25, filepath=None, filename=None, subject=None, content=None):
        self.sender = sender
        self.receiver = receiver
        self.smtp = smtp
        self.port = port
        self.password = password
        self.filepath = filepath
        self.filename = filename
        self.subject = subject
        self.content = content

    def send_email(self):
        def _format_addr(s):
            name, addr = parseaddr(s)
            return formataddr(( \
                Header(name, 'utf-8').encode(), \
                addr.encode('utf-8') if isinstance(addr, unicode) else addr))

        msg = MIMEMultipart()
        msg['From'] = _format_addr(u'<%s>' % self.sender)
        msg['To'] = _format_addr(u'<%s>' % self.receiver)
        if self.subject:
            msg['Subject'] = Header(u'%s' % self.subject, 'utf-8').encode()

        msg.attach(MIMEText(self.content, 'plain', 'utf-8'))
        if self.filepath:
            att = MIMEText(open(self.filepath, 'rb').read(), 'base64', 'utf-8')
            att["Content-Type"] = 'application/octet-stream'
            att["Content-Disposition"] = 'attachment; filename=%s' % self.filename

            msg.attach(att)

        server = smtplib.SMTP(self.smtp, self.port)
        server.login(self.sender, self.password)
        server.sendmail(self.sender, [self.receiver], msg.as_string())
        server.quit()
