import subprocess
import schedule
import time
import os

flask_script = 'python projectGPT/bmkg-gpt.py'

def start_flask():
    global flask_process
    flask_process = subprocess.Popen(flask_script, shell=True)
    print("Flask started.")

def stop_flask():
    global flask_process
    if flask_process:
        flask_process.terminate()
        print("Flask stopped.")


def restart_flask():
    stop_flask()
    time.sleep(5)  
    fetch_gempa()
    start_flask()

def fetch_weather_forecast():

    os.system('python D:\BMKG-GPT\projectGPT\Refreshscraping\weathertest.py')

def fetch_gempa():

    os.system('python D:\BMKG-GPT\projectGPT\Refreshscraping\ScrapingGempa.py')


start_flask()


schedule.every(1).hour.do(restart_flask)
schedule.every(1).day.at("00:10").do(fetch_weather_forecast)
schedule.every().day.at("13:10").do(fetch_weather_forecast)
schedule.every(1).day.at("07:10").do(fetch_weather_forecast)
schedule.every().day.at("18:10").do(fetch_weather_forecast)
while True:
    schedule.run_pending()
    time.sleep(1)
