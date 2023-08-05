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
account_id = 'test'
sandbox = True

client = NextCallerPlatformClient(username, password, sandbox=sandbox)

try:
    data = {'email': 'test@test.com'}
    response_content = client.update_platform_account(data, account_id)
    logger.info(response_content)
except HttpException as err:
    logger.error(
        'Response message: {}'.format(err.message),
    )
