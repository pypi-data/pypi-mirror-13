# -*- coding: utf-8 -*-
"""
Брокер. Позволяет посылать команды от сервера дочерним процессам.
"""
from openre.agent.decorators import daemonize
from openre.agent.helpers import daemon_stop
import logging
import signal
from openre.agent.args import parse_args
from openre.agent.broker.args import parser
from openre.agent.broker.broker import Agent

def run():
    args = parse_args(parser)
    def sigterm(signum, frame):
        signum_to_str = dict(
            (k, v) for v, k in reversed(sorted(signal.__dict__.items()))
            if v.startswith('SIG') and not v.startswith('SIG_')
        )
        logging.debug(
            'Got signal.%s. Clean and exit.',
            signum_to_str.get(signum, signum)
        )
        exit(0)

    @daemonize(
        args.pid_file,
        signal_map={
            signal.SIGTERM: sigterm,
            signal.SIGINT: sigterm,
        },
    )
    def start():
        """
        Запуск серера
        """
        logging.info('Start OpenRE.Agent broker')
        agent = Agent(vars(args))
        agent.run()

    def stop():
        """
        Остановка серера
        """
        logging.info('Stop OpenRE.Agent broker')
        daemon_stop(args.pid_file)

    if args.action == 'start':
        start()
    elif args.action == 'stop':
        stop()
    elif args.action == 'restart':
        stop()
        start()

