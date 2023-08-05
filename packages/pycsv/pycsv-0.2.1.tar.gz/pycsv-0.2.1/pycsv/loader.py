# coding=utf-8

from exceptions import PyCsvExcept, PyCsvRequiredHeader, PyCsvInvalidColumn, \
    PyCsvInvalidCast, PyCsvInvalidType, PyCsvOutBound, PyCsvInvalidFile, PyCsvInvalidOrder
import os
import csv
from datetime import datetime


class Loader(object):
    def __init__(self, path, with_header=True, separator=','):
        self.path = path
        self.with_header = with_header
        self.separator = separator
        self.data = []
        self.header = []
        self.type_collection = ["integer", "string", "datetime", "float"]
        self.columns = []
        if not os.path.exists(self.path):
            msg = 'Path not exist, you give {path}'.format(path=self.path)
            raise PyCsvExcept(msg)

    @property
    def rows_count(self):
        return len(self.data)

    @property
    def cols_count(self):
        if self.with_header:
            return len(self.header)
        if self.row_count:
            return len(self.data[0])
        return 0

    def __check_headers(self, required_headers):
        if not required_headers:
            return True
        if len(required_headers) == 0:
            return True
        for r_header in required_headers:
            if r_header not in self.header:
                return False

    def __add_and_check_index_column(self, columns):
        ret_value = {
            "asc": {
                "=": 0,
                ">": 1,
                "<": -1
            },
            "desc": {
                "=": 0,
                ">": -1,
                "<": 1
            }
        }
        for column in columns:
            if not self.with_header:
                if "index" not in column:
                    raise PyCsvInvalidColumn("Column invalid, index is required, you give : {column}".
                                             format(column=column))
            if "order" not in column:
                column["order"] = "asc"
            column["order"] = column["order"].lower()
            if column["order"] not in ["asc", "desc"]:
                raise PyCsvInvalidOrder("Order invalid, you give : {order}".format(order=column["order"]))
            column["order"] = ret_value[column["order"]]
            if "type" not in column:
                raise PyCsvInvalidType("Column invalid.")
            if column["type"] not in self.type_collection:
                raise PyCsvInvalidType("Type invalid for sort function. you give :{col}".format(col=column["type"]))
            if column["type"] == "datetime" and "format" not in column:
                raise PyCsvInvalidType("Format date is required. you give :{col}".format(col=column["type"]))
            try:
                if self.with_header:
                    column["index"] = self.header.index(column["column"])
            except ValueError:
                raise PyCsvInvalidColumn("Column {column} invalid.".format(column=column["column"]))
            self.columns.append(column)

    def __itemgetter(self):
        def get_item(item):
            result =[]
            for column in self.columns:
                if column["type"] == "integer":
                    result.append(self.__to_int(item[column["index"]]))
                if column["type"] == "float":
                    result.append(self.__to_float(item[column["index"]]))
                if column["type"] == "datetime":
                    result.append(self.__to_date(item[column["index"]], column["format"]))
                if column["type"] == "string":
                    result.append(item[column["index"]])
            return tuple(result)
        return get_item

    def __to_int(self, value):
        try:
            return int(value)
        except ValueError:
            raise PyCsvInvalidCast("Impossible to convert {v} to integer.".format(v=value))

    def __to_float(self, value):
        try:
            return float(value)
        except ValueError:
            raise PyCsvInvalidCast("Impossible to convert {v} to float.".format(v=value))

    def __to_date(self, value, fromat_date):
        try:
            return datetime.strptime(value, fromat_date)
        except ValueError:
            raise PyCsvInvalidCast("Impossible to convert {v} to date.".format(v=value))

    def is_col_row(self, col, row):
        if col > self.cols_count or col < 0:
            return False
        if row > self.rows_count or row < 0:
            return False
        return True

    def get_value(self, row, col):
        '''
        :param col: 0 to self.cols_count
        :param row: 0 to self.rows_count
        :return: value or except PyCsvOutBound
        '''

        if col > self.cols_count or col < 0:
            raise PyCsvOutBound("Invalid column {col}.".format(col=col))
        if row > self.rows_count or row < 0:
            raise PyCsvOutBound("Invalid row {row}.".format(row=row))
        return self.data[row][col]

    def fill_file(self, filename, required_headers=None):
        '''
        fill self.data
        :param filename: file name
        :param required_headers: list of header required
        excepts :
            PyCsvExcept
            PyCsvRequiredHeader
            PyCsvInvalidFile
        '''
        file_name = os.path.join(self.path, filename)
        try:
            csvfile = open(file_name, "r")
        except IOError, e:
            csvfile.close()
            raise PyCsvExcept("Connot open file %s, error : %s." % (file_name, str(e)))
        reader = csv.reader(csvfile, delimiter=self.separator)

        if self.with_header:
            for tmp in reader:
                self.header = [col.strip() for col in tmp]
                if not self.__check_headers(required_headers):
                    csvfile.close()
                    raise PyCsvRequiredHeader('The header required not exist.')
                break

        for row in reader:
            if len(row) > 0:
                if self.with_header and len(row) != len(self.header):
                    csvfile.close()
                    raise PyCsvInvalidFile("Invalid file, invalid cloumns number!")
                self.data.append([r.strip() for r in row])
        csvfile.close()

    def content_by_filename(self, filename):
        if filename in self.data:
            return self.data[filename]
        return None

    def column_count(self, filename):
        content = self.content_by_filename(filename)
        if content:
            return len(content[0])
        return -1

    def row_count(self, filename):
        content = self.content_by_filename(filename)
        if content:
            return len(content)
        return -1

    def __order(self, item1, item2):
        def order_by(pos, item1, item2):
            while pos < len(self.columns):
                column = self.columns[pos]
                if item1[pos] > item2[pos]:
                    return column["order"][">"]
                if item1[pos] < item2[pos]:
                    return column["order"]["<"]
                if pos == len(self.columns):
                    return column["order"]["="]
                else:
                    pos = pos + 1
                    order_by(pos, item1, item2)
        return order_by(0, item1, item2)

    def sort_by(self, columns):
        '''
        :param column:
            values : [{"column": "column1", "type": "string", "order": "desc"}
                    {"column": "column1", "type": "integer"}
                    {"column": "column1", "type": "datetime", "format": "%Y%m%d"},
                    {"column": "column1", "type": "datetime", "format": "%H:%M"},
                    {"column": "column1", "type": "float"}]
        '''
        self.__add_and_check_index_column(columns)
        self.data.sort(cmp=self.__order, key=self.__itemgetter())
