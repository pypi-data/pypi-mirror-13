# Copyright (c) 2015 Davide Gessa
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import requests
import binascii
import json
import sys
import logging
import time
import signal
from threading import Thread
from threading import Lock
from colorlog import ColoredFormatter
from libcontractvm import Wallet
from libcontractvm import ConsensusManager
from . import Log

logger = logging.getLogger('libcontractvm')


class DappManager:
	def __init__ (self, consensusmgr, wallet):
		self.consensusManager = consensusmgr
		self.wallet = wallet


	def produceTransaction (self, method, arguments, bmethod = 'broadcast'):
		logger.info ('Producing transaction: %s %s', method, str (arguments))

		while True:
			#print ('search for best')
			best = self.consensusManager.getBestNode()
			#print (best)
			# Create the transaction
			res = self.consensusManager.jsonCall (best, method, arguments)
			#print (res, best)
			txhash = self.wallet.createTransaction ([res['outscript']], res['fee'])

			if txhash == None:
				logger.error ('Failed to create transaction, retrying in few seconds...')
				time.sleep (10)
				continue

			# Broadcast the transaction
			cid = self.consensusManager.jsonCall (best, bmethod, [txhash, res['tempid']])

			if cid == None:
				logger.error ('Broadcast failed')
				time.sleep (10)
				continue

			cid = cid['txid']

			if cid != None:
				logger.info ('Broadcasting transaction: %s', cid)
				return cid
			else:
				logger.error ('Failed to produce transaction, retrying in 10 seconds')
				time.sleep (10)
