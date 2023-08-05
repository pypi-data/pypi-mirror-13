# -*- coding: utf-8 -*-

class OPCData(object):
    def __init__(self, data_id, tag, value, quality, timestamp):
        self._data_id = data_id
        self._tag = tag
        self._value = value
        self._quality = quality
        self._timestamp = timestamp

    @property
    def data_id(self):
        return self._data_id

    @property
    def tag(self):
        return self._tag

    @property
    def value(self):
        return self._value

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def quality(self):
        return self._quality

    def __repr__(self):
        return "<OPCData id:{} tag:{} value:{} timestamp:{} quality:{}>".format(
                self.data_id, self.tag, self.value, self.timestamp, self.quality)
