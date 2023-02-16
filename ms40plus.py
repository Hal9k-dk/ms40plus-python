import enum
import functools
import operator


def checksum(data):
    return functools.reduce(operator.xor, data)


class Window(enum.Enum):
    StartStop = 0
    RemoteSerial = 8
    SetPointValueHz = 102
    SetPointHysteresis = 105
    BaudRate = 108
    RotationalFrequencySettingHz = 120
    RotationalFrequencySettingRpm = 127
    BusCurrent = 200
    ThreePhaseVoltage = 201
    Power = 202
    DrivingFrequency = 203
    Status = 205
    ErrorCode = 206
    OutputFrequency = 207
    ControllerTemperature = 216
    PowerSupplyTemperature = 222
    OilLevel = 225
    RotationalFrequency = 233
    CycleTime = 300
    CycleNumber = 301
    PumpLife = 302
    TimeWithOilUnderLevel = 305
    TimeWithDirtyFilter = 306
    TimeControllerStandby = 307
    ControllerModelNumber = 319
    PumpModelNumber = 320
    PumpSpecialModelnumber = 321
    PumpSerialNumber = 322
    ControllerSerialNumber = 323
    MaintenanceTimer = 358
    LastHourTemperatureAverage = 362
    LastHourAveragePower = 364
    LastHourAverageFrequency = 365
    LastHourAverageTemperature = 382
    AverageTemperatureDuringPumpLife = 384
    ProgramListingCodeAndRevision = 406
    ParameterListingCodeAndRevision = 407
    Rs485SerialAddressSettings = 503
    SerialType = 504


class Command(enum.Enum):
    Read = 0x30
    Write = 0x31


class Response(enum.Enum):
    Read = 0x30
    Ack = 0x06
    Nack = 0x15
    UnknownWindow = 0x32
    DataTypeError = 0x33
    OutOfRange = 0x34
    WinDisabled = 0x35


class Status(enum.Enum):
    Stop = 0
    WaitInterlock = 1
    Start = 2
    Autotuning = 3
    Normal = 5
    Fail = 6


class Framing:
    def __init__(self):
        self.buffer = bytearray()

    def receive(self, data):
        self.buffer.extend(data)
        try:
            stx_index = self.buffer.index(0x02)
        except ValueError:
            self.buffer.clear()
            return  # no STX found
        try:
            etx_index = self.buffer.index(0x03)
        except ValueError:
            return  # incomplete
        if len(self.buffer) < etx_index + 3:
            return  # incomplete
        try:
            provided_checksum = int(self.buffer[etx_index+1:etx_index+3], 16)
        except ValueError:
            self.buffer.clear()
            print('invalid_checksum')
            return  # invalid checksum
        calculated_checksum = checksum(self.buffer[stx_index+1:etx_index+1])
        if calculated_checksum == provided_checksum:
            payload = self.buffer[stx_index+1:etx_index]
            self.buffer.clear()
            return payload

    def send(self, payload):
        command = bytearray([
            0x02,
            *list(payload),
            0x03
        ])
        calculated_checksum = checksum(command[1:])
        command.extend(bytes([calculated_checksum]).hex().upper().encode())
        return command
