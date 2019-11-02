import sys, utils, time
from defaultModule import DefaultModule
from config import *

CONFIG_PATH="./config.yaml"
CONFIG_TEMPLATE={"wallpaperDir": str(), "defaultSource": str(), }
DEFAULT_SLEEP=1 

time_last_set = 0
bg_change_interval = 2 


if __name__ == "__main__":
    
    try:
        config = load_config(CONFIG_PATH)

    except Exception as e:
        sys.exit(e)
        
    if not verify_config(config, CONFIG_TEMPLATE):
        sys.exit("config is incorrect, please correct it and try again")

    
    for key in config["modules"]:
        utils.load_module(key)

    activeModule = config["defaultModule"] 
    
    moduleInstance = sys.modules["modules."+activeModule].moduleClass(config) 
    
    # TODO: implement either UNIX socket for communication with 
    # config manager at runtime or dbus using the glib event
    # loop, to manage configuration and or change current module
    while True:
        
        current_time = time.time()
        if current_time - time_last_set > bg_change_interval:
            moduleInstance.run()
   
        # placeholder for non-blocking polling on socket / dbus communication 
        time.sleep(DEFAULT_SLEEP)
        

    

