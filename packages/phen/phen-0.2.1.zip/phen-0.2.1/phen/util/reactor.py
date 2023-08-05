#!/usr/bin/env python
#-*- coding:utf-8 -*-

from threading import Thread
from twisted.python import log
from twisted.internet import reactor


class FilterLogs(log.PythonLoggingObserver):
    def emit(self, eventDict):
        if not eventDict['system'].startswith(("SSH", "twisted.conch")):
            log.PythonLoggingObserver.emit(self, eventDict)


FilterLogs(loggerName="twisted").start()


def run():
    rt = Thread(target=reactor.run, name="Async Reactor Thread",
                kwargs={"installSignalHandlers": 0})
    rt.setDaemon(True)
    rt.start()
    return rt


def stop():
    reactor.callFromThread(reactor.stop)
