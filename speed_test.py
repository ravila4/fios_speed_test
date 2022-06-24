import logging
from time import sleep

import requests


class SpeedTest():
    """Runs a Verizon Fios router speedtest using the API from https://www.verizon.com/speedtest/
    """
    test_url = "https://www.verizon.com/SpeedTest/SpeedTestHandler.ashx"
    session = requests.Session()
    status = ""
    transid = None
    upload = 0
    download = 0
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept":  "*/*"
    }

    def start_test(self):
        print("Starting test...")
        response = self.session.get(self.test_url,
                                    params={"Status": "TR143TestStart",
                                            "IsLoggedIn": "N", "ssvz=": ""},
                                    headers=self.headers)
        response.raise_for_status()
        self.status = response.json()["StatusCode"]
        assert self.status == "S", "Failed to start test"
        self.transid = response.json()["TransID"]

    def check_status(self):
        if self.transid:
            response = self.session.get(
                self.test_url,
                params={
                    "Status": "TR143Update",
                    "IsLoggedIn": "N",
                    "UserActivityTransID": self.transid
                },
                headers=self.headers)
            response.raise_for_status()
            self.upload = response.json()["UploadResult"]
            self.download = response.json()["DownloadResult"]
            self.status = response.json()["StatusCode"]
        else:
            print("Run start_test() first.")

    def run(self):
        self.start_test()
        while self.status != "0":
            self.check_status()
            logging.info("Download speed: {0: >6} | Upload speed: {1: >6} | Status: {2}".format(
                self.download, self.upload, self.status))
            sleep(1)
        print("Test complete.")
        print("Download: {0: >6} Mbps | Upload: {1: >6} Mbps".format(
            self.download, self.upload))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    speed_test = SpeedTest()
    speed_test.run()
