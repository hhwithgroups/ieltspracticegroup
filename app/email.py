# from sae.mail import EmailMessage
from flask import render_template
from . import app

def send_email(recv_addr, subject, bd_tmplt, **kargs):
    pass
    '''
    m = EmailMessage()
    m.to = recv_addr
    m.subject = subject
    m.html = render_template(bd_tmplt+'.html', **kargs)
    m.body = render_template(bd_tmplt+'.txt', **kargs)
    m.smtp = (app.config['SMTP_HOST'],
              app.config['SMTP_PORT'],
              app.config['SMTP_USER'],
              app.config['SMTP_PASS'],
              True)
    m.send()
    '''
