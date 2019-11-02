import shutil, time, json, requests, defaultModule, config, backgroundManager

CONFIG_PATH="./wallhaven.yaml"
CONFIG_TEMPLATE={}

class moduleClass(defaultModule.DefaultModule):
    
    DOWNLOADS_PATH="/home/ajani/Pictures/auto-background/wallhaven/{0}"
    API_BASE_URL="https://wallhaven.cc/api/v1/search?{0}"
    API_TOKEN="7J0K2L7tWUouW43CmIIMlEOWG7pAEldE"
    headers = {"content" :"application/json"} 

    bg_file_paths = []
    bg_info = [] 

    active_bg_index = 0
    dl_batch_size = 1
    start_index = 0
    end_index = start_index + dl_batch_size

    def __init__(self, generalConf):

        #self.generalConf = generalConf 
        #conf = config.load_config(CONFIG_PATH) 
        #if not config.verify_config(config, CONFIG_TEMPLATE):
        #    sys.exit("wallhaven configuration error: Exiting")

        if self.API_TOKEN != "":
            self.headers["X-API-Key"] = self.API_TOKEN
    
    def run(self):
 
        # there are no more backgrounds to use
        # from the current selection
        #TODO: delete the old backgrounds
        if self.end_index == None or len(self.bg_info) == 0:
            print("getting background information")
            self.bg_info = self.get_backgrounds_information() 
            self.bg_file_paths = []
            self.start_index = 0
            self.end_index = self.get_next_end_index(0)
            self.active_bg_index = 0
        else:
            self.start_index = self.end_index 
            self.end_index = self.get_next_end_index(self.end_index)

        # The active index is out of range of the
        # bg_file_paths list
        if self.active_bg_index % self.dl_batch_size == 0:
            
            # download more backgrounds
            print("Downloading {} more background/s.".format(self.dl_batch_size))
            self.bg_file_paths = self.download_backgrounds(self.bg_info[self.start_index:self.end_index])

        backgroundManager.set_background(self.bg_file_paths[self.active_bg_index % self.dl_batch_size])

        self.active_bg_index += 1

    def get_next_end_index(self, end_index):
        end_index += self.dl_batch_size

        if end_index >= len(self.bg_info):
            end_index = None 
        
        return end_index

    def get_extension(self, name):
        index = name.rfind('.')
        
        return name[index:]
        
   
    """
        downloads all the backgrounds that are listed in backtroundsData
        returns a list of filePaths for the backgrounds that
        are successfully downloaded
    """
    def download_backgrounds(self, backgroundsData):
        
        filePaths = []

        for background in backgroundsData:
            try:
                extension = self.get_extension(background["path"])
                fileName = background["id"] + extension
                filePath = self.DOWNLOADS_PATH.format(fileName) 
                
                resp = requests.get(background["path"], stream=True)
                resp.raw.decode_content = True
                local_file = open(filePath, 'wb')
                shutil.copyfileobj(resp.raw, local_file)

                filePaths.append(filePath)         
                print("Downloaded file at {}".format(filePath))


            except Exception as e:
                print(e)
                # TODO: add logging

        return filePaths

    """
        sends a 
    """
    def get_backgrounds_information(self):
        
        parameters = self.get_api_request_parameters()
        requestUrl = self.API_BASE_URL.format(parameters) 
        
        response = requests.get(requestUrl, headers=self.headers)

        if response.status_code == 200:
            
            data = json.loads(response.content.decode("utf-8"))
            return data["data"]

        else:
            print(response)
            print(response.status_code)


        return None  
 
    """
        returns a string that includes all of the api search
        parameters ready to be appended to the API_BASE_URL
    """
    def get_api_request_parameters(self):
        #TODO: actually implement generating the string from the config
        return "categories=100&purity=100&atleast=1920x1080&ratios=16x9&sorting=random&order=desc&page=2"        

