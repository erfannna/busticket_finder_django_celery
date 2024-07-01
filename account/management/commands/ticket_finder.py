from django.core.management.base import BaseCommand
from account.models import Service
from jalali_date import date2jalali

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ippanel import Client
from ippanel import HTTPError

CLASS_NAME_ISF = "FreeChairsNum"
CLASS_NAME_KHC = "available-seat"

SMS_APIKEY = ''
SMS_PATTERN_CODE = ''
SMS_SENDER = "+983000505"
sms = Client(SMS_APIKEY)


class Command(BaseCommand):
    help = "Monitoring available tickets"

    def handle(self, *args, **options):
        services = Service.objects.filter(expired=False)

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        for serv in services:
            if serv.name == "اصفهان به خوانسار":
                class_name = CLASS_NAME_ISF
            else:
                class_name = CLASS_NAME_KHC

            driver.get(serv.checking_url)

            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

            if class_name == CLASS_NAME_KHC:
                elements = []
                el = driver.find_elements(By.CLASS_NAME, class_name)
                for e in el:
                    elements.append(e.find_element(By.TAG_NAME, 'span'))
            else:
                elements = driver.find_elements(By.CLASS_NAME, class_name)

            free_chairs = 0
            i = 1
            for element in elements:
                if element.text != '0' and element.text != '۰':
                    print(f"BUS {i} - Free chairs: {element.text}")
                    free_chairs += 1
                i += 1

            if free_chairs != 0:
                date = date2jalali(serv.datetime).strftime('%y/%m/%d')
                for passenger in serv.passengers.all():
                    try:
                        message_id = sms.send_pattern(
                            SMS_PATTERN_CODE,
                            SMS_SENDER,
                            f"+98{passenger.phone_number}",
                            {"name": f"{passenger.first_name}",
                             "destination": f"{serv.name}",
                             "date": f"{date}"
                             },
                        )
                        serv.passengers.remove(passenger)
                    except HTTPError:
                        pass
        driver.quit()

        self.stdout.write("Finding tickets just ran.")
