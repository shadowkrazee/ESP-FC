from machine import Pin, PWM
import utime
import uasyncio
import json
# ############################################ #
#                  ESP-FC Fan                  #
# ############################################ #
class Fan:
    name = ""
    num_fans = 1
    base_speed = 40
    current_speed = base_speed
    pwm_pin : Pin
    tach_pin: Pin
    pwm: PWM
    pulses = 0

    def set_speed(self, duty_percent):
        duty_16 = int(duty_percent * 65535 / 100)
        if duty_16 < 0:
            duty_16 = 0
        elif duty_16 > 65535:
            duty_16 = 65535
        self.pwm = PWM(self.pwm_pin, freq=25000, duty_u16=duty_16)
        self.current_speed = duty_percent
        print(f'Fan "{self.name}" duty cycle set to: {duty_percent}')
    
    async def read_rpm(self):
        global pulses
        pulses = 0
        def count_pulse(p:Pin):
            global pulses
            pulses += 1

        # Record start time
        start_time = utime.ticks_ms()
        # Register interrupt to count pulses for 1 second
        self.tach_pin.irq(trigger=Pin.IRQ_RISING, handler=count_pulse)
        await uasyncio.sleep_ms(1000)
        end_time = utime.ticks_ms()
        # Disable the interrupt
        self.tach_pin.irq(handler=None)
        # Calculate the read duration
        duration = utime.ticks_diff(start_time, end_time)
        # Calculate and return the rpm
        return (pulses / 2) * (60*(duration/1000))


    def __init__(self, cfg_dict):
        # Required keys
        for rk in ['pwm_pin', 'tach_pin']:
            if rk not in cfg_dict:
                raise KeyError(f'Key {rk} is required for type: Fan')
            if not isinstance(cfg_dict[rk], int):
                raise ValueError(f'"{rk}" must be an int!')
            if rk == 'pwm_pin':
                self.pwm_pin = Pin(cfg_dict[rk])
            else:
                self.tach_pin = Pin(cfg_dict[rk], Pin.IN)
        # Optional fields, override defaults if specified
        self.name = cfg_dict.get('name', self.name)
        self.num_fans = cfg_dict.get('num_fans', self.num_fans)
        self.base_speed = cfg_dict.get('base_speed', self.base_speed)
        self.set_speed(self.base_speed)

    def __eq__(self, other):
        return self.pwm_pin == other.pwm_pin or self.tach_pin == other.tach_pin
    
    def __str__(self):
        return self.name

# ############################################ #
#                 ESP-FC Sensor                #
# ############################################ #
class Sensor:
    name = ''
    type = 'UNKNOWN'
    resistance = 10000
    ha_id = ''

    types = {
        'ESP32': 'esp32_onboard',
        'ANALOG': 'analog',
        'HOME_ASSISTANT': 'home-assistant',
        'UNKNOWN': 'unknown'
    }

    def __init__(self, cfg_dict):
        self.name = cfg_dict.get('name', self.name)
        self.type = [k for k, i in self.types.items() if  i == cfg_dict.get('type', 'unknown')][0]
        self.resistance = cfg_dict.get('resistance', self.resistance)
        self.ha_id = cfg_dict.get('ha_id', self.ha_id)

    # TODO: IMPLEMENT ME
    def __eq__():
        return True
    
    def __str__(self):
        return self.name

# ############################################ #
#             ESP-FC Configuration             #
# ############################################ #

class Config:
    wifi = {
        'ssid': '',
        'password': ''
    }
    api = {
        'port': 8519,
        'debug': True
    }
    fans = []
    sensors = []

    # #####################################################
    # Get the Fan instance for a given name or index
    def get_fan(self, fan):
    # Returns: Fan instance, or None if no match
    # 
    # params:
    #   fan: The name or index of the desired Fan 
        fan_match = None
        if isinstance(fan, str):
             print('fan name provided, searching...')
             match = next((f for f in Config.fans if f['name'] == fan))
             if not match:
                return None
             print('match found:')
             print(match)
             fan_match = match
        elif isinstance(fan, int):
            if not fan < len(self.fans):
                return None
            else:
                fan_match = Config.fans[fan]

        return fan_match

    def __init__(self, cfg_file_name='config.sample.json'):
        with open(cfg_file_name) as cfg:
            for k, i in json.load(cfg).items():
                if k == 'wifi':
                    self.wifi.update(i)
                elif k == 'api':
                    self.api.update(i)
                elif k == 'fans':
                    print('Initializing fans...')
                    if not isinstance(i, list):
                        raise ValueError(f'{cfg_file_name} is malformed! "fans" must be an array!')
                    for fan_cfg in i:
                        try:
                            fan_instance = Fan(fan_cfg)
                            if fan_instance not in self.fans:
                                self.fans.append(fan_instance)
                        except(Exception) as ex:
                            print(f'Error initializing Fan instance: {ex}')
                    print(f'Fans: [{', '.join([str(s) for s in self.fans])}]')
                elif k == 'sensors':
                    print('Initializing sensors...')
                    if not isinstance(i, list):
                        raise ValueError(f'{cfg_file_name} is malformed! "sensors" must be an array!')
                    for sensor_cfg in i:
                        try:
                            sensor_instance = Sensor(sensor_cfg)
                            self.sensors.append(sensor_instance)
                        except(Exception) as ex:
                            print(f'Error initializing Sensor instance: {ex}')
                    print(f'Sensors: [{', '.join([str(s) for s in self.sensors])}]')

class APIHelper():
    # ######################################################## #
    # A helper class to encapsulate some common API functions  #
    # ######################################################## #

    # ########################################### 
    # Parse API Args using easy configurations    
    #                                             
    # Returns: a dictionary containing arguments  
    # parsed as configured, or with the provided  
    # default values.                             
    #                                             
    # Params:                                     
    #   args: the args from the request object    
    #   arg_configs: config dict defining desired 
    #       keys, types, and default values.      
    #                                             
    # Example:
    #   arg_configs = {
    #       # list types in order of preference
    #       # separated by '|', first match wins
    #       'fan': ('int|string', None),
    #       'speed': ('int', None)
    #   }
    #   APIHelper.parse_args(request.args, arg_configs)

    @staticmethod
    def parse_args(args, arg_configs):
        types_dict = {
            'int': int,
            'float': float,
            'string': str
        }
        parsed_args = {}
        for key, cfg in arg_configs:
            tps, default_val = cfg
            for typ in tps.split('|'):
                try:
                    inVal = args.get(key, None)
                    outVal = default_val if inVal is None else types_dict.get(typ)(inVal)
                    parsed_args[key] = outVal
                    break
                except(Exception) as ex:
                    print(f'Error attempting to parse "{key}" value "{inVal}" as type "{typ}": {ex}')
        return parsed_args