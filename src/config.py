

# ############################################ #
#             ESP-FC Configuration             #
# ############################################ #

class FCConfig:

    # #################################### #
    #           Wifi Credentials           #
    # #################################### #
    wifi = {
        'ssid': 'Tomorrowland',
        'password': 'Epcot19!'
    }
    # #################################### #
    #           API Configuration          #
    # #################################### #
    api = {
        'port': 8519,
        'debug': True
    }
    # #################################### #
    #           Fan Configuration          #
    # #################################### #
    fans = [
        {
            'name': 'exhaust',
            'num_fans': 4,
            'base_speed': 40,
            'pwm_pin': 21,
            'tach_pin': 19
        }
    ]
    # #################################### #
    #         Sensor Configuration         #
    # #################################### #
    sensors = [
        {
            'name': 'esp',
            'type': 'esp32_onboard'
        },
        # {
        #     'name': 'inline',
        #     'type': 'analog',
        #     'resistance': '10k',
        #     'pin': 12
        # },
        # {
        #     'name': 'system',
        #     'type': 'home-assistant',
        #     'ha_id': 'idk1'
        # },
        # {
        #     'name': 'intake',
        #     'type': 'home-assistant',
        #     'ha_id': 'idk2'
        # },
        # {
        #     'name': 'exhaust',
        #     'type': 'home-assistant',
        #     'ha_id': 'idk3'
        # }
    ]