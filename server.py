#!/usr/bin/env python3

import sys
import sched
import time
import requests
import json
from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.exceptions import ResponseErrorLoginRequiredException

class Sender:

    def __init__(self, backend_url : str, router_password : str):
        self._password = router_password
        self._client = self.make_client()
        self._queue = dict()
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._backend_url = backend_url

    ############ CREATE A huawei_lte_api CLIENT ############
    def make_client(self):
        MODEM_CREDS_USERNAME = "admin"
        MODEM_LOCAL_IP = "192.168.8.2"

        # establish a connection
        connection = AuthorizedConnection('http://{}:{}@{}/'.format(MODEM_CREDS_USERNAME,
                                                                    self._password,
                                                                    MODEM_LOCAL_IP))
        # init the client
        return Client(connection)

    ############ WRAPPER FOR SEND SMS + SEND CONFIRMATION ############
    def handle_request(self, sms_id: str, phone_number: str, message: str):
        print("[HANDLER] Sending message to {}".format(phone_number))
        try:
            err = self.send_sms([phone_number], message)
            self.confirm_sent(sms_id, not err)
        except Exception as e:
            print("[HANDLER] Handle request error : {}".format(e))

    ############ SEND SMS WITH USING THE MODEM CLIENT ############
    def send_sms(self, phone_numbers: list, message: str):
        try:
            response = self._client.sms.send_sms(phone_numbers, message)
            if response != "OK":
                return "Could not send ({}): {} => {}".format(response, phone_numbers, message)
        except ResponseErrorLoginRequiredException:
            self._client = self.make_client()

    ############ TELL THE MNIAM BACKEND THAT SMS WAS SENT ############
    def confirm_sent(self, sms_id: str, sent: bool):
        data = {'sms_id': sms_id,
                'status': "OK" if sent else "ERR"}
        headers = {'content-type': 'application/json'}
        try:
            r = requests.post(self._backend_url + "/api/sms/update", headers=headers, data=json.dumps(data))
            print("[HANDLER] Confimation sent, status code: {}".format(r.status_code))
        except Exception as e:
            print("[HANDLER] Confimation not sent. Exception{}".format(e))

    ############ CALLED EACH LOOP IT INVOCATION ############
    def _run(self, sc):
        try:
            # fetch list
            r = requests.get(self._backend_url + "/api/sms/fetch")
            try:
                # decode and handle send requests
                blob = r.json()
                if blob["message"] == "OK":
                    for [sms_id, sms_data] in blob["queue"].items():
                        self.handle_request(sms_id, sms_data["phone_number"], sms_data["message"])
            except:
                print("[LOOP] JSON error : could not decode.\n Code: {}\n Content: {}"
                    .format(r.status_code, r.content))
        except Exception as e:
            print("[LOOP] Request error : could not get /api/sms/fetch\n{}".format(e))
        self._scheduler.enter(60, 1, self._run, (sc,))

    ############ STARTS THE INFINITE LOOP ############
    def serve(self):
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._scheduler.enter(0, 1, self._run, (self._scheduler,))
        self._scheduler.run()

if __name__ == "__main__":
    url = sys.argv[1]
    psw = sys.argv[2]
    Sender(url, psw).serve()
