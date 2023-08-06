import logging


class CloudwatchLogs:
    def __init__(self, conn):
        """

        :param conn: AWS boto3 connection object.
        :return:
        """
        self.conn = conn
        self.log_group_names = []
        self.log_stream_names = []
        self.log_groups_and_streams = {} # {"aptsc-npemgmt" = ["eni-0460163-all", "eni-063-all", "eni-0460-all"]}
        logging.info("CloudwatchLogs object initialised")

    def _get_log_groups(self):
        log_groups = self.conn.describe_log_groups()
        for each in log_groups['logGroups']:
            self.log_group_names.append(each["logGroupName"])
        # return log_groups

    def _get_log_streams(self):
        stream_names = []
        for group_name in self.log_group_names:
            stream_names.append(self.conn.describe_log_streams(logGroupName=group_name))

        for stream_name in stream_names:
            self.log_stream_names = stream_name

    def populate_log_groups_and_streams(self):
        self._get_log_groups()
        for log_group in self.log_group_names:
            self.log_groups_and_streams[log_group] = self.conn.describe_log_streams(logGroupName=log_group)["logStreams"]