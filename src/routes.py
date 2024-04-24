from microdot import Microdot

def __init__():
    app = Microdot()

    @app.route('/')
    async def index(request):
        return 'Hello, world!'

    app.run()