import os

import bottle


def run():
    '''
    if __name__ == "__main__":
        from toolbelt.main import run
        run()
    '''
    bottle.BaseRequest.MEMFILE_MAX = os.getenv('MEMFILE_MAX_BYTES', 1024 * 500) # in bytes

    server = os.getenv('SERVER', 'meinheld')
    port = int(os.environ.get('PORT', 3000))
    debug = os.environ.get('DEBUG', '').lower().strip() in ['yes', 'true', '1', 'y', 't']
    debug = True
    if debug:
        print('DEBUG mode')
    if server:
        bottle.run(host='0.0.0.0', port=port, server=server, debug=debug)
    else:
        bottle.run(host='0.0.0.0', port=port, debug=debug)
