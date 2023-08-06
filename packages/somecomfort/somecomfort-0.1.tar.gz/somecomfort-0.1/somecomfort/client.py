import contextlib
import copy
import logging
import requests
import time


_LOG = logging.getLogger('somecomfort')
FAN_MODES = ['auto', 'on', 'circulate']
SYSTEM_MODES = ['auto', 'heat', 'off', 'cool']


class SomeComfortError(Exception):
    pass


class ConnectionTimeout(SomeComfortError):
    pass


class ConnectionError(SomeComfortError):
    pass


class AuthError(SomeComfortError):
    pass


class APIError(SomeComfortError):
    pass


class APIRateLimited(APIError):
    def __init__(self):
        super(APIRateLimited, self).__init__(
            'You are being rate-limited. Try waiting a bit.')


class SessionTimedOut(SomeComfortError):
    pass


def _convert_errors(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except requests.exceptions.Timeout:
            raise ConnectionTimeout()
        except requests.exceptions.ConnectionError:
            raise ConnectionError()
    return wrapper


class Device(object):
    def __init__(self, client, location):
        self._client = client
        self._location = location
        self._data = {}
        self._last_refresh = 0
        self._alive = None
        self._commslost = None

    @classmethod
    def from_location_response(cls, client, location, response):
        self = cls(client, location)
        self._deviceid = response['DeviceID']
        self._macid = response['MacID']
        self._name = response['Name']
        self.refresh()
        return self

    def refresh(self):
        data = self._client._get_thermostat_data(self.deviceid)
        if not data['success']:
            raise APIError('API reported failure to query device %s' % (
                self.deviceid))
        self._alive = data['deviceLive']
        self._commslost = data['communicationLost']
        self._data = data['latestData']
        self._last_refresh = time.time()

    @property
    def deviceid(self):
        """The device identifier"""
        return self._deviceid

    @property
    def mac_address(self):
        """The MAC address of the device"""
        return self._macid

    @property
    def name(self):
        """The user-set name of this device"""
        return self._name

    @property
    def is_alive(self):
        """A boolean indicating whether the device is connected"""
        return self._alive and not self._commslost

    @property
    def fan_running(self):
        """Returns a boolean indicating the current state of the fan"""
        return self._data['fanData']['fanIsRunning']

    @property
    def fan_mode(self):
        """Returns one of FAN_MODES indicating the current setting"""
        try:
            return FAN_MODES[self._data['fanData']['fanMode']]
        except KeyError:
            raise APIError(
                'Unknown fan mode %i' % self._data['fanData']['fanMode'])

    @fan_mode.setter
    def fan_mode(self, mode):
        try:
            mode_index = FAN_MODES.index(mode)
        except ValueError:
            raise SomeComfortError('Invalid fan mode `%s`' % mode)

        key = 'fanMode%sAllowed' % mode.title()
        if not self._data['fanData'][key]:
            raise SomeComfortError('Device does not support %s' % mode)
        self._client._set_thermostat_settings(
            self.deviceid, {'FanMode': mode_index})
        self._data['fanData']['fanMode'] = mode_index

    @property
    def system_mode(self):
        """Returns one of SYSTEM_MODES indicating the current setting"""
        try:
            return SYSTEM_MODES[self._data['uiData']['SystemSwitchPosition']]
        except KeyError:
            raise APIError(
                'Unknown system mode %i' % (
                    self._data['uiData']['SystemSwitchPosition']))

    @system_mode.setter
    def system_mode(self, mode):
        try:
            mode_index = SYSTEM_MODES.index(mode)
        except ValueError:
            raise SomeComfortError('Invalid system mode `%s`' % mode)

        key = 'Switch%sAllowed' % mode.title()
        if not self._data['uiData'][key]:
            raise SomeComfortError('Device does not support %s' % mode)
        self._client._set_thermostat_settings(
            self.deviceid, {'SystemSwitch': mode_index})
        self._data['uiData']['SystemSwitchPosition'] = mode_index

    @property
    def setpoint_cool(self):
        """The target temperature when in cooling mode"""
        return self._data['uiData']['CoolSetpoint']

    @setpoint_cool.setter
    def setpoint_cool(self, temp):
        lower = self._data['uiData']['CoolLowerSetptLimit']
        upper = self._data['uiData']['CoolUpperSetptLimit']
        if temp > upper or temp < lower:
            raise SomeComfortError('Setpoint outside range %.1f-%.1f' % (
                lower, upper))
        self._client._set_thermostat_settings(self.deviceid,
                                              {'CoolSetpoint': temp})
        self._data['uiData']['CoolSetpoint'] = temp

    @property
    def setpoint_heat(self):
        """The target temperature when in heating mode"""
        return self._data['uiData']['HeatSetpoint']

    @setpoint_heat.setter
    def setpoint_heat(self, temp):
        lower = self._data['uiData']['HeatLowerSetptLimit']
        upper = self._data['uiData']['HeatUpperSetptLimit']
        if temp > upper or temp < lower:
            raise SomeComfortError('Setpoint outside range %.1f-%.1f' % (
                lower, upper))
        self._client._set_thermostat_settings(self.deviceid,
                                              {'HeatSetpoint': temp})
        self._data['uiData']['HeatSetpoint'] = temp

    @property
    def current_temperature(self):
        """The current measured ambient temperature"""
        return self._data['uiData']['DispTemperature']

    @property
    def temperature_unit(self):
        """The temperature unit currently in use. Either 'F' or 'C'"""
        return self._data['uiData']['DisplayUnits']

    @property
    def raw_ui_data(self):
        """The raw uiData structure from the API.

        Note that this is read only!
        """
        return copy.deepcopy(self._data['uiData'])

    @property
    def raw_fan_data(self):
        """The raw fanData structure from the API.

        Note that this is read only!
        """
        return copy.deepcopy(self._data['fanData'])

    @property
    def raw_dr_data(self):
        """The raw drData structure from the API.

        Note that this is read only!
        """
        return copy.deepcopy(self._data['drData'])

    def __repr__(self):
        return 'Device<%s:%s>' % (self.deviceid, self.name)


class Location(object):
    def __init__(self, client):
        self._client = client
        self._devices = {}
        self._locationid = 'unknown'

    @classmethod
    def from_api_response(cls, client, api_response):
        self = cls(client)
        self._locationid = api_response['LocationID']
        devices = api_response['Devices']
        _devices = [Device.from_location_response(client, self, dev)
                    for dev in devices]
        self._devices = {dev.deviceid: dev for dev in _devices}
        return self

    @property
    def devices_by_id(self):
        """A dict of devices indexed by DeviceID"""
        return self._devices

    @property
    def devices_by_name(self):
        """A dict of devices indexed by name.

        Note that if you have multiple devices with the same name,
        this may not return them all!
        """
        return {dev.name: dev for dev in self._devices}

    @property
    def locationid(self):
        """The location identifier"""
        return self._locationid

    def __repr__(self):
        return 'Location<%s>' % self.locationid


class SomeComfort(object):
    def __init__(self, username, password, timeout=30):
        self._username = username
        self._password = password
        self._session = self._get_session()
        self._session.headers['X-Requested-With'] = 'XMLHttpRequest'
        self._timeout = timeout
        self._locations = {}
        self._baseurl = 'https://mytotalconnectcomfort.com/portal'
        self._login()
        self._discover()

    @staticmethod
    def _get_session():
        return requests.Session()

    @_convert_errors
    def _login(self):
        self._session.get(self._baseurl, timeout=self._timeout)
        params = {'UserName': self._username,
                  'Password': self._password,
                  'RememberMe': 'false',
                  'timeOffset': 480}
        resp = self._session.post(self._baseurl, params=params,
                                  timeout=self._timeout)
        if resp.status_code != 200:
            _LOG.error('Login as %s failed', self._username)
            raise AuthError('Login failed')

    @staticmethod
    def _resp_json(resp, req):
        try:
            return resp.json()
        except:
            # Any error doing this is probably because we didn't
            # get JSON back (the API is terrible about this).
            _LOG.exception('Failed to de-JSON %s response' % req)
            raise APIError('Failed to process %s response', req)

    def _request_json(self, method, *args, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self._timeout

        resp = getattr(self._session, method)(*args, **kwargs)
        req = args[0].replace(self._baseurl, '')

        if resp.status_code == 200:
            return self._resp_json(resp, req)
        elif resp.status_code == 401:
            raise APIRateLimited()
        else:
            _LOG.error('API returned %i from %s request',
                       resp.status_code, req)
            raise APIError('Unexpected %i response from API' % (
                resp.status_code))

    def _get_json(self, *args, **kwargs):
        return self._request_json('get', *args, **kwargs)

    def _post_json(self, *args, **kwargs):
        return self._request_json('post', *args, **kwargs)

    @contextlib.contextmanager
    def _retries_login(self):
        try:
            self.keepalive()
        except SessionTimedOut:
            self._login()

        yield

    def _get_locations(self):
        url = '%s/Location/GetLocationListData' % self._baseurl
        params = {'page': 1,
                  'filter': ''}
        with self._retries_login():
            return self._post_json(url, params=params)

    def _get_thermostat_data(self, thermostat_id):
        url = '%s/Device/CheckDataSession/%s' % (self._baseurl, thermostat_id)
        with self._retries_login():
            return self._get_json(url)

    def _set_thermostat_settings(self, thermostat_id, settings):
        data = {'SystemSwitch': None,
                'HeatSetpoint': None,
                'CoolSetpoint': None,
                'HeatNextPeriod': None,
                'CoolNextPeriod': None,
                'StatusHeat': None,
                'DeviceID': thermostat_id,
            }
        data.update(settings)
        url = '%s/Device/SubmitControlScreenChanges' % self._baseurl
        with self._retries_login():
            result = self._post_json(url, data=data)
            if result.get('success') != 1:
                raise APIError('API rejected thermostat settings')

    def keepalive(self):
        """Makes a keepalive request to avoid session timeout.

        Raises SessionTimedOut if the session has timed out.
        """
        url = '%s/Account/KeepAlive' % self._baseurl
        resp = self._session.get(url, timeout=self._timeout)
        if resp.status_code != 200:
            _LOG.info('Session timed out')
            raise SessionTimedOut('Session timed out')
        _LOG.info('Session refreshed')

    @_convert_errors
    def _discover(self):
        raw_locations = self._get_locations()
        for raw_location in raw_locations:
            try:
                location = Location.from_api_response(self, raw_location)
            except KeyError as ex:
                _LOG.error(('Failed to process location `%s`: '
                            'missing %s element'),
                           raw_location.get('LocationID', 'unknown'),
                           ex.args[0])
            self._locations[location.locationid] = location

    @property
    def locations_by_id(self):
        """A dict of all locations indexed by id"""
        return self._locations
