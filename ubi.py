import requests
import serial
import datetime
import time
import schedule
import os

class Light_on:
    def __init__(self, hr, min):
        self.hr = hr
        self.min = min
    def modifyTime(self, new_hr, new_min):
        self.hr = new_hr
        self.min = new_min
    def returnTime(self):
        if(len(self.hr)==1):
            self.hr = "0"+self.hr
        if(len(self.min)==1):
            self.min= "0"+self.min
        return self.hr +":"+ self.min

class Light_off:
    def __init__(self, hr, min):
        self.hr = hr
        self.min = min
    def modifyTime(self, new_hr, new_min):
        self.hr = new_hr
        self.min = new_min
    def returnTime(self):
        if(len(self.hr)==1):
            self.hr = "0"+self.hr
        if(len(self.min)==1):
            self.min= "0"+self.min
        return self.hr +":"+ self.min


ENDPOINT = "things.ubidots.com"
DEVICE_LABEL = os.environ.get("UBIDOTS_LABEL")
VARIABLE_LABEL = ""
VARIABLE_LABEL_1 = "temperature"
VARIABLE_LABEL_2 = "light"
VARIABLE_LABEL_3 = "soil"
TOKEN = os.environ.get("UBIDOTS_KEY")
DELAY = 1  # Delay in seconds

ser = serial.Serial("/dev/ttyACM0", 9600)
time.sleep(6)


#This function made by Jose García @https://github.com/jotathebest/
def post_var(payload, url=ENDPOINT, device=DEVICE_LABEL, token=TOKEN):
    try:
        url = "http://{}/api/v1.6/devices/{}".format(url, device)
        headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

        attempts = 0
        status_code = 400

        while status_code >= 400 and attempts < 5:
            write_log("[INFO] Sending data, attempt number: {}".format(attempts))
            req = requests.post(url=url, headers=headers,
                                json=payload)
            status_code = req.status_code
            attempts += 1
            time.sleep(1)

        write_log("[INFO] Results: {}".format(req.text))
    except Exception as e:
        write_log("[ERROR] Error posting, details: {}".format(e))

#This function made by Jose García @https://github.com/jotathebest/
def get_var(url=ENDPOINT, device=DEVICE_LABEL, variable=VARIABLE_LABEL,
            token=TOKEN):
    try:
        url = "http://{}/api/v1.6/devices/{}/{}/lv".format(url,
                                                        device,
                                                        variable)

        headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

        attempts = 0
        status_code = 400

        while status_code >= 400 and attempts < 5:
            write_log("[INFO] Retrieving data, attempt number: {}".format(attempts))
            req = requests.get(url=url, headers=headers)
            status_code = req.status_code
            attempts += 1
            time.sleep(1)

        write_log("[INFO] Results: {}".format(req.text))
        return req.text
    except Exception as e:
        write_log("[ERROR] Error posting, details: {}".format(e))

# get temperature info from arduino
def temp():
    ser.write(str.encode("temperature"))
    time.sleep(3)
    result = ser.readline().decode("utf-8")
    result_strip = float(result.strip())
    return result_strip

# get amount of light from arduino
def light():
    ser.write(str.encode("light"))
    time.sleep(3)
    result = ser.readline().decode("utf-8")
    result_strip = int(result.strip())
    return result_strip

# get soil moisture from arduino
def soil():
    ser.write(str.encode("soil"))
    time.sleep(3)
    result = ser.readline().decode("utf-8")
    result_strip = int(result.strip())
    return result_strip

# send command to arduino
def str_command(command):
    write_log(command)
    ser.write(str.encode(command))
    time.sleep(3)

# write log into log file function
def write_log(info):
    now = datetime.datetime.now()
    log_now = now.strftime("%d-%m-%Y %H:%M:%S")
    log_info = "{};{}".format(log_now, info)
    try:
        f = open("log.txt", "a", encoding="utf-8")
        f.write(log_info)
        f.write("\n")
    except:
        print("Something went wrong.")
        sys.exit(0)
    finally:
        f.close()

