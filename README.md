# iLumos
## RF remote control for iLumos switches using esp8266
## can also be used as a IR blaster for other devices
## based on IRBlaster here but simplified to remove temperature support and Alexa detection

### Features
- Transmits remote control codes received from Web.
- Remote control set up is in SPIFFs files which allows new set ups without changing code
- Files can be updated and deleted and viewed via web page. ip/edit or ip/edit?file=filename to view
- Built in simple web page mainly for testing. ip
- Normal use is via POST messages. ip/irjson
- Status check at ip/check (also returns list of macros)
- Update OTA to new binary firmare at ip/firmware
- Macro facility using files stored on SPIFFS
- Log recent commands ip/recent
- Incorporates WifiManager library for initial wifi set up

### Commands are sent to ip/ir with arguments
- auth (pincode or password to match built in value)
- device
	- name of remote control,
		- 'null' if just wait required,
		- 'macro' to use a macro from SPIFFS
		- 'detect' to turn alexa detect on / off
	- parameter
		- button name on remote control,
		- macro name,
		- 0/1 for detect on off
      
	- repeat (number of times to send ir code)
	- wait (mSec delay after sending code)
	- bits 0 for default, non zero overrides device definition
  
parameter is normally the name of the button on the control and the code to use is found by looking up in the buttonnames list and then finding the code for this button in the device set up.
If % is the first char of the parameter then the following code is used rather than by looking it up.
Code definitions are normally just the hex bits to send. The definition may start with #bitcount# to override the default bit count for the device. This may be used in the device table or in supplied parameters. For example, 
%#20#12345 will send 20 bits from the hex string 12345. 	
If device is macro then parameter is the name of the file in SPIFFS containing the macro
  
JSON can be posted to /irjson and contains authorisation and an array of commands using the same arguments allowing a sequence to be used using the POST to irjson
Example
```
{
	"auth":"1234",
	"commands": [
		{
			"device":"yamahaAV",
			"parameter":"hdmi4",
			"wait":"5000",
			"bits":"0",
			"repeat":"1"
		},
		{
			"device":"yamahaAV",
			"parameter":"hdmi1",
			"wait":"100",
			"bits":"0",
			"repeat":"1"
		}
	]
}
```

Macros are held in SPIFFS files with a .txt extension (e.g macro startall is in file /startall.txt). They have exactly the same content as a JSON POST. They are executed by using the device name 'macro'
and including the name of the macro file in the parameter field.

New macros can be generated by POSTING the macro content to /macro with the auth argument and an extra argument called macro containing name to be used.
Example
```
{
	"auth":"1234",
	"macro":"test1",
	"commands": [
		{
			"device":"yamahaAV",
			"parameter":"hdmi4",
			"wait":"5000",
			"bits":"0",
			"repeat":"1"
		},
		{
			"device":"yamahaAV",
			"parameter":"hdmi1",
			"wait":"100",
			"bits":"0",
			"repeat":"1"
		}
	]
}
```

Existing macros can be removed by using the same procedure but with no commands content.

### Config
- Edit iLumos.ino
	- Manual Wifi set up (Comment out WM_NAME)
		- AP_SSID Local network ssid
		- AP_PASSWORD 
		- AP_IP If static IP to be used
	- Wifi Manager set up
		- WM_NAME (ssid of wifi manager network)
		- WM_PASSWORD (password to connect)
		- On start up connect to WM_NAME network and browse to 192.168.4.1 to set up wifi
	- AP_PORT to access ir blaster web service
	- AP_AUTHID Pincode or password to authorise web commands
	- update_username user for updating firmware
	- update_password
	
### Remote controls definitions
- buttonnames.txt is a file held in SPIFFs which just holds a list of global button names across all devices
- Individual remote controls are defined in dev_devicename files. Code allows for up to 6 devices but can be increased in bitMessages.h
- dev_iLumos.txt has base data for iLumos control
- To define a device create a dev_devicename.txt file (look at supplied examples)
    - Config section holding base parameters of the remote
		- devicename e.g. lgtv 
		- H9000,L4500 pulse sequence at the start of each message
		- NULL pulse sequence at the end of each message
		- H550,L550 pulse sequence to represent a 0 bit
		- H550,L1600 pulse sequence to represent a 1 bit
		- 38000 ir modulation frequency
		- 0 used to do special encoding like in rc6
		- 100 gap in msec between repeat messages
		- 33 number of bits to transmit
		- 1 minimum number of repeats of message
		- 0 used to control toggling bits in rc codes
		- 20DF nec address which may be prepended to messages if not defined in the code. Leave empty if not nec protocol
		- -1 spare
	
	- Codes section consisting of lines of buttonname,hexcode
		- ONOFF,10EF	

### Other web commands
- /upload (simple one file uploader)
- /recent (lists recent activity)
- /check (shows basic status)
- /    (loads a web form to send commands manually)
- /edit (loads a web form to view file list and delete/ upload files)
- /edit?file=filename (view contents of a specific file)
- /reload (reloads buttonnames and device files. Use after changing any of these)

### Libraries
- BitMessages Routines to look up and create pulse sequences for a commands
- BitTx Bit bang routines to execute a pulse sequence
	- Interrupt driven and supports accurate modulation
- WifiManager
- FS
- DNSServer
- ArduinoJson (must be v6 or greter)
- ESP8266mDNS
- ESP8266HTTPUpdateServer

### Install procedure
- Normal arduino esp8266 compile and upload
- A simple built in file uploader (/upload) should then be used to upload the 4 base files to SPIFF
  edit.htm.gz
  index.html
  favicon.ico
  graphs.js.gz
- The /edit operation is then supported to upload further blaster definition files
	
### Tool for gathering codes from iLumos
This is a simple python program (ilumosrf.py) expected to run on a Raspberry Pi and using a 433MHz receiver connected to GPIO24.


Note that the program assumes the GPIO is low when 433MHz is off.
  
### Triggering from Alexa / IFTTT
- Set up Router to port forward external requests to IRBlaster device. Use a dns service if possible to give router external IP a name
- Register with IFTTT and set up Alexa service using your Amazon login
- Create new Applet with Alexa as IF. Select trigger with phrase. Enter phrase to be the trigger, e.g tv on.
- Use Maker WebHooks as the THAT action.
- Enter a URL into Webhooks to invoke the IRBlaster action (typically use a macro) e.g `
http://yourExtIP:port?plain={"auth":"1234","commands":[{"device":"macro","parameter":"TVOn","wait":"1000"}]}`
Note that this needs to be in the IFTTT URL, putting the POST in the body in IFTTT does not seem to work
- Create and save the macro with same name (TVOn) in the IRBlaster to support the request
   
	

