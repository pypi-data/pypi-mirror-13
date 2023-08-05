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
profile_id = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
account_id = 'test'

client = NextCallerPlatformClient(username, password, sandbox=sandbox)

# update by profile id
try:
    data = {'email': 'test@test.com'}
    client.update_by_profile_id(profile_id, data, account_id)
except HttpException as err:
    logger.error(
        'Response message: {}'.format(err.message),
    )
