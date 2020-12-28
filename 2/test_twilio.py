 
# put your own credentials here 
ACCOUNT_SID = "AC0c8290c2ea6e80979b9d419029e25c4f" 
AUTH_TOKEN = "9f45c5b4dd1428470aaa4e7ae5fa4707" 
 
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
 
client.messages.create(
    to="16318355443", 
    from_="+16319542023", 
    body="测试",  
    #media_url=r'http://www.clker.com/cliparts/d/b/2/7/13440412741381521061sunflower1-md.png'
)



import smtplib
smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
type(smtpObj)

smtpObj.ehlo()
smtpObj.starttls()

MY_SECRET_PASSWORD = input('Enter your ps: ')
smtpObj.login('wwhome16@gmail.com', MY_SECRET_PASSWORD)



smtpObj.sendmail('wwhome16@gmail.com', 'yuyangfirst@gmail.com',
'Subject: So long.\nDear Alice, so long and thanks for all the fish. Sincerely,dsasd \
sdfsdfsdfs fsdfsdfsd')
{}



smtpObj.quit()import os
