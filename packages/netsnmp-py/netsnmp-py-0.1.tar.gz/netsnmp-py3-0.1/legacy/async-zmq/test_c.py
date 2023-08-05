#!/usr/bin/python3

from netsnmp.api import get_async as snmpget_async
#import cx_Oracle
import zmq
import redis, hiredis
import logging, logging.handlers
import queue, random, sys, time
import multiprocessing as mp

# command name
cmdname = sys.argv[0]

# configure short loglevel names
logging._levelToName = {
    logging.CRITICAL: 'CRI',
    logging.ERROR:    'ERR',
    logging.WARNING:  'WAR',
    logging.INFO:     'INF',
    logging.DEBUG:    'DBG',
    logging.NOTSET:   'NOSET',
}

# DB definitions
DB = {
    "apportal": {
        'server': 'host',
        'port'  : '1521',
        'name'  : 'name',
        'user'  : 'user',
        'pass'  : 'pass'
    },
}

### Global definitions
#BUG: udp sendto failures when 49116 > MAX_WORKERS*MAX_PER_WORKER > 49112
# limitation lies somewhere between 49112 and 49116(??) - getting EPERM (1)... kernel dropping?
#http://comments.gmane.org/gmane.comp.security.firewalls.netfilter.devel/29993
# 8 * 4096 = 32768 max requests at any given time
MAX_WORKERS=2
MAX_PER_WORKER=4096

# Number of ZMQ PULL processes to spawn
ZMQ_PROCESSORS = 4
zmq_processors = []

# Time to pause for ZMQ initialization (Seconds)
ZMQ_PAUSE=0.1

# ZMQ High water mark
ZMQ_HWM=10000000

# ZMQ endpoints
ZMQ_IN  = "ipc:///tmp/%s_in" % cmdname
ZMQ_OUT = "ipc:///tmp/%s_out" % cmdname

# ZeroMQ Message Frame pointers ([OP, HOST, OIDS..])
OP=0
HOST=1
OIDS=2

## SNMP

SNMP_RETRIES=1
# SNMP timeout is in milliseconds
SNMP_TIMEOUT=250
SNMP_TIMEOUT_DELTA=MAX_WORKERS

# Messaging Intake/Processing
def ZMQProcessor(success, timeout):
    """
    Intake work via ZeroMQ socket and queue for processing after _sentinel is signaled
    """

    # Per-processor queue
    q = queue.Queue()

    # Processor ZMQ PULL socket
    incoming = zmq.Context().socket(zmq.PULL)
    incoming.setsockopt(zmq.RCVHWM, ZMQ_HWM)
    incoming.connect(ZMQ_OUT)

    # redis pipeline
    #_redis = redis.Redis(host='127.0.0.1').pipeline()

    log.debug('Starting up...')

    # Pull via ZMQ and Queue
    while True:
        response = incoming.recv_multipart()
        if response[0] == b'_sentinel':
            log.debug('Shutting down ZMQ_PULL socket...')
            incoming.close()
            break
        q.put_nowait(response)

    # Queue processing
    qsize = q.qsize()
    log.debug('Processing %d responses...' % (qsize,))
    start = time.perf_counter()
    i=0
    while not q.empty():
        response = [frame.decode() for frame in q.get()]
        if response[OP] == '1':
            with success.get_lock():
                success.value+=1
            # Parse OIDs
            vars = [var.split('=', maxsplit=1) for var in response[OIDS:]]
            vars = {oid: value for (oid, value) in vars}
            try: 
                #_redis.hmset(response[HOST] if not response[HOST].startswith("udp6") else response[HOST].replace("udp6:[", "").replace("]", ""),
                #             vars)
                i+=1
            except redis.exceptions.RedisError as e:
                log.debug('redis exception: %s' % (str(e).strip()))
                continue
            # Flush redis pipeline periodically
            if i > 4095:
                #_redis.execute()
                i=0
        elif response[OP] == '2':
            with timeout.get_lock():
                timeout.value+=1
    #_redis.execute()
    end = time.perf_counter()
    elapsed = end-start
    log.info('Finished processing %d responses in %.3fs' % (qsize, elapsed))

