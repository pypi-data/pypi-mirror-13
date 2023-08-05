class System:
    """Class to get various System information's of a device which supports ``urn:dslforum-org:service:DeviceInfo:1``
    and ``urn:dslforum-org:service:Time:1``.

    The class supports devices which supports ``urn:dslforum-org:service:Time:1`` and
    ``urn:dslforum-org:service:DeviceInfo:1``
    namespace. Unless the device is a AVM Fritz Box the DeviceTR64 objects needs to load the device definitions with
    :meth:`~simpletr64.DeviceTR64.loadDeviceDefinitions` before the usage of any of the methods. For a Fritz.box
    :meth:`~simpletr64.DeviceTR64.setupTR64Device` has to be called. Also a device might not
    support all of the actions. This class does not implement all of the actions of this namespace, please check the
    SCPD definitions if you miss some functionality. This library provides some tools to gather the needed
    information's.

    .. seealso::

        :meth:`~simpletr64.DeviceTR64.loadDeviceDefinitions`, :meth:`~simpletr64.DeviceTR64.loadSCPD`,
        :meth:`~simpletr64.DeviceTR64.setupTR64Device`

        The tools which have been provided with this library shows good use of the full library.
    """
    def __init__(self, deviceTR64):
        """Initialize the object.

        :param DeviceTR64 deviceTR64: an initialized DeviceTR64 object
        :rtype: System
        """
        self.__device = deviceTR64

    def getSystemInfo(self):
        """Execute GetInfo action to get information's about the System on the device.

        :return: information's about the System on the device.
        :rtype: SystemInfo
        """
        namespace = "urn:dslforum-org:service:DeviceInfo:1"
        uri = self.__device.getControlURL(namespace)

        results = self.__device.execute(uri, namespace, "GetInfo")

        return SystemInfo(results)

    def reboot(self):
        """Reboot the device"""
        namespace = "urn:dslforum-org:service:DeviceConfig:1"
        uri = self.__device.getControlURL(namespace)

        client = self.__device.getConnection(uri, namespace)
        client.Reboot()

    def getTimeInfo(self):
        """Execute GetInfo action to get information's about the time on the device.

        :return: information's about the time on the device.
        :rtype: TimeInfo
        """
        namespace = "urn:dslforum-org:service:Time:1"
        uri = self.__device.getControlURL(namespace)

        results = self.__device.execute(uri, namespace, "GetInfo")

        return TimeInfo(results)


class TimeInfo:
    """A container class for time information's."""

    def __init__(self, results):
        """Initialize an object

        :param results: action results of an GetInfo action
        :type results: dict[str,str]
        :rtype: TimeInfo
        """
        self.__ntpServer1 = results["NewNTPServer1"]
        self.__ntpServer2 = results["NewNTPServer2"]
        self.__currentLocalTime = results["NewCurrentLocalTime"]
        self.__localTimeZone = results["NewLocalTimeZone"]
        self.__isDaylightSaving = results["NewLocalTimeZoneName"]
        self.__daylightSavingStart = bool(results["NewDaylightSavingsUsed"])
        self.__daylightSavingEnd = results["NewDaylightSavingsStart"]
        self.__localTimeZoneName = results["NewDaylightSavingsEnd"]
        self.__raw = results

    @property
    def raw(self):
        """Return the raw results which have been used to initialize the object.

        :return: the raw results
        :rtype: dict[str,str]
        """
        return self.__raw

    @property
    def ntpServer1(self):
        """Return the first configured NTP server.

        :return: the first configured NTP server.
        :rtype: str
        """
        return self.__ntpServer1

    @property
    def ntpServer2(self):
        """Return the second configured NTP server.

        :return: the second configured NTP server.
        :rtype: str
        """
        return self.__ntpServer2

    @property
    def currentLocalTime(self):
        """Return current local time.

        :return: current local time.
        :rtype: str
        """
        return self.__currentLocalTime

    @property
    def localTimeZone(self):
        """Return the local time zone.

        :return: the local time zone.
        :rtype: str
        """
        return self.__localTimeZone

    @property
    def localTimeZoneName(self):
        """Return the name of the local time zone.

        :return: the name of the local time zone.
        :rtype: str
        """
        return self.__localTimeZoneName

    @property
    def isDaylightSaving(self):
        """Return if it is now day light saving time.

        :return: if it is now day light saving time.
        :rtype: bool
        """
        return self.__isDaylightSaving

    @property
    def daylightSavingStart(self):
        """Return when the day light saving time starts.

        :return: when the day light saving time starts.
        :rtype: str
        """
        return self.__daylightSavingStart

    @property
    def daylightSavingEnd(self):
        """Return when the day light saving time ends.

        :return: when the day light saving time ends.
        :rtype: str
        """
        return self.__daylightSavingEnd


class SystemInfo:
    """A container class for System information's."""

    def __init__(self, results):
        """Initialize an object

        :param results: action results of an GetInfo action
        :type results: dict[str,str]
        :rtype: SystemInfo
        """
        self.__manufactureName = results["NewManufacturerName"]
        self.__modelName = results["NewModelName"]
        self.__description = results["NewDescription"]
        self.__serialNumber = results["NewSerialNumber"]
        self.__softwareVersion = results["NewSoftwareVersion"]
        self.__hwVersion = results["NewHardwareVersion"]
        self.__uptime = int(results["NewUpTime"])
        self.__log = results["NewDeviceLog"]
        self.__raw = results

    @property
    def raw(self):
        """Return the raw results which have been used to initialize the object.

        :return: the raw results
        :rtype: dict[str,str]
        """
        return self.__raw

    @property
    def manufactureName(self):
        """Return the name of the manufacture of the device.

        :return: the name of the manufacture of the device.
        :rtype: str
        """
        return self.__manufactureName

    @property
    def modelName(self):
        """Return the name of the model of the device.

        :return: the name of the model of the device.
        :rtype: str
        """
        return self.__modelName

    @property
    def description(self):
        """Return a description of the device.

        :return: a description of the device
        :rtype: str
        """
        return self.__description

    @property
    def serialNumber(self):
        """Return the serial number of the system.

        :return: the serial number of the system.
        :rtype: str
        """
        return self.__serialNumber

    @property
    def softwareVersion(self):
        """Return the software version of the system.

        :return: the software version of the system.
        :rtype: str
        """
        return self.__softwareVersion

    @property
    def hwVersion(self):
        """Return the hardware version of the system.

        :return: the hardware version of the system.
        :rtype: str
        """
        return self.__hwVersion

    @property
    def uptime(self):
        """Return the uptime of the system.

        :return: the uptime of the system.
        :rtype: int
        """
        return self.__uptime

    @property
    def log(self):
        """Return the last lines in the log file.

        :return: the last lines in the log file.
        :rtype: str
        """
        return self.__log
