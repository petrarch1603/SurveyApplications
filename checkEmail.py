import email
import imaplib
import os
import smtplib
from secrets import *
import datetime as DT

today = DT.date.today()
week_ago = today - DT.timedelta(days=7)
week_ago = (week_ago.strftime('%d-%b-%Y'))
week_ago_since = ('(SINCE ' + week_ago + ')')
print(week_ago_since)
ORG_EMAIL = "@gmail.com"
FROM_EMAIL = "pmcgranaghan.jacobs" + ORG_EMAIL
FROM_PWD = GMAIL_PWD
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT = 993
detach_dir = '.'
target_subject = 'SH7'


def checkemail():
    senders = []
    try:
        imapSession = imaplib.IMAP4_SSL('imap.gmail.com')
        typ, accountDetails = imapSession.login(FROM_EMAIL, FROM_PWD)
        imapSession.select('inbox')
        typ, data = imapSession.search(None, '(UNSEEN)')


        # Iterating over all emails
        for msgId in data[0].split():
            typ, messageParts = imapSession.fetch(msgId, '(BODY.PEEK[HEADER])') # PEEK keeps it from being marked as read

            emailBody = messageParts[0][1]
            mail = email.message_from_bytes(emailBody)
            if (mail['subject']) == target_subject:
                typ, messageParts = imapSession.fetch(msgId, '(RFC822)')
                for part in mail.walk():
                    if part.get_content_maintype() == 'multipart/mixed':
                        print(part)
                        print(part.get_filename())
                        continue
                    if part.get('Content-Disposition') is None:
                        print(part.as_string())
                        continue
                    if part.get_filename()[-3:] == 'jpg':
                        file_Name = part.get_filename()
                        from_str = mail['from']
                        from_email = from_str[from_str.find("<") + 1:from_str.find(">")]
                        senders.append(from_email)

        if bool(file_Name):
            filePath = os.path.join(detach_dir, file_Name)
            if not os.path.isfile(filePath):
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
        else:
            print("No File_name")
        imapSession.close()
        imapSession.logout()
    except Exception as e:
        print(e)
    # senders is a list object of all the people who sent an email. Only the last email sent will be processed.
    return senders

print(checkemail())