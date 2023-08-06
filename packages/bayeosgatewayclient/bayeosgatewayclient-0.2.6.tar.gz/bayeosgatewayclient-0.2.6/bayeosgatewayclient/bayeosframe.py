"""Implementation of BayEOS Frame Protocol Specification."""

from struct import pack, unpack
from time import time
from datetime import datetime
from abc import abstractmethod

REFERENCE_TIME_DIF = (datetime(2000, 1, 1) -
                              datetime(1970, 1, 1)).total_seconds()

class BayEOSFrame(object):
    """Factory Class for BayEOS Frames."""

    @staticmethod
    def factory(frame_type=0x1):
        """Instantiates a BayEOS Frame object regarding Frame Type."""
        try:
            return FRAME_TYPES[frame_type]['class'](frame_type)
        except KeyError as err:
            print 'Frame Type ' + str(err) + ' not found.'

    def __init__(self, frame_type=0x1):
        """Creates the binary Frame Type header of BayEOS Frames."""
        self.frame_type = frame_type
        self.frame = pack('<b', frame_type)

    @abstractmethod
    def create(self, *args):
        """Initialized a BayEOS Frame with its Frame Type specific attributes.
        @param *args: list of positional arguments
        """
        return

    @abstractmethod
    def parse(self):
        """Parses a binary coded BayEOS Frame into a Python dictionary."""
        return {'name' : FRAME_TYPES[self.frame_type]['name']}

    def to_string(self):
        """Prints a readable form of the BayEOS Frame."""
        print self.parse()

    def get_name(self):
        """Returns the Frame name regarding its Frame Type."""
        return FRAME_TYPES[self.frame_type]['name']

    def get_payload(self):
        """Returns a Python tuple containing the Payload."""
        return self.parse()[1:]

    @staticmethod
    def to_object(frame):
        """Initializes a BayEOSFrame object from a binary coded frame.
        @param frame: binary coded String
        @returns BayEOSFrame object
        """
        try:
            frame_type = unpack('<b', frame[0:1])[0]
            return BayEOSFrame.factory(frame_type)
        except TypeError as err:
            print 'Error in to_object method: ' + str(err)

    @staticmethod
    def parse_frame(frame):
        """Parses a binary coded BayEOS Frame into a Python dictionary.
        @param frame: binary coded String
        @return Python dictionary
        """
        try:
            bayeos_frame = BayEOSFrame.to_object(frame)
            bayeos_frame.frame = frame
            return bayeos_frame.parse()
        except AttributeError as err:
            print 'Error in parse_frame method: ' + str(err)

class DataFrame(BayEOSFrame):
    """Data Frame Factory class."""
    def create(self, values=(), value_type=0x41, offset=0):
        """Creates a BayEOS Data Frame.
        @param values: list, tuple or dictionary with channel number keys
        @param value_type: defines Offset and Data Type
        @param offset: length of Channel Offset (if Offset Type is 0x0)
        """
        if type(values) is dict:
            val_list = []            
            for key, value in values.iteritems():
                val_list.append((key,value))
            values = val_list
        value_type = int(value_type)
        frame = pack('<b', value_type)
        offset_type = (0xf0 & value_type)  # first four bits of the Value Type
        data_type = (0x0f & value_type)  # last four bits of the Value Type
        try:
            val_format = DATA_TYPES[data_type]['format']  # search DATA_TYPES Dictionary
        except KeyError as err:
            print 'Error in create method for Data Frame: Data Type ' + str(err) + ' is not defined.'
            return

        if offset_type == 0x0:  # Data Frame with channel offset
            frame += pack('<b', offset)  # 1 byte channel offset

        try:
            for [key, each_value] in values:
                if offset_type == 0x40:  # Data Frame with channel indices
                    frame += pack('<b', key)
                frame += pack(val_format, each_value)
        except TypeError:
            key = 1
            for each_value in values:  # simple Data Frame, Offset Type is 0x2
                if offset_type == 0x40:  # Data Frame with channel indices
                    frame += pack('<b', key)
                    key += 1
                frame += pack(val_format, each_value)
        self.frame += frame

    def parse(self):
        """Parses a binary coded BayEOS Data Frame into a Python dictionary.
        @return tuples of channel indices and values
        """
        if unpack('<b', self.frame[0:1])[0] != 0x1:
            print 'This is not a Data Frame.'
            return False
        value_type = unpack('<b', self.frame[1:2])[0]
        offset_type = 0xf0 & value_type
        data_type = 0x0f & value_type
        val_format = DATA_TYPES[data_type]['format']
        val_length = DATA_TYPES[data_type]['length']
        pos = 2
        key = 0
        payload = {}
        if offset_type == 0x0:
            key = unpack('<b', self.frame[2:3])[0]  # offset
            pos += 1
        while pos < len(self.frame):
            if offset_type == 0x40:
                key = unpack('<b', self.frame[pos:pos + 1])[0]
                pos += 1
            else:
                key += 1
            value = unpack('<' + val_format, self.frame[pos:pos + val_length])[0]
            pos += val_length
            payload[key] = value
        return BayEOSFrame.parse(self), {'values' : payload}

