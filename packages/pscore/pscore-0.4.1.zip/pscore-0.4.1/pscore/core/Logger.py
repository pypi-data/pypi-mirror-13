import logging
import logging.handlers
import os
import threading

log_dir = './logs/'


class Logger(logging.Logger):
    def __init__(self, test_name):
        super(Logger, self).__init__(name=test_name, level=logging.DEBUG)

        formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s  %(filename)s:%(lineno)d in %(funcName)s : %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

        # synchronize calls to create directory from multiple threads
        lock = threading.Lock()
        lock.acquire()
        
        if not os.path.exists(log_dir):

            try:
                os.makedirs(log_dir)
            except OSError as e:
                print('Error creating log directory, type {}\nMessage: {}'.format(type(e), str(e)))

        lock.release()

        log_file_name = os.path.join(log_dir, '{}.log'.format(test_name))

        log_file_handler = logging.FileHandler(
                filename=log_file_name,
                mode='w')

        log_file_handler.setFormatter(formatter)
        super(Logger, self).addHandler(log_file_handler)
