import os
import datetime
import time
import requests
import base64
import pickle
from pushover import Pushover

def send_via_pushover(pushover_user,pushover_api,pushover_device,content):

    client = Pushover(token=pushover_api)
    client.message(user=pushover_user, message=content, title='SimpleFin', device=pushover_device)

    return None

def list_to_string(lst):
    if not lst:
        return False
    else:
        return ' '.join(map(str, lst))

def setup_function(file_name):
    setup_token = input('SimpleFin Setup Token? ')

    claim_url = base64.b64decode(setup_token)
    response = requests.post(claim_url)
    access_url = response.text

    pushover_user = input('Pushover User? (leave blank to skip) ')

    pushover_api = input('Pushover API? (leave blank to skip) ')

    pushover_device = input('Pushover Device? (leave blank to skip) ')

    data = {"access_url":access_url, "pushover_user":pushover_user, "pushover_api":pushover_api, "pushover_device":pushover_device}
        
    with open(file_name,"wb") as  file:
        pickle.dump(data, file)
        file.close()

    return None


def main():

    file_name = os.path.dirname(os.path.realpath(__file__)) + "/simplefin-data.pickle"

    try:

        with open(file_name,"rb") as  file:
            data = pickle.load(file)
            access_url = data["access_url"]
            pushover_user = data["pushover_user"]
            pushover_api = data["pushover_api"]
            pushover_device = data["pushover_device"]

            file.close()
    
    except IOError:   

        access_url = ''

    if not access_url:
    
        setup_function(file_name)

        with open(file_name,"rb") as  file:
            data = pickle.load(file)
            access_url = data["access_url"]
            pushover_user = data["pushover_user"]
            pushover_api = data["pushover_api"]
            pushover_device = data["pushover_device"]

            file.close()
        
    scheme, rest = access_url.split('//', 1)
    auth, rest = rest.split('@', 1)

    url = scheme + '//' + rest + '/accounts'
    username, password = auth.split(':', 1)

    start_datetime = datetime.date.today()-datetime.timedelta(days=1)
    start_unixtime = int(round(time.mktime(start_datetime.timetuple())))
    end_datetime = datetime.date.today()
    end_unixtime = int(round(time.mktime(end_datetime.timetuple())))

    response = requests.get(url, auth=(username, password),params={'start-date': start_unixtime, 'end-date': end_unixtime})
    data = response.json()

    errors = data['errors']

    error_string = list_to_string(errors)

    if error_string:
        print(error_string)

        if pushover_user:
            send_via_pushover(pushover_user,pushover_api,pushover_device,error_string)
    
if __name__ == "__main__":
    main()