class CommandFrame(BayEOSFrame):
    """Command and Command Response Frame Factory class."""
    def create(self, cmd_type, cmd):
        """Creates a BayEOS Command or Command Response Frame.
        @param cmd_type: type of command
        @param cmd: instruction for or response from receiver
        """
        self.frame += pack('<b', cmd_type) + cmd

    def parse(self):
        """Parses a binary coded Command Frame into a Python dictionary.
        @return command type and instruction
        """
        return BayEOSFrame.parse(self), {'cmd_type' : unpack('<b', self.frame[1:2])[0],
                                         'cmd' : self.frame[2:]}

class MessageFrame(BayEOSFrame):
    """Message and Error Message Frame Factory class."""
    def create(self, message):
        """Creates a BayEOS Message or Error Message Frame.
        @param message: message to save
        """
        self.frame += message

    def parse(self):
        """Parses a binary coded Message Frame into a Python dictionary.
        @return message
        """
        return BayEOSFrame.parse(self), {'message' : self.frame[1:]}

class RoutedFrame(BayEOSFrame):
    """Routed Frame Factory class."""
    def create(self, my_id, pan_id, nested_frame):
        """
        Creates a BayEOS Routed Frame.
        @param my_id: TX-XBee MyId
        @param pan_id: XBee PANID
        @param nested_frame: valid BayEOS Frame
        """
        self.frame += pack('<h', my_id) + pack('<h', pan_id) + nested_frame

    def parse(self):
        """Parses a binary coded Routed Frame into a Python dictionary.
        @return TX-XBee MyId, XBee PANID, nested frame as a binary String
        """
        nested_frame = BayEOSFrame.parse_frame(self.frame[5:])
        return BayEOSFrame.parse(self), {'my_id' : unpack('<h', self.frame[1:3])[0],
                                         'pan_id' : unpack('<h', self.frame[3:5])[0],
                                         'nested_frame' : nested_frame}

class RoutedRSSIFrame(BayEOSFrame):
    """Routed RSSI Frame Factory class."""
    def create(self, my_id, pan_id, nested_frame, rssi=''):
        """Creates a BayEOS Routed RSSI Frame.
        @param my_id: TX-XBee MyId
        @param pan_id: XBee PANID
        @param rssi: Remote Signal Strength Indicator
        @param nested_frame: valid BayEOS Frame
        """
        ids = pack('<h', my_id) + pack('<h', pan_id)
        if rssi:
            self.frame += ids + pack('<b', rssi) + nested_frame
        self.frame += ids + nested_frame

    def parse(self):
        """Parses a binary coded Routed RSSI Frame into a Python dictionary.
        @return TX-XBee MyId, XBee PANID, RSSI, nested frame as a binary String
        """
        nested_frame = BayEOSFrame.parse_frame(self.frame[6:])
        return BayEOSFrame.parse(self), {'my_id' : unpack('<h', self.frame[1:3])[0],
                                         'pan_id' : unpack('<h', self.frame[3:5])[0],
                                         'rssi' : unpack('<b', self.frame[5:6])[0],
                                         'nested_frame' : nested_frame}

class DelayedFrame(BayEOSFrame):
    """Delayed Frame Factory class."""
    def create(self, nested_frame, delay=0):
        """Creates a BayEOS Delayed Frame.
        @param nested_frame: valid BayEOS Frame
        @param delay: delay in milliseconds
        """
        if not delay:
            delay = time()
        timestamp = round((time() - delay) * 1000)
        print timestamp
        self.frame += pack('<l', timestamp) + nested_frame
        self.nested_frame = nested_frame

    def parse(self):
        """Parses a binary coded Delayed Frame into a Python dictionary.
        @return timestamp and nested_frame as a binary String
        """
        nested_frame = BayEOSFrame.parse_frame(self.frame[5:])
        return BayEOSFrame.parse(self), {'timestamp' : unpack('<l', self.frame[1:5])[0],
                                         'nested_frame' : nested_frame}

