from functools import wraps
import re
import time


def profile(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        start_time = time.time()
        ret = fn(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(blue('Execution time %.3f' % (elapsed_time)))
        return ret
    return decorated


def ab(url, requests=10000, concurrency=50, timelimit=0, log=True, verbose=False):
    """
    Example:
    Time taken for tests:   0.008 seconds
    Complete requests:      1
    Failed requests:        0
    Non-2xx responses:      1
    Requests per second:    129.82 [#/sec] (mean)
    """
    log_level = 2 if verbose else 0
    if timelimit:
        results = env.run('ab -n %s -c %s -t %s -v %s %s' % (requests, concurrency, timelimit, log_level, url), capture=True)
    else:
        results = env.run('ab -n %s -c %s -v %s %s' % (requests, concurrency, log_level, url), capture=True)
    r = results.replace('\n', 'newline')
    reqs_per_second = re.search(r'.*Requests per second:\s*(\d+[.]?\d*)', r).groups(0)[0]
    elapsed_time = re.search(r'.*Time taken for tests:\s*(\d+[.]?\d*)', r).groups(0)[0]
    complete_requests = int(re.search(r'.*Complete requests:\s*(\d+)', r).groups(0)[0])
    failed_requests = int(re.search(r'.*Failed requests:\s*(\d+)', r).groups(0)[0])
    try:
        non_2xx_requests = int(re.search(r'.*Non-2xx responses:\s*(\d+)', r).groups(0)[0])
    except (AttributeError, IndexError, ValueError):
        non_2xx_requests = 0
    if log:
        if failed_requests > 0 or non_2xx_requests > 0:
            print(red('Error'))
            print(red('Failed: %s' % (failed_requests)))
            print(red('non 2xx: %s' % (non_2xx_requests)))
        else:
            print(green('Success'))
        print(blue('%s reqs/s' % reqs_per_second))
    return dict(reqs_per_second=reqs_per_second, elapsed_time=elapsed_time,
        complete_requests=complete_requests, failed_requests=failed_requests,
        non_2xx_requests=non_2xx_requests)


def weighttp(url, requests=10000, concurrency=50, threads=5, log=True):
    def format_weighttp_result(results, log=True):
        '''
        Example:
        finished in 1 sec, 665 millisec and 7 microsec, 6005 req/s, 1225 kbyte/s
        requests: 10000 total, 10000 started, 10000 done, 0 succeeded, 10000 failed, 0 errored
        status codes: 10000 2xx, 0 3xx, 0 4xx, 0 5xx
        traffic: 2090000 bytes total, 2090000 bytes http, 0 bytes data
        '''
        def parse_summary_line(line):
            'finished in 1 sec, 665 millisec and 7 microsec, 6005 req/s, 1225 kbyte/s'
            reqs_per_seconds = re.search(r'(\d+[.]?\d*) req/s', line).groups(0)[0]
            kbs_per_seconds = re.search(r'(\d+[.]?\d*) kbyte/s', line).groups(0)[0]
            elapsed_time = re.sub(r'microsec.+', 'microsec', line.replace('finished in ', ''))
            return elapsed_time, int(reqs_per_seconds), int(kbs_per_seconds)

        def parse_requests_line(line):
            'requests: 10000 total, 10000 started, 10000 done, 0 succeeded, 10000 failed, 0 errored'
            reqs = dict(total=0, started=0, done=0, succeeded=0, failed=0, errored=0)
            tokens = map(str.strip, line.replace('requests: ', '').split(','))
            for t in tokens:
                value, req = t.split(' ')
                reqs[req] = int(value)
            return reqs

        def parse_status_code_line(line):
            'status codes: 10000 2xx, 0 3xx, 0 4xx, 0 5xx'
            codes = dict(_2xx=0, _3xx=0, _4xx=0, _5xx=0)
            tokens = map(str.strip, line.replace('status codes: ', '').split(','))
            for t in tokens:
                value, code = t.split(' ')
                codes['_' + code] = int(value)
            return codes

        results = results.replace('\n', 'newline')
        results = re.sub(r'^(.*)finished', 'finished', results, flags=re.M).strip()
        lines = results.split('newline')
        elapsed_time, reqs_per_second, kbs_per_second = parse_summary_line(lines[0])
        reqs = parse_requests_line(lines[1])
        codes = parse_status_code_line(lines[2])

        if log:
            success = reqs['failed'] == 0 and reqs['errored'] == 0 and reqs['total'] == reqs['done'] and codes['_4xx'] == 0 and codes['_5xx'] == 0
            if success:
                m = green('Success')
                s = '2xx: %s 3xx: %s' % (codes['_2xx'], codes['_3xx']) + ' 4xx: %s 5xx: %s' % (codes['_4xx'], codes['_5xx'])
                e = 'Failed: %s Errored: %s' % (reqs['failed'], reqs['errored'])
            else:
                m = red('Error')
                s = '2xx: %s 3xx: %s' % (codes['_2xx'], codes['_3xx']) + red(' 4xx: %s 5xx: %s' % (codes['_4xx'], codes['_5xx']))
                e = red('Failed: %s Errored: %s' % (reqs['failed'], reqs['errored']))
            n = 'Total: %s Started: %s Done: %s Succeeded: %s' % (reqs['total'], reqs['started'], reqs['done'], reqs['succeeded'])
            print(m + ' ' + s)
            print(n + ' ' + e)
            print(blue('%s reqs/s' % reqs_per_second))

        results = dict(elapsed_time=elapsed_time, reqs_per_second=reqs_per_second, kbs_per_second=kbs_per_second)
        results['requests'] = reqs
        results['status_codes'] = codes
        return results

    # http://adventuresincoding.com/2012/05/how-to-get-apachebenchab-to-work-on-mac-os-x-lion
    # install('Weighttp')
    results = env.run('weighttp -n %s -c %s -t %s -k %s' % (requests, concurrency, threads, url), capture=True)
    return format_weighttp_result(results, log=log)
