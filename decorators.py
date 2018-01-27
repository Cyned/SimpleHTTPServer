def set_browser(func):
    """a head of the page"""
    def function_wrapper(self, *args, **kwargs):
        self.conn.send(b"HTTP/1.1 200 Ok\r\n\r\n")
        self.conn.send(b"<head><meta charset='utf-8'></head>")
        self.conn.send(b"<head><meta Content-Type='text/html'></head>")
        self.conn.send(b"<body>")
        func(self, *args, **kwargs)
        self.conn.send(b"</body>")
    return function_wrapper
