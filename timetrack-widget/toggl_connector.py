from toggl.api_client import TogglClientApi

settings = {
    'token': 'xxx',
    'user_agent': 'your app name'
}
toggle_client = TogglClientApi(settings)