# red lead-info constantly from ubidots
def leds():
    red_on_check = True
    red_off_check = True
    green_on_check = True
    green_off_check = True
    while True:
        red_led = float(get_var(ENDPOINT,DEVICE_LABEL,"red_led", TOKEN))
        green_led = float(get_var(ENDPOINT,DEVICE_LABEL,"green_led", TOKEN))
        int_red = int(red_led)
        int_green = int(green_led)
        #red led logic
        if(int_red == 1 and red_on_check):
            str_command("red_led_on")
            #print("red_led_on")
            red_on_check = False
            red_off_check = True
        elif(int_red == 0 and red_off_check):
            str_command("red_led_off")
            #print("red_led_off")
            red_on_check = True
            red_off_check = False
        #green led logic
        if(int_green == 1 and green_on_check):
            str_command("green_led_on")
            #print("green_led_on")
            green_on_check = False
            green_off_check = True
        elif(int_green == 0 and green_off_check):
            #print("green_led_off")
            green_on_check = True
            green_off_check = False
            str_command("green_led_off")

# sends sensor values to ubidots
def send_values():
    # Get sensor values
    sensor_value_1 = temp()
    sensor_value_2 = light()
    sensor_value_3 = soil()
    # Builds Payload and topíc
    payload = {VARIABLE_LABEL_1: sensor_value_1,
               VARIABLE_LABEL_2: sensor_value_2,
               VARIABLE_LABEL_3: sensor_value_3
              }
    # Sends data
    post_var(payload)

# prints the sensor values to the terminal
def print_sensor_values():
    sensor_value_1 = temp()
    sensor_value_2 = light()
    sensor_value_3 = soil()
    now = datetime.datetime.now()
    log_now = now.strftime("%d-%m-%Y %H:%M:%S")
    print(log_now)
    print("Temperature: {}".format(sensor_value_1))
    print("Amount of light: {}".format(sensor_value_2))
    print("Soil moisture: {}".format(sensor_value_3))

# function for testing
def job():
    print("I'm working...")
    now = datetime.datetime.now()
    print ("Current date and time : ")
    print (now.strftime("%d-%m-%Y %H:%M:%S"))

def light_on_off():
    # clear on-off schedule
    schedule.clear('daily-tasks')

    # configure when the light is on
    light_on = Light_on("00", "00")
    hr_on = float(get_var(ENDPOINT,DEVICE_LABEL,"time_on_h", TOKEN))
    min_on = float(get_var(ENDPOINT,DEVICE_LABEL,"time_on_min", TOKEN))
    hr_str_on = "{:.0f}".format(hr_on)
    min_str_on = "{:.0f}".format(min_on)
    light_on.modifyTime(hr_str_on,min_str_on)
    on_time = light_on.returnTime()
    schedule.every().day.at(on_time).do(str_command, "red_led_on").tag('daily-tasks', 'light_on')

    # configure when the light is off
    light_off = Light_off("00", "00")
    hr_off = float(get_var(ENDPOINT,DEVICE_LABEL,"time_off_h", TOKEN))
    min_off = float(get_var(ENDPOINT,DEVICE_LABEL,"time_off_min", TOKEN))
    hr_str_off = "{:.0f}".format(hr_off)
    min_str_off = "{:.0f}".format(min_off)
    light_off.modifyTime(hr_str_off,min_str_off)
    off_time = light_off.returnTime()
    schedule.every().day.at(off_time).do(str_command, "red_led_off").tag('daily-tasks', 'light_off')

def main_ubidots():
    #leds()
    #send_values()
    for i in range(24):
        i = str(i)
        if(len(i)==1):
            i = "0"+ i
        i = i+":00"
        schedule.every().day.at(i).do(send_values)
    schedule.every().day.at("12:30").do(light_on_off)
    print("Ubidots functions are on.")
    print("CTRL-C to stop udibots functions")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def main_menu():
    print("Main menu. Give number for action: ")
    print("1) Print sensor values")
    print("2) Start Ubidots functions")
    print("3) Stop Ubidots functions")
    print("4) Light on")
    print("5) Light off")
    print("6) Stop program")
    choice = input("Your choice: ")
    return choice

def main():
    while True:
        choice = main_menu()
        if (choice == "1"):
            print_sensor_values()
        elif(choice == "2"):
            ubi = main_ubidots()
        elif(choice == "3"):
            print("Ubidots functions are off.")
        elif(choice == "4"):
            print("Light is on.")
            str_command("red_led_on")
        elif(choice == "5"):
            print("Light is off.")
            str_command("red_led_off")
        elif(choice == "6"):
            print("Good bye!")
            break
        else:
            print("Unknown error.")
    return None


if __name__ == "__main__":
    main()
