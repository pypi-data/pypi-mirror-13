import logging
from pynextcaller.client import NextCallerPlatformClient
from pynextcaller.exceptions import HttpException


logger = logging.getLogger('nextcaller')
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

username = 'XXXXX'
password = 'XXXXX'
sandbox = True

client = NextCallerPlatformClient(username, password, sandbox=sandbox)

try:
    data = {
        'id': 'test_username',
        'first_name': 'Clark',
        'last_name': 'Kent',
        'email': 'test@test.com'
    }
    response_content = client.create_platform_account(data)
    logger.info(response_content)
except HttpException as err:
    logger.error(
        'Response message: {}'.format(err.message),
    )
