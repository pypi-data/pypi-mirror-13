#!/bin/env python3
# -*- coding: utf-8 -*-

'''
Created on 23/11/2014

@author: rand huso

This module implements the MPI Inversion of Control framework.

MI_MachineInfo class contains information about the current node on which the application runs, and is sent automatically to Rank0.

_MI_PrefixMessage class is used internally by the framework, and is not intended for use by anyone else.

mpi_ioc class is the simplistic framework itself.
There is currently a presentation on github.com under my rchuso account in the mpi_ioc project that describes the use of this framework.
There is also a demonstration application that uses this framework and a PyQt UI to demonstrate the similarities between the two.

The C code (proprietary) version of this I made back in mid 2009 has several additional features that aren't necessary to demonstrate
how UI events and incoming MPI messages should be treated similarly.
'''

from mpi4py import MPI
import psutil
import socket

class MI_MachineInfo(object):
    '''
    This class provides information about the CPU where this instance of the application is running in an MPI environment.
    As with all messages sent between nodes, it contains a _tagNumber_.
    Currently only getting the machine name and the total memory.
    '''

    tagNumber = 20141123

    def __init__(self):
        self.hostname = socket.gethostbyaddr(socket.gethostname())[0]  # or use Get_processor_name()
        self.memory = psutil.phymem_usage()[0]
    def getNodeName(self) -> str: return self.hostname
    def getMemory(self) -> str: return self.memory

class _MI_PrefixMessage(object):
    '''
    This class is for internal use only.
    This is the control or prefix message sent ahead of a message going from one node to another.
    It's also used to convey a simple _Notice_ message when no other message is following.
    '''

    tagNumber = 20141122

    def __init__(self, sourceRank: int, nextTagNumber: int, commandNumber: int=1):
        self.sourceRank = sourceRank
        self.nextTagNumber = nextTagNumber
        self.commandNumber = commandNumber

