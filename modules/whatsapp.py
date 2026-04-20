import config
import pywhatkit as wp
import time

class WhatsappModule:
    def __init__(self):
        pass

    def send_message(self,phone,message):
        try:
            wp.sendwhatmsg_instantly(
                phone_no=phone, 
                message=message, 
                wait_time=15, 
                tab_close=True
            )
            return "Message Sent Successfully"
        except:
            return "Unable to send message.."