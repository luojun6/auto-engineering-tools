import os, sys
current_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, root_dir)

import logging

class Logger:
    def __init__(self, logger_name="DefaultLogger", 
                 logging_level=logging.DEBUG):
        self.__logger = logging.getLogger(logger_name)
        if logging_level not in logging._levelToName:
            raise TypeError(f"Invalid input logging_level: {logging_level}.")
        self.__logger.setLevel(logging_level)
        self.__ch = logging.StreamHandler()
        self.__ch.setLevel(logging_level)
        
        self.__formatter = logging.Formatter(
            f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.__ch.setFormatter(self.__formatter)
        self.__logger.addHandler(self.__ch)
        
    def debug(self, msg):
        self.__logger.debug(msg)
        
    def info(self, msg):
        self.__logger.info(msg)
        
    def warn(self, msg):
        self.__logger.warning(msg)
        
    def error(self, msg):
        self.__logger.error(msg)
        
    def critical(self, msg):
        self.__logger.critical(msg)
    
        
if __name__ == "__main__":
    print(logging.DEBUG in logging._levelToName)
        
