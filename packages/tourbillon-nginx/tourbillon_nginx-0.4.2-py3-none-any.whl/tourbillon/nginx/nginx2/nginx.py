import logging
import re

import requests
import trollius as asyncio
from trollius import From


logger = logging.getLogger(__name__)


@asyncio.coroutine
def get_nginx_stats(agent):
    yield From(agent.run_event.wait())
    logger.debug('starting get_nginx_stats')
    config = agent.config['nginx']
    logger.debug('get_nginx_stats config retrieved')
    db_config = config['database']
    yield From(agent.async_create_database(**db_config))
    logger.debug('getting event loop')
    loop = asyncio.get_event_loop()
    while agent.run_event.is_set():
        logger.debug('in while loop')
        try:
            yield From(asyncio.sleep(config['frequency']))
            url = config['url']

            res = yield From(loop.run_in_executor(
                None, requests.get, url))

            if res.status_code == 200:
                text = res.text

                logger.debug(text)

                status = text.strip().split('\n')
                conn = status[0].strip().split(': ')[-1]
                accepts, handled, num_req = status[2].strip().split(' ')
                reading, writing, waiting = re.split(r'[:\s]\s*',
                                                     status[-1].strip())[1::2]
                data = [{
                    'measurement': 'nginx_stats',
                    'tags': {
                        'hostname': config['host']
                    },
                    'fields': {
                        'connections': int(conn),
                        'total_accepts': int(accepts),
                        'total_handled': int(handled),
                        'total_requests': int(num_req),
                        'reading': int(reading),
                        'writing': int(writing),
                        'waiting': int(waiting)
                    }
                }]
                logger.debug('nginx data: {}'.format(data))
                yield From(agent.async_push(data, db_config['name']))
            else:
                logger.warning('cannot get nginx stats: status={}'
                               .format(res.status_code))
        except:
            logger.exception('cannot get nginx stats')
    logger.info('get_nginx_status terminated')
