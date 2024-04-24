from microdot import Microdot

def __init__():
    print('Hello from routes.py!')
    app = Microdot()

    @app.route('/')
    async def index(request):
        return 'Hello, world!'

    app.run(port=8519, debug=True)