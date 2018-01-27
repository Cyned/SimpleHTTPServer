from colorama import Fore
from sys import stdout


class Output(object):

    def __init__(self, out=None):
        """
            :param out: output stream
        """
        if out:
            self.out = out
        else:
            self.out = stdout

    def success(self, s):
        """
            function to show the success message

            :param s: text (string) to print
        """
        print("{begin}{string}{end}\n".format(begin=Fore.BLUE, end=Fore.WHITE, string=s), file=self.out)

    def error(self, s):
        """
            function to show the error message

            :param s: text (string) to print
        """
        print("{begin}{string}{end}\n".format(begin=Fore.RED, end=Fore.WHITE, string=s), file=self.out)

    def info(self, s):
        """
            function to show the info message

            :param s: text (string) to print
        """
        print("{string}\n".format(string=s), file=self.out)
