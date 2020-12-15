import RPi.GPIO as GPIO
import time
import smtplib
import thread
import cred
import imaplib
import email
import os

from PCF8574 import PCF8574_GPIO
from Adafruit_LCD1602 import Adafruit_CharLCD

try:

    need_clean = False

    #Message Template
    MSG  = '\nDoor was '
    DOOR_MSG = {True:'opened', False:'closed'}


    #function to send message to phone
    def send_msg(message):
        print('send msg function')
        print('initiating server')
        server = smtplib.SMTP( cred.SMTPHOST, 587 )
        print('starting tls')
        server.starttls()
        server.login( cred.FROM, cred.PASS )
        print('sending message...')
        server.sendmail(cred.FROM, cred.TO, message)
        print('message sent!')
        server.quit()


    def read_msg(nothing):
        # connect to host using SSL
        mail = imaplib.IMAP4_SSL(cred.IMAPHOST,993)
        mail.login(cred.FROM, cred.PASS)
        mail.select('Inbox')
        type, data = mail.search(None, '(FROM "2085396059@vzwpix.com")')
        mail_ids = data[0]
        off = 0
        stop = 0 
        for num in data[0].split():
            typ, data = mail.fetch(num, '(RFC822)' )
            raw_email = data[0][1]# converts byte literal to string removing b''
            raw_email_string = raw_email.decode('utf-8')
            email_message = email.message_from_string(raw_email_string)# downloading attachments
            for part in email_message.walk():
                fileName = part.get_filename()        
                if bool(fileName):
                    filePath = os.path.join('/home/pi/', fileName)
                    if not os.path.isfile(filePath) :
                        fp = open(filePath, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()            
                        f = open(filePath, "r")
                        text = f.readline()
                        f.close()
                        os.remove(filePath)
                        text = text.replace(".", "")
                        text = text.replace(" ", "")
                        text = text.lower()
                        if text == 'off':
                            off = 1   
                        elif text == 'stop':
                            stop = 1    
                        else:
                            print('Not stopped')
                            send_msg("\nError: please type 'Stop'")
            mail.store(num, '+FLAGS', '\\Deleted') #deletes recent email
        #cleans email trash
        mail.expunge()
        mail.close()
        if off == 1:
            GPIO.output(buzz,GPIO.LOW)
            print('Sucessfully Restarted') 
            lcd.setCursor(0,0)
            lcd.message('Alarm was restarted')
	        send_msg("\nAlarm restarted")
	if stop == 1:
        GPIO.output(buzz,GPIO.LOW)
        print('Successfully stopped') 
	    send_msg("\nAlarm Deactivated") 
	    lcd.clear() 
	    os._exit(0)	


    def while_read(nothing):
        while True:
            time.sleep(10)
            thread.start_new_thread(read_msg,("",))

    #Initializing GPIO
    print('Setting up hardware...')
    PIN = 36
    buzz = 38 
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(buzz, GPIO.OUT)
    #next_state to check for to send message
    next_state = True

    need_clean = True

    PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
    PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
    # Create PCF8574 GPIO adapter.
    try:
        mcp = PCF8574_GPIO(PCF8574_address)
    except:
        try:
            mcp = PCF8574_GPIO(PCF8574A_address)
        except:
            print ('I2C Address Error !')
            exit(1)
    # Create LCD, passing in MCP GPIO adapter.
    lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)

    #Running actual program
    print('Ready!')
    mcp.output(3,1)     # turn on LCD backlight
    lcd.begin(16,2)     # set number of LCD lines and columns
    thread.start_new_thread(send_msg, ("\nAlarm Activated\n\nType 'stop' to stop deactivate it",))
    off = 0
    #Run infinitely
  
    thread.start_new_thread(while_read,("",))

    while True:
        
        #Check for next state
        if GPIO.input(PIN) == next_state:
            doorTime = time.strftime('%I:%M:%S %p')
            message = "Door was " + DOOR_MSG[next_state] + "\n\nType 'off' to restart alarm" 
            lcd.setCursor(0,0)
            lcd.message(message + '\n at ' + doorTime) 
            print(message) 
            GPIO.output(buzz,GPIO.HIGH) 
            #Send message on different thread
            thread.start_new_thread(send_msg, ("\n" + message,))
            #Negate next_state
            next_state = not next_state
        time.sleep(0.3)
except KeyboardInterrupt:
    print('KeyboardInterrupt')
    GPIO.output(buzz,GPIO.LOW) 
    GPIO.cleanup()
    lcd.clear() 
    need_clean = False
    
#cleans up necessary hardware
if need_clean:
    lcd.clear()
    GPIO.cleanup() #For normal exit
print('\nEnd!')
