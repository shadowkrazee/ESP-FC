import sys
import time
import gc
sys.path.append('/lib')
import machine

import network
import uasyncio
from microdot import Microdot
from ESPFC import APIHelper, Config, Fan, Sensor

config: Config
rest_server = Microdot()
station = None

# Daddy loves Juniper Alessi

async def init_config():
    print('Initializing ESP-FC Configuration...')
    global config
    config = Config('config.json')

async def init_routes():
    global rest_server
    print('Initializing routes...')
    # ############################################ #
    # Get current temp of a Sensor by name or index
    @rest_server.route('/temp')
    async def temp(request):
        global config
        response = f'Method "{request.method}" not supported on this route'
        # parse required args (common)
        parsed_args = APIHelper.parse_args(request.args, {'sensor': ('int|string', None)})
        sensor_instance = config.get_sensor(parsed_args['sensor'])
        if sensor_instance is None:
                return ({'Error': f'Bad Request: Sensor "{parsed_args['sensor']}" not found, or index out of range'}, 400)
        current_temp = await sensor_instance.read_temp()
        if current_temp is None:
                return ({'Error': f'Bad Request: Sensor type"{sensor_instance.type}" not yet supported'}, 400)
        response = f'Sensor "{sensor_instance.name}" current temp: {current_temp}'
        return response

    # ############################################ #
    # Get current RPM of a Fan by name or index
    @rest_server.route('/rpm')
    async def rpm(request):
        global config
        response = f'Method "{request.method}" not supported on this route'
        # parse required args (common)
        parsed_args = APIHelper.parse_args(request.args, {'fan': ('int|string', None)})
        fan_instance = config.get_fan(parsed_args['fan'])
        if fan_instance is None:
                return ({'Error': f'Bad Request: Fan "{parsed_args['fan']}" not found, or index out of range'}, 400)
        current_rpm = await fan_instance.read_rpm()
        response = f'WARNING: This feature is not yet fully impemented and currently returns nonsense!\nFan "{parsed_args['fan']}" current rpm: {current_rpm}'
        return response
    
    # ############################################ #
    # Get or Set speed of a fan by name or index
    @rest_server.route('/fan-speed', methods=['GET', 'POST'])
    async def fan_speed(request):
        global config
        response = f'Method "{request.method}" not supported on this route'
        # parse required args (common)
        parsed_args = APIHelper.parse_args(request.args, {'fan': ('int|string', None), 'speed': ('int', None)})
        
        if parsed_args['fan'] is None:
                return ({'Error': 'Bad Request: param "fan: int|string" is required'}, 400)
        
        # Get the Fan instance from the config
        fan_instance = config.get_fan(parsed_args['fan'])
        
        if fan_instance is None:
                return ({'Error': f'Bad Request: Fan "{parsed_args['fan']}" not found, or index out of range'}, 400)
        
        # Handle GET
        if request.method == 'GET':
            print('Handling GET /fan-speed')
            response = fan_instance.current_speed
        # Handle SET
        elif request.method == 'POST':
            print('Handling POST /fan-speed')
            speed = parsed_args['speed']
            if speed is None:
                    return ({'error': 'Bad Request: param "speed: int" is required'}, 400)
            if (speed < 0 or speed > 100):
                return ({'error': 'Bad Request: param "speed" must be an integer 0-100'}, 400)
            # Set the speed
            fan_instance.set_speed(speed)
            response = f'Fan "{fan_instance.name}" duty cycle set to: {fan_instance.current_speed}'
            print(response)
        
        return str(response)
    
    # ############################################ #
    # Global API handlers
    @rest_server.before_request
    async def before(request):
        request.g.start_time = time.time()

    @rest_server.after_request
    async def after(request, response):
        duration = time.time() - request.g.start_time
        print(f'Request to {request.path} took {duration:0.2f} seconds')
        # Collect garbage after eact REST call
        gc.collect()
    
    @rest_server.errorhandler(404)
    async def not_found(request):
        return {'error': '404 - resource not found'}, 404
    
async def init_network():
  print('Initializing network...')
  global station
  station = network.WLAN(network.STA_IF)
  station.active(True)
  station.config(dhcp_hostname='ESP-FC')
  # Scanning first helps connection reliabliity for some reason
  station.scan()

  try:
    station.connect(Config.wifi['ssid'], Config.wifi['password'])
  except Exception as ex:
    print(ex)
    print('Error connecting to network, trying again?')

  # Wait 5 sec or until connected
  tmo = 50
  tries = 3
  while not station.isconnected():
      await uasyncio.sleep_ms(100)
      tmo -= 1
      if tmo == 0:
          tries -= 1
          tmo = 50
          print(f'Connection failed.. {tries} attempts remaining.')
          if (tries > 0):
            station.active(False)
            init_network()
          else:
            break

  print(station.ifconfig())

async def main():
    global rest_server
    print("ESP-FC started.")
    # Give the fans time to spin up
    await uasyncio.sleep_ms(500)
    # Init Config, Fans, and Sensors
    await init_config()
    print('ESP-FC Initialized.')
    # Init API endpoints
    await init_routes()
    print('Routes Initialized.')
    # Init Wifi connection
    await init_network()
    network_status = 'Initialized' if station.status() == 1010 else 'Initialization failed'
    print(f'Network {network_status}.')

    rest_server.run(port=8519, debug=True)

if __name__ == "__main__":
    uasyncio.run(main())