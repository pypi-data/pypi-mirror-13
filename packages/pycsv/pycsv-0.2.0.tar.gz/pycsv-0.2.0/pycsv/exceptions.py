
class PyCsvRequiredHeader(Exception):
    def __init__(self, msg):
        self.message = 'PyCsv :' + msg


class PyCsvInvalidColumn(Exception):
    def __init__(self, msg):
        self.message = 'PyCsv :' + msg


class PyCsvExcept(Exception):
    def __init__(self, msg):
        self.message = 'PyCsv :' + msg


class PyCsvInvalidCast(Exception):
    def __init__(self, msg):
        self.message = 'PyCsv :' + msg

class PyCsvInvalidType(Exception):
    def __init__(self, msg):
        self.message = 'PyCsv :' + msg

class PyCsvOutBound(Exception):
    def __init__(self, msg):
        self.message = 'PyCsv :' + msg

class PyCsvInvalidFile(Exception):
    def __init__(self, msg):
        self.message = 'PyCsv :' + msg