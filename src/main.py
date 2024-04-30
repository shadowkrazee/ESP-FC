import sys
import time
import gc
sys.path.append('/lib')
import machine
import esp32
import network
import uasyncio
from microdot import Microdot
from config import FCConfig

rest_server = Microdot()
station = None
pwms = []

# Daddy loves Juniper Alessi

async def init_fans():
    print('Initializing fans...')
    for index, fan in enumerate(FCConfig.fans):
            duty_percent = fan['base_speed']
            duty_16 = int(duty_percent * 65535 / 100)
            pwms.append(machine.PWM(machine.Pin(fan['pwm_pin']), freq=25000, duty_u16=duty_16))
            fan['current_speed'] = duty_percent
            print(f'Fan "{fan['name']}" duty cycle set to: {duty_percent}')

async def init_sensors():
    print('Initializing sensors...')
    # TODO: IMPLEMENT ME
    print(esp32.raw_temperature()) # read the internal temperature of the MCU, in Fahrenheit

async def init_routes():
    global rest_server
    print('Initializing routes...')

    @rest_server.before_request
    async def before(request):
        request.g.start_time = time.time()

    @rest_server.after_request
    async def after(request, response):
        duration = time.time() - request.g.start_time
        print(f'Request to {request.path} took {duration:0.2f} seconds')
        # Collect garbage after eact REST call
        gc.collect()
    
    @rest_server.route('/')
    async def index(request):
        return 'Hello, world!'
    
    @rest_server.route('/fan-speed', methods=['GET', 'POST'])
    async def fan_speed(request):
        response = f'Method "{request.method}" not supported on this route'
        # parse required args (common)
        fan = request.args.get('fan', None)
        fan_config = None
        if fan is None:
                return ({'error': 'Bad Request: param "fan" is required'}, 400)
        
        # Attempt to convert the fan to an int
        try:
             fan = int(fan)
        except:
             pass
        
        if isinstance(fan, str):
             print('fan name provided, searching...')
             match = next((f for f in FCConfig.fans if f['name'] == fan))
             if not match:
                return ({'error': 'Bad Request: param "fan" no matching name found'}, 400)
             print('match found:')
             print(match)
             fan_config = match
        elif isinstance(fan, int):
            if not fan < len(FCConfig.fans):
                return ({'error': 'Bad Request: param "fan" index out of range'}, 400)
            fan_config = FCConfig.fans[fan]
        else:
            return ({'error': 'Bad Request: param "fan" should be an int or string'}, 400)
        
        # Handle GET
        if request.method == 'GET':
            print('Handling GET /fan-speed')
            response = fan_config['current_speed']
        # Handle SET
        elif request.method == 'POST':
            print('Handling POST /fan-speed')
            # Parse out the speed param
            speed = request.args.get('speed', None)
            if speed is None:
                    return ({'error': 'Bad Request: param "speed" is required'}, 400)
            try:
                speed = int(speed)
            except:
                 return ({'error': 'Bad Request: param "speed" must be an integer 1-100'}, 400)
            if (speed < 0 or speed > 100):
                return ({'error': 'Bad Request: param "speed" must be an integer 1-100'}, 400)
            # Set the speed
            # TODO: Fan class with functions..
            duty_percent = speed
            # TODO: Un-hard-code this...
            pwms[0].duty_u16(int(duty_percent * 65535 / 100))
            fan_config['current_speed'] = duty_percent
            response = f'Fan "{fan_config['name']}" duty cycle set to: {duty_percent}'
            print(response)
        
        return str(response)
    
    @rest_server.errorhandler(404)
    async def not_found(request):
        return {'error': 'resource not found'}, 404
    
async def init_network():
  print('Initializing network...')
  global station
  station = network.WLAN(network.STA_IF)
  station.active(True)
  station.config(dhcp_hostname='ESP-FC')
  # Scanning first helps connection reliabliity for some reason
  station.scan()

  try:
    station.connect(FCConfig.wifi['ssid'], FCConfig.wifi['password'])
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
    # Initialize your devices and variables here
    # For example, setup GPIO pins or sensors
    print("ESP-FC started.")
    # Give the fans time to spin up
    await uasyncio.sleep_ms(500)
    await init_fans()
    print('Fans Initialized.')
    await init_sensors()
    print('Sensors Initialized.')
    await init_routes()
    print('Routes Initialized.')
    await init_network()
    network_status = 'Initialized' if station.status() == 1010 else 'Initialization failed'
    print(f'Network {network_status}.')

    rest_server.run(port=8519, debug=True)

if __name__ == "__main__":
    uasyncio.run(main())