from abc import ABCMeta, abstractmethod
import time

__author__ = 'Silvio'


class FileNameProvider:
    """
    Abstract class to provide "unique" file names

    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def get_file_name(self):
        """
        Get the file name

        @rtype : str
        @return : "unique" file name
        """
        pass


class FileNameProviderByTime(FileNameProvider):
    """
    A class to provide file names based on time

    """

    def __init__(self):
        super(FileNameProviderByTime, self).__init__()

    def get_file_name(self):
        """
        Get the file name

        @rtype : str
        @return : "unique" file name
        """
        return time.strftime("E%Y%m%d%H%M%S")
