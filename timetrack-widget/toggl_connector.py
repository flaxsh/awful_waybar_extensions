from toggl.api_client import TogglClientApi
import json




if __name__ == '__main__':
    credentials = json.load(open('credentials.json'))
    settings = {
        'token': credentials['TOGGL_TOKEN'],
        'user_agent': 'WaybarTogglWidget'
    }
    toggle_client = TogglClientApi(settings)
    pass