# Messaging Pipeline
def ZMQStreamer(running):
    """
    Proxy ZeroMQ via pipeline (zmq.STREAMER)
    """

    incoming = zmq.Context().socket(zmq.PULL)
    incoming.setsockopt(zmq.RCVHWM, ZMQ_HWM*MAX_WORKERS)
    incoming.bind(ZMQ_IN)

    outgoing = zmq.Context().socket(zmq.PUSH)
    outgoing.setsockopt(zmq.SNDHWM, ZMQ_HWM*ZMQ_PROCESSORS)
    outgoing.bind(ZMQ_OUT)

    log.debug('Starting up...')
    with running.get_lock():
        running.value = 1
    zmq.device(zmq.STREAMER, incoming, outgoing)

if __name__ == '__main__':

    # example list for get_async
    #hosts = [
    #('HOST_OR_IP', 'community', ['1.3.6.1.2.1.1.1.0', '1.3.6.1.2.1.1.3.0']),
    #('udp6:[IP]:161', 'community', ['1.3.6.1.2.1.1.1.0'])
    #]

    db = DB['apportal']
    #dbh = cx_Oracle.connect('%s/%s@%s/%s' % (db['user'], db['pass'], db['server'], db['name']))

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s.%(msecs)03dZ [%(processName)s/%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%dT%H:%M:%S')
    log = logging.getLogger(__name__)

    _log_queue = queue.Queue()
    log_async  = logging.handlers.QueueHandler(_log_queue)
    log_queue  = logging.handlers.QueueListener(_log_queue, *log.handlers)

    log_queue.start()

    # Overwrite handlers to only utilize QueueHandler()
    log.handlers = [log_async,]

    query = '''\
SELECT \
IP \
FROM DB WHERE \
IP IS NOT NULL AND \
IP NOT IN ('null', 'NOSUCHOBJECT') AND \
LAST_POLL >= SYSDATE - INTERVAL '5' DAY AND \
ROWNUM <= 1000000\
'''
    community='public'

    #select = dbh.cursor()
    #select.arraysize = 4096
    
    _oids = {
            'ap.model': '1.3.6.1.2.1.1.1.0',
            'ap.serial_number': '1.3.6.1.4.1.15768.3.1.1.11.2.0',
            'ap.tunnel_peer1': '1.3.6.1.4.1.15768.5.1.1.2.1.5.1.1',
            'ap.tunnel_peer2': '1.3.6.1.4.1.15768.5.1.1.2.1.9.1.1',
            'ap.swbank_active': '1.3.6.1.4.1.15768.3.1.1.3.1.0',
            'ap.swbank_next': '1.3.6.1.4.1.15768.3.1.1.3.2.0',
            'ap.software_a': '1.3.6.1.4.1.15768.3.1.1.3.5.1.2.1',
            'ap.software_b': '1.3.6.1.4.1.15768.3.1.1.3.5.1.2.2',
            'ap.tunnel_status': '1.3.6.1.4.1.15768.5.1.1.3.1.1.1.1',
            'ap.vpn_label': '1.3.6.1.4.1.15768.5.1.1.2.1.2.1.1',
            'ap.tunnel1_active': '1.3.6.1.4.1.15768.5.1.1.3.1.3.1.1',
            'ap.tunnel2_active': '1.3.6.1.4.1.15768.5.1.1.3.1.4.1.1',
            'ap.radius_server1': '1.3.6.1.2.1.67.1.2.1.1.3.1.2.1',
            'ap.radius_server2': '1.3.6.1.2.1.67.1.2.1.1.3.1.2.2',
#            'cm.software': '1.3.6.1.4.1.15768.6.4.1.1.1.5.1',
    }
    oids = {
            'ap.model': '1.3.6.1.2.1.1.1.0',
            'ap.mode' : '1.3.6.1.2.1.1.3.0',
    }

    hosts = []
    oidl  = list(oids.values())

    # Absolute start timer
    _start = time.time()
    # Step timer
    start = time.perf_counter()
    # append host tuple with inline ipv6 logic
    [hosts.append(
        (host, community, oidl)
    ) for host in ('archt01', 'archt02', 'archt03', 'archt04', 'archt05', 'archt06')]
    #select.close()
    #dbh.close()
    total = len(hosts)
    end = time.perf_counter()
    log.info('got %d hosts from DB in %.3fms' % (total, (end-start)*1000))

    try:
        ## Global multiprocessing-safe counters
        success = mp.Value('i', 0)
        timeout = mp.Value('i', 0)
        ## ZMQStreamer switch (set to 1 after successful initialization)
        zmq_streamer_running = mp.Value('i', 0)


        # Start ZeroMQ Streamer
        zmq_streamer = mp.Process(target=ZMQStreamer,
                                   args=(zmq_streamer_running,),
                                   name='ZMQStreamer',
                                   daemon=True)

        zmq_streamer.start()

        # Let the ZMQ sockets start up
        time.sleep(ZMQ_PAUSE)
        if not zmq_streamer_running.value == 1:
            raise RuntimeError("ZMQStreamer failed to initialize")

        # Spin up ZeroMQ Processors
        for i in range(ZMQ_PROCESSORS):
            zmq_processors.append(
                mp.Process(target=ZMQProcessor,
                            args=(success, timeout),
                            name='ZMQProc-%03d' % (i+1),
                            daemon=True)
            )
            zmq_processors[-1].start()

        time.sleep(ZMQ_PAUSE)

        # List of multiprocessing.Process() objects (worker processes)
        workers = []
        
        # Worker/process id iterator
        p=0
        # Host index range iterator
        i=0
        # While any hosts or workers exist
        start = time.perf_counter()
        while hosts or workers:
            pids = []
            if hosts and len(workers) < MAX_WORKERS:
                _timeout = SNMP_TIMEOUT+random.randint(p%2, SNMP_TIMEOUT_DELTA)
                log.debug('Defining process for range %d:%d (%dms)' % (i, i+MAX_PER_WORKER, _timeout))

                # Define process(es) which call get_async C function
                # get_async([(str hostname, str community, [str oid,..])..], int timeout_ms, int retries, int ZMQ_HWM, str ZMQ_IN)
                workers.append(
                    mp.Process(target=snmpget_async,
                                args=(hosts[:MAX_PER_WORKER], 
                                      _timeout,
                                      SNMP_RETRIES, 
                                      ZMQ_HWM, 
                                      ZMQ_IN), daemon=True)
                )

                del hosts[:MAX_PER_WORKER]
                i+=MAX_PER_WORKER
                workers[-1].start()
                if len(workers) < MAX_WORKERS:
                    p+=1
                    continue
                else:
                    p=0

            [pids.append(proc.pid) for proc in workers]
            log.debug('Process PIDs: %s' % pids)

            # Continually monitor progress and re-loop when all workers are finished (unless force_reloop)
            while workers:
                force_reloop = False
                for proc in workers:
                    if proc.is_alive():
                        continue
                    else:
                        workers.remove(proc)
                        if proc.exitcode == 0:
                            log.info('%d - Process finished' % proc.pid)
                        else:
                            log.error('%d - Process failed (%d)' % (proc.pid, proc.exitcode))
                        # if processes take variable amount of time, might want to break and loop to start a new process
                        # this ensures MAX_WORKERS processes active at all times
                        force_reloop = True
                        break
                if force_reloop:
                    break

        # Finally, raise successful completion
        raise SystemExit

    except RuntimeError as e:
        log.critical("%s", e)

    except SystemExit:
        end = time.perf_counter()
        elapsed = end-start
        log.debug('Polling completed in %.3fs' % elapsed)

        # Signal end to ZMQProcessor(s)
        zmq_sentinel = zmq.Context().socket(zmq.PUSH)
        zmq_sentinel.connect(ZMQ_IN)
        for _ in range(ZMQ_PROCESSORS):
            zmq_sentinel.send(b'_sentinel')

        time.sleep(ZMQ_PAUSE)

        zmq_sentinel.close()

        # Wait for ZMQProcessor(s) to complete
        while zmq_processors:
            for zmq_processor in zmq_processors:
                zmq_processor.join()
                zmq_processors.remove(zmq_processor)

        log.info('from %d total hosts got %d timeouts (%.1f%%)' % (total, timeout.value, ((timeout.value/total)*100)))
        log.info('got %d oid responses from %d hosts' % ((success.value*len(oids)), success.value))
        log.info('lost %d hosts' % (total-(success.value+timeout.value)))
        log.info('%.2f oids/sec' % ((success.value*len(oidl))/elapsed))
        log.info('%.2f reqs/sec' % ((success.value+timeout.value)/elapsed))

        _end = time.time()
        _elapsed = _end-_start
        log.info('total time taken %.3fs' % _elapsed)

    finally:
        # Ensure logging is flushed
        log_queue.stop()