class mpi_ioc(object):
    '''
    This class is the framework that controls the sending and receiving of messages in an MPI execution environment.

    Typical use:
    mi = mpi_ioc( None, infoRecipientMethod )
    mi.register( MyCommClass1, methodToProcessCommClass1 )
    mi.register( MyCommClass2, methodToProcessCommClass2 )
    mi.register( MyCommClass3, methodToProcessCommClass3 )
    ...
    mi.start()

    Once started, the framework on each node will gather the capabilities of the CPU and send this information to Rank 0 (the 'control node').
    When any message is received by any node (including the capabilities message) the registered method is invoked and given the number of the
    node that sent the message and the received message.
    When a message is received, the application on that node may take the opportunity to send message(s) to other node(s).
    The control node (Rank 0) will end the process by sending a request to terminate (the 'stop' method).
    '''

    def __init__(self, startupMethodRank0=None, machineInfoRecipientRank0=None):
        '''
        The startupMethodRank0 is your method to be invoked when the framework is started.
        The machineInfoRecipientRank0 is your method to be invoked when the capabilities message (MI_MachineInfo) is received from any node.
        One of these methods should be supplied - leaving both None will be very uneventful.
        Both of these functions will be invoked on the control node only, and not on other nodes. An alternative would be to broadcast
        the capabilities so everyone can have this information.
        '''

        self.startupMethodRank0 = startupMethodRank0
        if machineInfoRecipientRank0 is not None:
            self.register(MI_MachineInfo, self.machineInfoRecipientRank0)
        self.machineInfoRecipientRank0 = machineInfoRecipientRank0
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()
        self.iocLoop = True
        self.nextNoticeNumber = -999 # just an arbitrary negative number to keep the notices in a different set from other messages
        self.messageNumberByClass = {}
        self.messageCallbackByTag = {}
        self.noticeLookupByNumber = {}
        self.noticeLookupByName = {}
        self.noticeCallbackMethodByNumber = {}

    def getRank(self) -> int: return self.rank

    def getSize(self) -> int: return self.size

    def isControl(self) -> bool: return 0 == self.getRank()

    def register(self, callbackItem, callbackMethod, tagNumber: int=None) -> None:
        '''
        Register callback methods (callbackMethod) to be invoked when objects of the callbackItem are received.

        The framework will invoke the 'callbackMethod' when objects of the 'callbackItem' are received.
        If the 'callbackItem' is a string, there is no following object, and the method will be invoked with fewer arguments.

        Example:
        mi.register( MyCommClass1, methodToProcessCommClass1 ) # registers full message
        mi.register( 'Message', methodToProcessCommClass2 ) # registers notice

        When the framework receives an object of type 'MyCommClass1', it will invoke the registered method 'methodToProcessCommClass1' with
        the arguments '( sendingNodeNumber, receivedObject )'.
        When the framework receives a message of type 'Message', it will invoke the registered method 'methodToProcessCommClass2' with the
        single argument '( sendingNodeNumber )'.

        NOTE:
        All nodes sending and receiving full messages (not simple Notices) must have already registered the 'callbackItem' classes.
        These may be registered during the execution at any time - and all such objects must contain the requisite 'tagNumber'.
        All nodes must have already registered Notices (string Notices and their corresponding methods).
        It's best to register all these before starting the framework - as there could be some confusion when Notices are created
        on some nodes and not on others where other Notices are created - confusing the layer. An alternative to this is to supply
        a 'tagNumber' separately.
        '''

        if isinstance(callbackItem, str):
            if tagNumber is not None:
                msgTagNumber = tagNumber
            else:
                self.nextNoticeNumber -= 1
                msgTagNumber = self.nextNoticeNumber
            self.noticeLookupByNumber[msgTagNumber] = callbackItem
            self.noticeLookupByName[callbackItem] = msgTagNumber
            self.noticeCallbackMethodByNumber[msgTagNumber] = callbackMethod
        else:
            if tagNumber is not None:
                msgTagNumber = tagNumber
            else:
                msgTagNumber = callbackItem.tagNumber
            self.messageNumberByClass[callbackItem.__name__] = msgTagNumber
            self.messageCallbackByTag[msgTagNumber] = callbackMethod

    def bcastMessage(self, txMessage) -> None:
        ''' Sends the message to all the other nodes (currently using 'sendMessage' and not the comm.broadcast method). '''
        for nodeNumber in range(self.size):
            if self.rank != nodeNumber:
                self.sendMessage(nodeNumber, txMessage)

    def sendMessage(self, txNode, txMessage) -> None:
        ''' Sends the message (object or string) to the specified node. '''
        try:
            if isinstance(txMessage, str):
                txMessageNumber = self.noticeLookupByName[txMessage]
                prefixMessage = _MI_PrefixMessage(self.rank, 1, txMessageNumber)
                self.comm.send(prefixMessage, dest=txNode, tag=_MI_PrefixMessage.tagNumber)
            else:
                txMessageNumber = self.messageNumberByClass[txMessage.__class__.__name__]
                prefixMessage = _MI_PrefixMessage(self.rank, txMessageNumber)
                self.comm.send(prefixMessage, dest=txNode, tag=_MI_PrefixMessage.tagNumber)
                self.comm.send(txMessage, dest=txNode, tag=txMessageNumber)
        except KeyError as k:
            print('[%d] EXCEPTION -- Message [%s] problem.\n' % (self.rank, txMessage.__class__.__name__))
            raise k

    def start(self) -> None:
        '''
        Starts the framework and takes control of the execution until the 'stop' method is invoked.

        The registered 'startupMethodRank0' (if any) will be started first.
        The machine information will be gathered on every node and sent to Rank0 and given to the registered 'machineInfoRecipientRank0' method.
        '''
        if 0 == self.rank:
            if self.startupMethodRank0 is not None:
                self.startupMethodRank0()
        else:
            if self.machineInfoRecipientRank0 is not None:
                machineInfo = MI_MachineInfo()
                self.sendMessage(machineInfo, 0)
        while self.iocLoop:
            otherMess = self.comm.recv(source=-1, tag=_MI_PrefixMessage.tagNumber)
            if 0 == otherMess.commandNumber:
                self.iocLoop = False
            elif otherMess.commandNumber in self.noticeLookupByNumber.keys():
                try:
                    self.noticeCallbackMethodByNumber[otherMess.commandNumber](otherMess.sourceRank)
                except KeyError as k:
                    print('[%d] EXCEPTION -- mpi_ioc::invokeRegisteredMethod no registered commandNumber[%d]' % (self.rank, otherMess.commandNumber))
                    raise k
            else:
                fullMess = self.comm.recv(source=otherMess.sourceRank, tag=otherMess.nextTagNumber)
                try:
                    self.messageCallbackByTag[otherMess.nextTagNumber](otherMess.sourceRank, fullMess)
                except KeyError as k:
                    print('[%d] EXCEPTION -- mpi_ioc::invokeRegisteredMethod no registered tagNumber[%d]' % (self.rank, otherMess.nextTagNumber))
                    raise k
        return

    def stop(self) -> None:
        ''' Stops the main loop and returns control to the application. '''
        if 0 == self.rank and self.iocLoop:
            self.iocLoop = False
            message = _MI_PrefixMessage(0, 0, 0)
            for destinationRank in range(0, self.size):
                self.comm.send(message, dest=destinationRank, tag=_MI_PrefixMessage.tagNumber)
