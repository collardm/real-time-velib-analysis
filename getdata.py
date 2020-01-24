# import the necessary packages
import os
import requests
import pandas as pd
from time import localtime, strftime
from repeatedtimer import RepeatedTimer

# For more information see https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/information/
def download_csv():
    global iteration

    # set the endpoint API URL
    url = "https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true&csv_separator=%3B"
    
    # Track request_time 
    request_time = strftime("%Y-%m-%d_%H-%M-%S", localtime())

    # make the call
    print("[INFO] Call the API")
    resp = requests.get(url)

    if resp.status_code != 200:
        print("[INFO] API call failed at :", request_time)
    
    else:        
        # get location of the python script
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname('__file__')))

        # Save the csv file with the date and the time in the filename.
        filename = "velib_" + request_time + ".csv"
        with open(os.path.join(__location__, filename), "wb") as f:
            f.write(resp.content)

        print("[INFO] File number {} saved".format(iteration))
    
    iteration += 1

    return    

if __name__ == '__main__':
    # delay in seconds
    delay = 60
    iteration = 1    

    rt = RepeatedTimer(delay, download_csv)
    