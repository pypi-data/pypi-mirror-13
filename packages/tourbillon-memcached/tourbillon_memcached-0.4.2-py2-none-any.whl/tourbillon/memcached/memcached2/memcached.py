import logging

import trollius as asyncio
from trollius import From


logger = logging.getLogger(__name__)


STATS_FIELDS = {
    'connection_structures': int,
    'incr_misses': int,
    'conn_yields': int,
    'listen_disabled_num': int,
    'cas_misses': int,
    'rusage_system': float,
    'bytes': int,
    'delete_hits': int,
    'hash_bytes': int,
    'reserved_fds': int,
    'curr_items': int,
    'pointer_size': int,
    'cmd_flush': int,
    'cas_hits': int,
    'threads': int,
    'bytes_read': int,
    'evictions': int,
    'reclaimed': int,
    'curr_connections': int,
    'accepting_conns': int,
    'get_misses': int,
    'total_connections': int,
    'incr_hits': int,
    'cmd_touch': int,
    'decr_misses': int,
    'get_hits': int,
    'bytes_written': int,
    'rusage_user': float,
    'auth_cmds': int,
    'decr_hits': int,
    'hash_power_level': int,
    'hash_is_expanding': int,
    'cmd_set': int,
    'cas_badval': int,
    'cmd_get': int,
    'delete_misses': int,
    'limit_maxbytes': int,
    'touch_misses': int,
    'total_items': int,
    'evicted_unfetched': int,
    'touch_hits': int,
    'expired_unfetched': int,
    'auth_errors': int
}


@asyncio.coroutine
def get_memcached_stats(agent):
    yield From(agent.run_event.wait())
    config = agent.config['memcached']
    logger.info('starting "get_memcached_stats" task for "%s"',
                config['hostname'])
    db_config = config['database']
    yield From(agent.async_create_database(**db_config))
    memcached_host = config['hostname']
    memcached_port = config['port']
    while agent.run_event.is_set():
        yield From(asyncio.sleep(config['frequency']))
        try:
            logger.debug('open connection to memcached server')
            reader, writer = yield From(asyncio.open_connection(
                memcached_host, memcached_port))

            writer.write(bytes('stats\n'.encode('ascii')))
            logger.debug('command stats sent')
            results = []
            while True:
                buf = yield From(reader.read(1024))
                logger.debug('data read from socket')
                data = buf.decode()
                results.append(data)
                if data.endswith('END\r\n'):
                    logger.debug('data read finished')
                    break
            writer.close()
            results = ''.join(results).split('\r\n')[0:-2]
            points = [{
                'measurement': 'memcached_stats',
                'tags': {
                    'host': memcached_host,
                },
                'fields': {
                }
            }]
            logger.debug('parsing results')
            for line in results:
                stat, key, val = line.split(' ')
                if key in STATS_FIELDS:
                    points[0]['fields'][key] = STATS_FIELDS[key](val)
            logger.debug(points)
            yield From(agent.async_push(points, db_config['name']))
        except:
            logger.exception('cannot get the memcached stats')
    logger.info('get_memcached_stats terminated')
