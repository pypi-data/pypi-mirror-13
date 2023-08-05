import logging
from pynextcaller.client import NextCallerClient
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
data = {
    'first_name': 'Jerry',
    'last_name': 'Seinfeld',
    'address': '129 West 81st Street',
    'city': 'New York',
    'state': 'NY',
    'zip_code': '10024',
}

client = NextCallerClient(username, password, sandbox=sandbox)

# get by address
try:
    response_content = client.get_by_name_address(data)
    logger.info(response_content)
except HttpException as err:
    logger.error(
        'Response message: {}'.format(err.message),
    )
