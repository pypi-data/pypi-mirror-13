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

# get by profile id
try:
    response_content = client.get_by_profile_id(profile_id, account_id)
    logger.info(response_content)
except HttpException as err:
    logger.error(
        'Response message: {}'.format(err.message),
    )
