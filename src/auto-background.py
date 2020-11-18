#!/bin/python
import time, json, requests, sys, shutil, subprocess 
from collections import deque


# encapsulates all of the business logic for how to downloading backgrounds
# from a particular source
class BgDownloader:
    api_url="https://wallhaven.cc/api/v1/search?{0}"
    api_token = "U2ossqGCHMfzVpouHv7i0AT9J926NkEo"
    headers = {"content" :"application/json"} 
    bg_info = deque() 

    def __init__(self, bg_dir):
        self.bg_dir = bg_dir
    
    # downloads one single background and if we have run out of bg dowload info
    # gets more background info from the api then dowloads the next background
    def download_one(self):
        try:
            bg_info = bg_info.popleft()
        except:
            # if bg_info is still empty then just abort 
            if not self.get_backgrounds_information():
                sys.exit(-1)
            bg_info = self.bg_info.popleft()

        bg_name = bg_info["id"]
        bg_path = self.bg_dir.format(bg_name)
            
        resp = requests.get(bg_info["path"], stream=True)
        resp.raw.decode_content = True

        bg_file = open(bg_path, 'wb')
        shutil.copyfileobj(resp.raw, bg_file)
       
        # send back the path to the newly downloaded bg
        return bg_path
    
    def get_backgrounds_information(self):
        parameters = "categories=100&purity=110&atleast=1920x1080&ratios=16x9&sorting=toplist&topRange=1y&order=desc&page=1"        
        requestUrl = self.api_url.format(parameters) 
        
        response = requests.get(requestUrl, headers=self.headers)

        if response.status_code == 200:
            
            data = json.loads(response.content.decode("utf-8"))
            # add all the background information into the queue to help
            # keeping track of which ones we have downloaded or not
            for bg in data["data"]:
                self.bg_info.append(bg)
            return True
        else:
            print(response)
            print(response.status_code)


        return False 

# encapsulates the management of when to download new backgrounds 
class BgManager:
    backlog = deque()
    backlog_size = 10
    dl_threshold = 5
    now = time.time()
    before = now

    def __init__(self, bg_dir):
        self.bg_downloader = BgDownloader(bg_dir)

    def next_bg(self):
        try:
            return self.backlog.popleft() 
        except: 
            return None 

    def set_bg(self, bg_path, shell=True, bg_settings=["--bg-fill"]):
        args = "feh" 

        for setting in bg_settings:

            args += " "
            args += setting

        args += " "
        args += bg_path

        result = subprocess.Popen(args, shell=True, universal_newlines=True)
        returncode = result.returncode

    # blocks execution for a given number of seconds
    # by either calling time.sleep() or downloading
    # backgrounds
    def sleep(self, seconds):
        print("start sleep time = {}".format(seconds))

        start = time.time()
        start_len = len(self.backlog)
           
        print("len(backlog) - {}, threshold - {}".format(len(self.backlog), self.dl_threshold));

        # only download backgrounds when the number of backgrounds in the backlog
        # falls below the threshold
        if len(self.backlog) < self.dl_threshold:

            # keep downloading backgrounds until either the backlog
            # is full, or the required seconds is reached
            while len(self.backlog) < self.backlog_size:
                download_start = time.time()
                self.backlog.append(self.bg_downloader.download_one())
                download_end = time.time()
                print("Download took {} seconds".format(download_end - download_start))
                
                if time.time() >= start + seconds:
                    return


        time.sleep(seconds)

        print("end sleep time = {}".format(time.time()))

if __name__ == "__main__":
    bg_dir = "/home/ajani/Pictures/auto-background/wallhaven/{0}"
   
    refresh_interval = 60*10 # ten minutes 

    bg_man = BgManager(bg_dir)

    # allow manager to download some backgrounds before first run
    bg_man.sleep(10)

    while True:
        bg_path = bg_man.next_bg()
        if bg_path != None:
            bg_man.set_bg(bg_path)   

        bg_man.sleep(refresh_interval)

