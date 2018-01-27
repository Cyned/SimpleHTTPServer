from os import chdir, sep
from os import listdir as l_dir
from os import path as join_path

from mimetypes import guess_type
import decorators

from urllib import parse as url_parse


BUFSIZE = 1024
ENCODING = 'utf-8'
HISTORY = set()


class Client(object):
    def __init__(self, con, c_adr, current_path, output):

        """
            :param con: a new socket object usable to send and receive data on the connection;
            :param c_adr: the address bound to the socket on the other end of the connection;
            :param current_path: current directory/location;
            :param output: Object (Output).
        """
        self.conn = con
        self.adr = c_adr

        self.output = output

        request = self.conn.recv(BUFSIZE)

        self.path = self.get_path(request.decode(ENCODING))

        self.current_path = current_path

    @decorators.set_browser
    def show_pic(self):
        """show the picture in the browser"""
        file = join_path.join(self.current_path, self.path)
        self.output.info("Open the picture: {file}".format(file=file))
        self.conn.send("<p>Pictures</p>".encode(ENCODING))
        self.conn.send("<div><img src='{path}' alt='There is a picture {file}'><div>".format(path=file, file=self.path)
                       .encode(ENCODING))

    @decorators.set_browser
    def show_text(self, file):
        """
            show the text-type files in the browser

            :param file: name of the file
        """
        file = join_path.join(self.current_path, file)
        self.output.info("Open the text file: {file}".format(file=file))
        with open(file, "rb") as f:
            self.conn.send(f.read())

    @decorators.set_browser
    def downland(self):
        """downland the file"""
        file = join_path.join(self.current_path, self.path)
        self.output.success("Download the file: {file}".format(file=file))
        self.conn.send("<p>Downland the file <a download href='{path}'>{file}</a></p>".
                       format(path=file, file=self.path).encode(ENCODING))
        self.conn.send(''.format(path=file).encode(ENCODING))

    @decorators.set_browser
    def show_error(self, msg):
        """
            show any errors

            :param msg: error message
        """
        self.output.error(msg)
        self.conn.send("<h1>Sorry. Something wrong.</h1><br><br>".encode(ENCODING))
        self.conn.send(msg.encode(ENCODING))

    @decorators.set_browser
    def show_list(self, data):
        """
            show the folders and files

            :param data: list of the folders and files of the current directory/locations
        """
        self.conn.send("<h1>Directory listing for {path}</h1><br>".format(path=self.current_path).encode(ENCODING))
        self.conn.send("<hr><ul>".encode(ENCODING))
        if self.current_path != sep:
            self.conn.send("<li type=circle><a href='{back}'>{back}</a></li>".format(back="...").encode(ENCODING))
        for item in data:
            self.conn.send("<li type=circle><a href='{file}'>{file}</a></li>".format(file=item).encode(ENCODING))
        self.conn.send("<ul><br>".encode(ENCODING))
        self.conn.send("<hr>".encode(ENCODING))

    def parse(self):
        """check if there is index.html"""
        file_list = l_dir(self.current_path)
        if 'index.html' in l_dir(self.current_path):
            file = "index.html"
            self.show_text(file)
            self.move_back()
        else:
            self.show_list(file_list)

    def move_back(self):
        """move back to the previous directory/location"""
        index = self.current_path.rfind(sep)
        self.current_path = self.current_path[:index]
        if self.current_path == "":
            self.current_path = sep

    def search_in_history(self):
        """
            search the path in the history
            :return: return True if such was found
        """
        for item in HISTORY:
            if self.path in l_dir(item):
                self.current_path = item
                return True
        return False

    def what_is_it(self):
        """
            function to know the type of the file and call needed necessary method
        """
        file_type = guess_type(self.path)[0]

        if file_type is not None:
            if "image" in file_type:
                self.show_pic()
            elif "text" in file_type:
                self.show_text(self.path)
            else:
                self.downland()
        else:
            self.show_error("Something wrong with this file")

    def do(self):
        """
            - either move to the next directory/location
            - or show/download the file

            :return: current path we have gone to
        """
        is_dir = True
        self.output.info("Current directory: {path}".format(path=self.current_path))

        if self.path == "...":
            self.move_back()
        elif self.path != "" and self.path != "favicon.ico":
            try:
                chdir(join_path.join(self.current_path, self.path))
                chdir(self.current_path)
                self.current_path = join_path.join(self.current_path, self.path)
                HISTORY.add(self.current_path)
            except NotADirectoryError:
                is_dir = False
                self.what_is_it()
            except FileNotFoundError as error:
                if not self.search_in_history:
                    is_dir = False
                    self.show_error("{message}\n{error}".format(message="Something is wrong. Try maybe click "
                                                                        "button 'forward' or 'back' in your browser.\n",
                                                                error=error))
            except PermissionError as error:
                is_dir = False
                self.show_error("{message}".format(message=error))

        if is_dir:
            self.parse()

        return self.current_path

    @staticmethod
    def get_path(text):
        """
            :param text: request (String)

            :return: the path from the request we want to go to
        """
        end = text.find("H")
        new_path = text[5:end - 1]                          # get only the path the client has chosen
        new_path = url_parse.unquote(new_path, ENCODING)    # fix the url decode
        return new_path
