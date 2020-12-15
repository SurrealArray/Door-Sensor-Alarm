# Door-Sensor-Alarm

To start the program use “python sensor.py” in the Raspberry Pi.

Structure of source code:

sensor.py
In the function send_msg(), it takes in a string parameter which is what will be sent as a text message. The way it works is that it sends the message via SMTP using my email address. To do this it must login and then send the message.
In the function read_msg(), it is made to read all messages incoming from my phone. The way it does this is by logging in to my email and filtering through messages that are only coming from my phone. It will read the most recent message and if the message is either ‘stop’ or ‘off’, it will either turn off the system or reset the alarm. Then the message is deleted so then it doesn’t get read again.
In the function while_read(), this is a function that goes to function read_msg every 10 seconds. This function is called by a created thread to ensure it can run simultaneously with the rest of the program.
The main body of the code will initialize/set up all the hardware, create the thread mentioned before, and do a while loop that will run forever until the program is exited. This loop is to check if the door sensor is changed to either open or closed. It checks it every 0.3 seconds so it updates quickly.

cred.py
This code stores all necessary for connecting to SMTP/IMAP4 servers, as well as having the email login information. It even stores the phone number that it will send a text to.
