from twilio.rest import Client

def send_sms():
    account_sid = 'YOUR_ACCOUNT_SID'
    auth_token = 'YOUR_AUTH_TOKEN'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='+1XXXXXXXXXX',  # Twilio PHONE NUMBER
        body='SOS!',
        to='+YOUR_REAL_PHONE'
    )
    print(message.sid)
