#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import argh
import requests

from time import time
from crate.client import connect
from concurrent.futures import ThreadPoolExecutor, wait


executor = ThreadPoolExecutor(20)


class Result:
    def __init__(self,
                 version_info,
                 statement,
                 started,
                 ended,
                 repeats,
                 client_runtimes,
                 server_runtimes):
        self.version_info = version_info
        self.statement = statement
        # need ts in ms in crate
        self.started = int(started * 1000)
        self.ended = int(ended * 1000)
        self.repeats = repeats
        self.client_runtimes = client_runtimes
        self.server_runtimes = server_runtimes

        runtimes = self.server_runtimes
        avg = sum(runtimes) / float(len(runtimes))
        self.runtime_stats = {
            'avg': round(avg, 3),
            'min': round(min(runtimes), 3),
            'max': round(max(runtimes), 3)
        }

    def __str__(self):
        return json.dumps(self.__dict__)


class QueryRunner:
    def __init__(self, stmt, repeats, hosts):
        self.stmt = stmt
        self.hosts = hosts
        self.repeats = repeats
        self.conn = connect(hosts)

    def warmup(self, num_warmup):
        futures = []
        for i in range(num_warmup):
            c = self.conn.cursor()
            stmt = self.stmt
            futures.append(executor.submit(lambda: c.execute(stmt)))
        wait(futures)

    def run(self):
        version_info = self.__get_version_info(self.conn.client.active_servers[0])

        started = time()
        client_runtimes = []
        server_runtimes = []
        cursor = self.conn.cursor()
        for i in range(self.repeats):
            start = time()
            cursor.execute(self.stmt)
            client_runtimes.append(round(time() - start, 3))
            server_runtimes.append(cursor.duration / 1000.)
        ended = time()

        return Result(
            statement=self.stmt,
            version_info=version_info,
            started=started,
            ended=ended,
            repeats=self.repeats,
            client_runtimes=client_runtimes,
            server_runtimes=server_runtimes
        )

    def __get_version_info(self, server):
        data = requests.get(server).json()
        return {
            'number': data['version']['number'],
            'hash': data['version']['build_hash']
        }


@argh.arg('hosts', type=str, nargs='+')
def timeit(stmt, hosts, warmup=30, repeat=30):
    """ runs the given statement a number of times and returns the runtime stats
    """
    runner = QueryRunner(stmt, repeat, hosts)
    runner.warmup(warmup)
    result = runner.run()
    return result


def main():
    argh.dispatch_command(timeit)


if __name__ == '__main__':
    main()
