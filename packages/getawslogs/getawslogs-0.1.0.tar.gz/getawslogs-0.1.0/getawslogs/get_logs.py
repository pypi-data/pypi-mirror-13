import os
import sys
import threading
import logging
from re import search as regex_search


class _StreamLogs(threading.Thread):
    """
    This class is used used internally by FetchLog class.
    It spawns threads that run in infinite loops to fetch a logStream associated to a logGroup
    """
    def __init__(self, conn, log_group_name, stream_name):
        """
        object initialisation
        """
        try:
            def _get_next_time(file_path):
                """
                Determine next seek time when a log file
                already exists.

                :param file_path: path to file to resume writing logs
                :return: Str epoch time format
                """
                logging.info("log file %s exists, trying to determine next seek time" % file_path)
                file_handle = open(file_path, "r")
                lines = file_handle.readlines()
                if len(lines) < 1:
                    logging.info("%s is an empty file!" % file_path)
                    return None
                file_handle.close()
                last_line = lines[-1]
                ingestion_time = last_line.split(",")[0]
                try:
                    start_time = regex_search('\d+', ingestion_time).group()
                    logging.info("%s next start time: %s" % (file_path, start_time))
                    return int(start_time)
                except AttributeError, error:
                    logging.exception(error)
                    logging.exception("Unable to determine next ingestion time for %s" % file_path)
                    return None

            threading.Thread.__init__(self)
            self.next_time = None
            self.next_token = ""
            self.conn = conn
            self.stream_name = str(stream_name).replace("/", "_")  # Required to avoid nested folder creation failure.
            self.log_group_name = str(log_group_name).replace("/", "_")

            self.LOG_FILE_PATH = os.curdir + os.sep
            self.LOG_FILE_NAME = "vpc_"+self.log_group_name+"_"+self.stream_name+".log"
            if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
                try:
                    UNIX_PATH = "/var/log/getawslogs/"
                    if os.path.isdir(UNIX_PATH) and os.access(UNIX_PATH, os.W_OK):
                        self.LOG_FILE_PATH = UNIX_PATH
                    elif not os.path.isdir("/var/log/getawslogs"):
                        os.makedirs("/var/log/getawslogs", mode=00755)
                        self.LOG_FILE_PATH = UNIX_PATH
                except IOError, error:
                    logging.warning(error)
                except Exception, error:
                    logging.warning(error)
                    logging.info("The Logs will be written to current directory.")

            # Check if logfile already exists and get the last time stamp.
            if os.path.isfile(self.LOG_FILE_PATH + self.LOG_FILE_NAME):
                self.next_time = _get_next_time(self.LOG_FILE_PATH + self.LOG_FILE_NAME)

            self.LOG_FILE_HANDLE = open(self.LOG_FILE_PATH + self.LOG_FILE_NAME, "a", 0)

            logging.info("FetchLogs object initialised")
        except IOError, e:
            logging.exception(e)
        except Exception, e:
            logging.exception(e)

    def run(self):
        # TODO: Change below loop condition to use a killswitch variable to kill threads.
        while True:
            try:
                if self.next_time is not None:
                    events_response = self.conn.get_log_events(logGroupName=self.log_group_name,
                                                               logStreamName=self.stream_name,
                                                               startTime=self.next_time)
                elif len(self.next_token) < 1:
                    events_response = self.conn.get_log_events(logGroupName=self.log_group_name,
                                                               logStreamName=self.stream_name)
                else:
                    events_response = self.conn.get_log_events(logGroupName=self.log_group_name,
                                                               logStreamName=self.stream_name,
                                                               nextToken=self.next_token)
                self.next_token = events_response["nextForwardToken"]\
                    if len(events_response["nextForwardToken"]) > 0 else ""
                self.next_time = None  # next_time is used to resume logging and should only be called once
                for events in events_response["events"]:
                    event = str(events).replace("{", "")\
                            .replace("}", "")\
                            .replace(" u'", " '")\
                            .replace("u'", "'")\
                            .replace("':", ":")
                    self.LOG_FILE_HANDLE.write(event+"\n")
                    self.LOG_FILE_HANDLE.flush()
            except ValueError, error:
                logging.error(error)
            except Exception, error:
                logging.error(error)


class FetchLogs:
    """
    Takes the logGroup as an argument and gets all the
    associated logStreams and write them to a flat file.

    TODO: Should periodically check for new logStreams
    """

    def __init__(self, conn, log_group):
        self.conn = conn
        self.log_group = log_group
        self.log_streams = []
        self.stream_threads = []  # Holds all the thread objs for each stream that belongs to the logGroup
        # super(FetchLogs, self).__init__()  # Not required since this class doesn't inherit Process class
        logging.info("FetchLogs object initialised")

    def _get_log_streams(self):
        """
        Populates/Updates the instance variable log_streams of FetchLogs class
        """
        streams = self.conn.describe_log_streams(logGroupName=self.log_group)
        streams = streams["logStreams"]
        stream_names = []
        for names in streams:
            stream_names.append(names["logStreamName"])
        self.log_streams = stream_names

    def run(self):
        self._get_log_streams()
        logging.info("From Process LG: " + str(self.log_group))
        logging.info("From Process SN: " + str(self.log_streams))
        for log_stream in self.log_streams:
            # Start a thread for each logStream
            thread = _StreamLogs(self.conn, self.log_group, log_stream)
            self.stream_threads.append(thread)
            thread.start()
        for each in self.stream_threads:
            each.join()
        logging.info("Exiting FetchLogs() process")
