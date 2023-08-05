import os
import logging
from sys import stdout
from thread import start_new_thread



class TirelessRunner:
    INPUT_DIR = './in/'
    SOLUTION_DIR = './out/'
    STORAGE_DIR = './storage/'


    def __init__(self, solution_function):
        self.solution_function = solution_function
        self.logger = self.__createLogger()


    def __createLogger(self):
        log_handler = logging.StreamHandler()
        log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] - %(message)s")
        log_handler.setFormatter(log_formatter)
        logger = logging.getLogger(self.__class__.__name__)
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)
        return logger


    def run(self):
        if not os.path.exists(self.INPUT_DIR):
            self.logger.error("Missing input directory: {0}".format(self.INPUT_DIR))
            return
        self.__prepareOutputDirectories()
        self.__startThreads()
        while True:
            pass


    def __prepareOutputDirectories(self):
        if not os.path.exists(self.SOLUTION_DIR):
            os.makedirs(self.SOLUTION_DIR)
        if not os.path.exists(self.STORAGE_DIR):
            os.makedirs(self.STORAGE_DIR)


    def __startThreads(self):
        for filename in os.listdir(self.INPUT_DIR):
            input_fp = self.INPUT_DIR + filename
            solution_fp = (self.SOLUTION_DIR + filename).replace('.in', '.ans')
            result_fp = (self.STORAGE_DIR + filename).replace('.in', '.res')
            start_new_thread(self.__threadFunction, (input_fp, solution_fp, result_fp))


    def __threadFunction(self, input_fp, solution_fp, result_fp):
        self.logger.info("Starting solution Thread for {0}".format(input_fp))
        best_result = None
        try:
            f = open(result_fp, 'r')
            best_result = int(f.readline())
            f.close()
        except Exception:
            self.logger.info("{} has no previous result, starting from scratch".format(input_fp))
        while True:
            (result, solution) = self.solution_function(input_fp)
            if best_result == None or result > best_result:
                self.logger.info("{0} has found a better result: {1}".format(input_fp, result))
                best_result = result
                f = open(solution_fp, 'w')
                f.write(solution)
                f.close()
                f = open(result_fp, 'w')
                f.write(str(best_result))
                f.close()
