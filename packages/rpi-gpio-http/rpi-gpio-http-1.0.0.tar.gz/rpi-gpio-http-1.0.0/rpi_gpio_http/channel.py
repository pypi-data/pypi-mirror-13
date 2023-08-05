from abc import ABCMeta, abstractmethod
import RPi.GPIO as GPIO
import logging

logger = logging.getLogger(__name__)

class ChannelException(Exception):
    def __init__(self, channel, msg):
        message = "Error occured in channel(%s@%s): %s" % (channel.type, channel.pin, msg)
        super(ChannelException, self).__init__(message)
        self.message = message

class Channel(object):
    type = None

    def __init__(self, pin):
        self.__pin = pin
        GPIO.cleanup(pin)

    @property
    def pin(self):
        return self.__pin

    @abstractmethod
    def get_value(self):
        return GPIO.input(self.pin) == GPIO.HIGH

    @abstractmethod
    def set_value(self, value):
        pass

class InputChannel(Channel):
    pull_types = dict(
        up = GPIO.PUD_UP,
        down = GPIO.PUD_DOWN,
    )

    def __init__(self, pin, pull = None):
        super(InputChannel, self).__init__(pin)
        params = {}
        if pull:
            if pull not in self.pull_types:
                raise ChannelException(self, "Undefined pull type: '%s'" % pull)
            params['pull_up_down'] = self.pull_types[pull]
        GPIO.setup(pin, GPIO.IN, **params)

    def set_value(self, value):
        raise ChannelException(self, "Cannot set value for input!")

class OutputChannel(Channel):
    def __init__(self, pin):
        super(OutputChannel, self).__init__(pin)
        GPIO.setup(pin, GPIO.OUT)

class PWMChannel(OutputChannel):
    def __init__(self, pin, frequency):
        super(PWMChannel, self).__init__(pin)
        self.__pwm = GPIO.PWM(self.pin, frequency)
        self.__started = False
        self.__value = 0

    def set_value(self, value):
        self.__value = value
        if self.__started:
            self.__pwm.ChangeDutyCycle(value)
        else:
            self.__pwm.start(value)
            self.__started = True

    def get_value(self):
        return self.__value

class ChannelFactory(object):
    channel_types = dict(
        input = InputChannel,
        output = OutputChannel,
        pwm = PWMChannel,
    )

    @staticmethod
    def create(channel_config):
        type = channel_config['type']
        if type not in ChannelFactory.channel_types:
            logger.error("Undefined channel type: '%s'" % type)
            return None
        params = {}
        if 'params' in channel_config:
            params.update(channel_config['params'])
        channel = ChannelFactory.channel_types[type](channel_config['pin'], **params)
        channel.type = type
        logger.info("Channel %s@%s created" % (type, channel.pin))
        return channel
