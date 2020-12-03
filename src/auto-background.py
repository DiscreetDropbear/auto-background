#!/bin/python
import time, json, requests, sys, shutil, subprocess, os, threading, queue 
from collections import deque
from pathlib import Path

# create a thread and

# encapsulates all of the business logic for how to downloading backgrounds
# from a particular source
class DownloadingEngine(threading.Thread):
    API_URL="https://wallhaven.cc/api/v1/search?{0}"
    # API_TOKEN = "U2ossqGCHMfzVpouHv7i0AT9J926NkEo"
    headers = {"content" : "application/json"} 
    bg_info = deque()
    page_num = 1 

    def __init__(self, bg_dir, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.bg_dir = bg_dir
        self.out_queue = out_queue
        self.in_queue = in_queue
        
    def run(self):
        while True:
            # block untill main thread asks for more backgrounds to be downloaded
            download_amount = self.in_queue.get()

            for i in range(download_amount):
                info = self.get_next_bg_info() 
                bg_name = info["id"]
                bg_path = self.bg_dir.format(bg_name)
            
                try:
                    resp = requests.get(info["path"], stream=True)
                    resp.raw.decode_content = True

                    bg_file = open(bg_path, 'wb')
                    shutil.copyfileobj(resp.raw, bg_file)
                except Exception as e:
                    print(e)

                self.out_queue.put(bg_path)
       
    def get_next_bg_info(self):
        # TODO: use pagination functionality of api to go to next page when we can
        if len(self.bg_info) == 0:
            # loop until we get more bg_info
            while True:
                if not self.download_more_bg_info():
                    # take a break so we don't wear ourselves out
                    # requesting info ;)
                    time.sleep(1)
                else:
                    break
             
        return self.bg_info.popleft()

    def download_more_bg_info(self):
        parameters = "categories=100&purity=110&atleast=1920x1080&ratios=16x9&sorting=toplist&topRange=1y&order=desc&page={}"        
        requestUrl = self.API_URL.format(parameters) 
        print(self.page_num)
        try:
            response = requests.get(requestUrl.format(self.page_num), headers=self.headers)
        except Exception as e:
            return False

        if response.status_code == 200:
            
            data = json.loads(response.content.decode("utf-8"))

            # if data["data"] is empty then there is no content for the page
            # and we have gone too far, set the page back to 1 to start over
            if len(data["data"]) == 0:
                self.page_num = 1
                return False

            # add all the background information into the queue to help
            # keeping track of which ones we have downloaded or not
            for bg in data["data"]:
                self.bg_info.append(bg)

            self.page_num += 1 
            return True

        return False 

# encapsulates the management of when to download new backgrounds 
class BgManager:
    backlog = deque()
    backlog_size = 10
    dl_threshold = 5
    download_amount = backlog_size - dl_threshold
    now = time.time()
    before = now

    def __init__(self, bg_dir):
        self.in_queue = queue.Queue()
        # used to send a number of background paths to put in the in_queue
        self.out_queue = queue.Queue()
        # start downloading backgrounds
        self.out_queue.put(self.backlog_size)

        self.bg_downloader = DownloadingEngine(bg_dir, self.out_queue, self.in_queue)
        self.bg_downloader.start()

    # returns true if it was able to set a new background, otherwise returns false
    # should send another request sooner than normal on a false
    def next_bg(self):
        try:
            bg_path = self.in_queue.get(block=False)
            self.set_bg(bg_path)

            if self.in_queue.qsize() < self.dl_threshold:
                # when the number of backgrounds that are ready falls below the threshold
                # tell the other thread to download some more
                self.out_queue.put(self.download_amount)
            return True
        except Exception as e: 
            # TODO: find someway to make sure that more backgrounds are being downloaded
            return False

    def set_bg(self, bg_path, shell=True, bg_settings=["--bg-fill"]):
        args = "feh" 

        for setting in bg_settings:

            args += " "
            args += setting

        args += " "
        args += bg_path

        result = subprocess.Popen(args, shell=True, universal_newlines=True)
        returncode = result.returncode

if __name__ == "__main__":
    bg_dir = "~/Pictures/auto-background/wallhaven/{0}"
    path = os.path.expanduser(bg_dir)
    os.makedirs(path.format(""), exist_ok=True)

    refresh_interval = 60*5 # ten minutes 

    bg_man = BgManager(path)

    while True:
        if bg_man.next_bg():
            print("sleeping for {} seconds".format(refresh_interval))
            time.sleep(refresh_interval)
        else:
            print("background failed to update, retry in 5 seconds")
            time.sleep(5)
