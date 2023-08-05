class FileSet:
    file = []
    name = ""
    private = False
    usage = []
    def __init__(self, name="", file=[], usage = [], private=False):
        self.name    = name
        self.file    = file
        self.usage   = usage
        self.private = private
