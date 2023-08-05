import aiohttp
import asyncio
import logging
import re


logger = logging.getLogger(__name__)


@asyncio.coroutine
def get_nginx_stats(agent):
    yield from agent.run_event.wait()
    config = agent.config['nginx']
    db_config = config['database']
    yield from agent.async_create_database(**db_config)

    while agent.run_event.is_set():
        try:
            yield from asyncio.sleep(config['frequency'])
            url = config['url']

            logger.debug('obtaining status from {}'.format(config['host']))

            res = yield from aiohttp.get(url)
            if res.status == 200:
                text = yield from res.text()

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
                yield from agent.async_push(data, db_config['name'])
            else:
                logger.warning('cannot get nginx stats: status={}'
                               .format(res.status))
        except:
            logger.exception('cannot get nginx stats')
    logger.info('get_nginx_status terminated')