class OriginFrame(BayEOSFrame):
    """Origin Frame Factory class."""
    def create(self, origin, nested_frame):
        """Creates a BayEOS Origin Frame.
        @param origin: name to appear in the gateway
        @param nested_frame: valid BayEOS frame
        """
        origin = origin[0:255]
        self.frame += pack('<b', len(origin)) + origin + nested_frame
        self.nested_frame = nested_frame

    def parse(self):
        """Parses a binary coded Origin Frame into a Python dictionary.
        @return origin and nested_frame as a binary String
        """
        length = unpack('<b', self.frame[1:2])[0]
        nested_frame = BayEOSFrame.parse_frame(self.frame[length + 2:])
        return BayEOSFrame.parse(self), {'origin' : self.frame[2:length + 2],
                                         'nested_frame' : nested_frame}

class BinaryFrame(BayEOSFrame):
    """Binary Frame Factory class."""
    def create(self, string):
        """Creates a BayEOS Frame including a binary coded String
        @param string: message to pack
        """
        length = len(string)
        self.frame += pack('<f', length) + pack(str(length) + 's', string)

    def parse(self):
        """Parses a binary coded Binary Frame into a Python dictionary.
        @return length and content of a String
        """
        return BayEOSFrame.parse(self), {'length' : unpack('<f', self.frame[1:5])[0],
                                         'string' : self.frame[5:]}

class TimestampFrameSec(BayEOSFrame):
    """Timestamp Frame (s) Factory class."""
    def create(self, nested_frame, timestamp=0):
        """Creates a BayEOS Timestamp Frame with second precision
        @param nested_frame: valid BayEOS frame
        @param timestamp: time in seconds
        """
        if not timestamp:
            timestamp = time()
        # seconds since 1st of January, 2000
        time_since_reference = round(timestamp - REFERENCE_TIME_DIF)
        self.frame += pack('<l', time_since_reference) + nested_frame
        self.nested_frame = nested_frame

    def parse(self):
        """Parses a binary coded Timestamp Frame (s) into a Python dictionary.
        @return timestamp and nested_frame as a binary String
        """
        nested_frame = BayEOSFrame.parse_frame(self.frame[5:])
        return BayEOSFrame.parse(self), {'timestamp' : unpack('<l', self.frame[1:5])[0],
                                         'nested_frame' : nested_frame}

class TimestampFrame(BayEOSFrame):
    """Timestamp Frame (ms) Factory class."""
    def create(self, nested_frame, timestamp=0):
        """Creates a BayEOS Timestamp Frame with millisecond precision
        @param nested_frame: valid BayEOS frame
        @param timestamp: time
        """
        if not timestamp:
            timestamp = time()
        self.frame += pack('<q', round(timestamp * 1000)) + nested_frame
        self.nested_frame = nested_frame

    def parse(self):
        """Parses a binary coded Timestamp Frame (ms) into a Python dictionary.
        @return timestamp and nested_frame as a binary String"""
        nested_frame = BayEOSFrame.parse_frame(self.frame[9:])
        return BayEOSFrame.parse(self), {'timestamp' : unpack('<q', self.frame[1:9])[0],
                                         'nested_frame' : nested_frame}

DATA_TYPES = {0x1 : {'format' : '<f', 'length' : 4},  # float32 4 bytes
              0x2 : {'format' : '<i', 'length' : 4},  # int32 4 bytes
              0x3 : {'format' : '<h', 'length' : 2},  # int16 2 bytes
              0x4 : {'format' : '<b', 'length' : 1},  # int8 1 byte
              0x5 : {'format' : '<q', 'length' : 8}}  # double 8 bytes

FRAME_TYPES = {0x1: {'name' : 'Data Frame',
                     'class' : DataFrame},
               0x2: {'name' : 'Command Frame',
                     'class' : CommandFrame},
               0x3: {'name' : 'Command Response Frame',
                     'class' : CommandFrame},
               0x4: {'name' : 'Message Frame',
                     'class' : MessageFrame},
               0x5: {'name' : 'Error Message Frame',
                     'class' : MessageFrame},
               0x6: {'name' : 'Routed Frame',
                     'class' : RoutedFrame},
               0x7: {'name' : 'Delayed Frame',
                     'class' : DelayedFrame},
               0x8: {'name' : 'Routed RSSI Frame',
                     'class' : RoutedRSSIFrame},
               0x9: {'name' : 'Timestamp Frame',
                     'class' : TimestampFrameSec},
               0xa: {'name' : 'Binary',
                     'class' : BinaryFrame},
               0xb: {'name' : 'Origin Frame',
                     'class' : OriginFrame},
               0xc: {'name' : 'Timestamp Frame',
                     'class' : TimestampFrame}}

# swaps keys and values in FRAME_TYPES Dictionary
# FRAME_NAMES = {value['name']:key for key, value in FRAME_TYPES.iteritems()}
# for key, value in FRAME_NAMES.iteritems():
#     print key, value