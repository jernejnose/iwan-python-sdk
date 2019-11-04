import asyncio
import base64
import hashlib
import hmac
import json
import time

import websockets


# Utility functions #
def timestamp():
    return int(time.time() * 1000.0)


class ApiInstance:
    def __init__(self, api_key, secret_key, uri='wss://api.wanchain.org:8443/ws/v3/'):
        self.api_key = str(api_key)
        self.secret_key = str(secret_key)
        self.uri = str(uri)
        if self.uri[-1] != "/":
            self.uri += "/"
        self.endpoint = "{}{}".format(self.uri, self.api_key)

    # Utility methods #
    def _new_message(self, method, chain_type=None):
        if chain_type is not None:
            obj = {"jsonrpc": "2.0", "method": str(method), "params": {"chainType": chain_type}, "id": 1}
        else:
            obj = {"jsonrpc": "2.0", "method": str(method), "params": {}, "id": 1}
        return obj

    def _make_signature(self, message):
        json_message = bytes(json.dumps(message, separators=(',', ':')), 'utf-8')
        auth_code = hmac.new(bytes(self.secret_key, 'utf-8'), msg=json_message, digestmod=hashlib.sha256)
        return base64.b64encode(auth_code.digest()).decode()

    def _make_request(self, message):
        message['params']['timestamp'] = timestamp()
        message['params']['signature'] = self._make_signature(message)

        str_msg = json.dumps(message, separators=(',', ':'))
        print(str_msg)

        async def send():
            async with websockets.connect(self.endpoint) as websocket:
                await websocket.send(str_msg)
                return await websocket.recv()

        return asyncio.get_event_loop().run_until_complete(send())

    # Accounts methods #
    def get_balance(self, address, chain_type='WAN'):
        """
        Get balance for a single address.
        :param address: The account being queried.
        :param chain_type: The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getBalance", chain_type)
        message['params']['address'] = str(address)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_multi_balances(self, addresses, chain_type='WAN'):
        """
        Get balance for multiple Addresses in a single call.
        :param addresses: An array of addresses being queried.
        :param chain_type: The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getMultiBalances", chain_type)
        message['params']['address'] = addresses
        response = json.loads(self._make_request(message))
        return response['result']

    def get_nonce(self, address, chain_type='WAN'):
        """
        Get the nonce of an account.
        :param address: The account being queried.
        :param chain_type: The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getNonce", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_nonce_include_pending(self, address, chain_type='WAN'):
        """
        Get the pending nonce of an account.
        :param address: The account being queried.
        :param chain_type: The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getNonceIncludePending", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_utxo(self, address, minconf, maxconf, chain_type='BTC'):
        """
        Get the detail BTC UTXO info for BTC.
        :param address: The address array that you want to search.
        :param minconf: The min confirm number of BTC UTXO, usually 0.
        :param maxconf: The max confirm number of BTC UTXO, usually the confirmed blocks you want to wait for the utxo.
        :param chain_type: The chain being queried. Currently supports "BTC".
        :return:
        """
        message = self._new_message("getUTXO", chain_type)
        message['params']['address'] = address
        message['params']['minconf'] = minconf
        message['params']['maxconf'] = maxconf
        response = json.loads(self._make_request(message))
        return response['result']

    def import_address(self, address, chain_type='BTC'):
        """
        Send a import address command to BTC.
        :param address: The BTC account address you want to import to the node to scan transactions.
        :param chain_type: The chain being queried. Currently supports "BTC".
        :return:
        """
        message = self._new_message("importAddress", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    # Blocks #
    def get_block_by_hash(self, block_hash, chain_type='WAN'):
        """
        Get the block information about a block by block hash on certain chain.
        :param block_hash: The blockHash you want to search.
        :param chain_type: The chain being queried. Currently supports "WAN" or "ETH".
        :return:
        """
        message = self._new_message("getBlockByHash", chain_type)
        message['params']['blockNumber'] = block_hash
        response = json.loads(self._make_request(message))
        return response['result']

    def get_block_by_number(self, block_number, chain_type='WAN'):
        """
        Get the block information about a block by block number on certain chain.
        :param block_number:The blockNumber you want to search.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH".
        :return:
        """
        message = self._new_message("getBlockByNumber", chain_type)
        message['params']['blockNumber'] = block_number
        response = json.loads(self._make_request(message))
        return response['result']

    def get_block_number(self, chain_type='WAN'):
        """
        Get the current latest block number.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH" or "BTC".
        :return:
        """
        message = self._new_message("getBlockNumber", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_block_transaction_count(self, block_number=None, block_hash=None, chain_type='WAN'):
        """
        Get the number of transaction in a given block by blockNumber or blockhash on certain chain.
        :param block_number:The blockNumber you want to search.
        :param block_hash:The blockHash you want to search.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH".
        :return:
        """
        message = self._new_message("getBlockTransactionCount", chain_type)
        if block_number is not None:
            message['params']['blockNumber'] = block_number
        if block_hash is not None:
            message['params']['blockHash '] = block_hash
        response = json.loads(self._make_request(message))
        return response['result']

    # Contracts #
    def call_sc_func(self, sc_addr, name, args, abi, chain_type='WAN'):
        """
        Call the specific public function of one contract on certain chain.
        :param sc_addr:The token address for the certain token.
        :param name:The name of the specific contract public function.
        :param args:The parameters array a of the specific contract public function.
        :param abi:The abi of the specific contract.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH".
        :return:
        """
        message = self._new_message("callScFunc", chain_type)
        message['params']['scAddr'] = sc_addr
        message['params']['name'] = name
        message['params']['args'] = args
        message['params']['abi'] = abi
        response = json.loads(self._make_request(message))
        return response['result']

    def get_sc_map(self, sc_addr, name, key, abi, chain_type='WAN'):
        """
        Get the specific public map value of one contract on certain chain.
        :param sc_addr:The token address for the certain token.
        :param name:The name of the specific contract public map.
        :param key:The key of parameter of the specific contract public map.
        :param abi:The abi of the specific contract.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH".
        :return:
        """
        message = self._new_message("getScMap", chain_type)
        message['params']['scAddr'] = sc_addr
        message['params']['name'] = name
        message['params']['key'] = key
        message['params']['abi'] = abi
        response = json.loads(self._make_request(message))
        return response['result']

    def get_sc_var(self, sc_addr, name, abi, chain_type='WAN'):
        """
        Get the specific public parameter value of one contract on certain chain.
        :param sc_addr:The token address for the certain token.
        :param name:The name of the specific contract public map.
        :param abi:The abi of the specific contract.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH".
        :return:
        """
        message = self._new_message("getScVar", chain_type)
        message['params']['scAddr'] = sc_addr
        message['params']['name'] = name
        message['params']['abi'] = abi
        response = json.loads(self._make_request(message))
        return response['result']

    # CrossChain #
    def get_coin_2_wan_ratio(self, cross_chain='ETH'):
        """
        Coin exchange ratio,such as 1 ETH to 880 WANs in ICO period, the precision is 10000, the ratio is 880*precision = 880,0000. The ratio would be changed according to the market value ratio periodically.
        :param cross_chain:The cross-chain native coin name that you want to search, should be "ETH" or "BTC".
        :return:
        """
        message = self._new_message("getCoin2WanRatio")
        message['params']['crossChain'] = cross_chain
        response = json.loads(self._make_request(message))
        return response['result']

    def get_reg_tokens(self, cross_chain='ETH'):
        """
        Get the information of tokens which are supported for cross-chain ability.
        :param cross_chain: The cross-chain name that you want to search, should be "ETH".
        :return:
        """
        message = self._new_message("getRegTokens")
        message['params']['crossChain'] = cross_chain
        response = json.loads(self._make_request(message))
        return response['result']

    def get_storeman_groups(self, cross_chain='ETH'):
        """
        Get the detailed cross-chain storemanGroup info for one cross-chain native coin, like the quota, etc.
        :param cross_chain:The cross-chain name that you want to search, should be "ETH" or "BTC".
        :return:
        """
        message = self._new_message("getStoremanGroups")
        message['params']['crossChain'] = cross_chain
        response = json.loads(self._make_request(message))
        return response['result']

    def get_token_2_wan_ratio(self, token_sc_address, cross_chain='ETH'):
        """
        Token exchange ratio,such as 1 token to 880 WANs, the precision is 10000, the ratio is 880*precision = 880,0000. The ratio would be changed accoring to the market value ratio periodically.
        :param token_sc_address:The token contract address for the specified token.
        :param cross_chain:The cross-chain name that you want to search, should be "ETH".
        :return:
        """
        message = self._new_message("getToken2WanRatio")
        message['params']['crossChain'] = cross_chain
        message['params']['tokenScAddr'] = token_sc_address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_token_storeman_groups(self, token_sc_address, cross_chain='ETH'):
        message = self._new_message("getTokenStoremanGroups")
        message['params']['crossChain'] = cross_chain
        message['params']['tokenScAddr'] = token_sc_address
        response = json.loads(self._make_request(message))
        return response['result']

    # Events #
    def get_sc_event(self, address, topics, from_block=None, to_block=None, chain_type='WAN'):
        """
        Get smart contract event log via topics.
        :param address:The contract address.
        :param topics:An array of string values which must each appear in the log entries. The order is important, if you want to leave topics out use null, e.g. [null, '0x00...'].
        :param from_block:The number of the earliest block (latest may be given to mean the most recent, block). By default 0.
        :param to_block:The number of the latest block (latest may be given to mean the most recent, block). By default latest.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getScEvent", chain_type)
        message['params']['address'] = address
        message['params']['topics'] = topics
        message['params']['fromBlock'] = from_block
        message['params']['toBlock'] = to_block
        response = json.loads(self._make_request(message))
        return response['result']

    def monitor_event(self, address, topics, chain_type='WAN'):
        """
        Subscribe to a smart contract event monitor. The server will push the event to the subscriber when the event occurs.
        :param address:The contract address.
        :param topics:Array of values which must each appear in the log entries. The order is important, if you want to leave topics out use null, e.g. [null, '0x00...'].
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("monitorEvent", chain_type)
        message['params']['address'] = address
        message['params']['topics'] = topics
        response = json.loads(self._make_request(message))
        return response['result']

    # POS #
    def get_activity(self, epoch_id, chain_type='WAN'):
        """
        Get the activity information of the specified epoch. For historical epochs the values are fixed, while the current epoch will update the latest current values in real time.
        :param epoch_id:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :param chain_type:The epochID you want to search.
        :return:
        """
        message = self._new_message("getActivity", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_current_epoch_info(self, chain_type='WAN'):
        """
        Get the current epoch info.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getCurrentEpochInfo", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_current_staker_info(self, chain_type='WAN'):
        """
        Returns an array with information on each of the current validators.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getCurrentStakerInfo", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_delegator_incentive(self, address, from_epoch, to_epoch, chain_type='WAN'):
        message = self._new_message("getDelegatorIncentive", chain_type)
        message['params']['address'] = address
        message['params']['from'] = from_epoch
        message['params']['to'] = to_epoch
        response = json.loads(self._make_request(message))
        return response['result']

    def get_delegator_stake_info(self, address, chain_type='WAN'):
        """
        Get the identified delegator's staking info.
        :param address:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :param chain_type:The delegator address you want to query.
        :return:
        """
        message = self._new_message("getDelegatorStakeInfo", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_delegator_sup_stake_info(self, address, chain_type='WAN'):
        """
        Get the specified delegator's supplementary information.
        :param address: The delegator's address you want to query.
        :param chain_type: The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getDelegatorSupStakeInfo", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_delegator_total_incentive(self, address, validator_address=None, from_epoch=None, to_epoch=None,
                                      chain_type='WAN'):
        """
        Get the identified delegator's total incentives.
        :param address:The delegator's address you want to query.
        :param validator_address:The validator's address you want to query.
        :param from_epoch:The starting epochID you want to query.
        :param to_epoch:The ending epochID you want to query.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getDelegatorTotalIncentive", chain_type)
        message['params']['address'] = address
        if validator_address is not None:
            message['params']['validatorAddress '] = validator_address
        if from_epoch is not None:
            message['params']['from'] = from_epoch
        if to_epoch is not None:
            message['params']['to'] = to_epoch
        response = json.loads(self._make_request(message))
        return response['result']

    def get_epoch_id(self, chain_type='WAN'):
        message = self._new_message("getEpochID", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_epoch_id_by_time(self, query_time, chain_type='WAN'):
        """
        Calculates the Epoch ID according to the time. Enter the UTC time in seconds to get the corresponding Epoch ID.
        :param query_time:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :param chain_type:The UTC time seconds you want to query.
        :return:
        """
        message = self._new_message("getEpochIDByTime", chain_type)
        message['params']['time'] = query_time
        response = json.loads(self._make_request(message))
        return response['result']

    def get_epoch_incentive_block_number(self, epoch_id, chain_type='WAN'):
        """
        Get the block number which contains the incentives transactions for the specified epoch.
        :param epoch_id:The epochID you want to query.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getEpochIncentiveBlockNumber", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_epoch_incentive_pay_detail(self, epoch_id, chain_type='WAN'):
        """
        Get the reward information of the specified epoch, enter epochID, and reward payment details (including RNP reward, EL reward and chunk reward) will be returned for all the verification nodes and clients working in the epoch.
        :param epoch_id:The epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getEpochIncentivePayDetail", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_epoch_leaders_by_epoch_id(self, epoch_id, chain_type='WAN'):
        """
        Get the public key list of the epoch leaders of the specified EpochID with the input parameter as EpochID.
        :param epoch_id:The epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getEpochLeadersByEpochID", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_epoch_stake_out(self, epoch_id, chain_type='WAN'):
        """
        Get the record of stake out transactions for the specified epoch.
        :param epoch_id:The epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getEpochStakeOut", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_leader_group_by_epoch_id(self, epoch_id, chain_type='WAN'):
        """
        Get the Epoch Leader and Random Number Proposer addresses and public key lists in the specified epoch.
        :param epoch_id:The epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getLeaderGroupByEpochID", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_max_block_number(self, epoch_id, chain_type='WAN'):
        """
        Get the highest block number of the specified epoch ID(s).
        :param epoch_id: The epochID(s) you want to query. Can be number or array of numbers.
        :param chain_type: The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("ime", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_max_stable_blk_number(self, chain_type='WAN'):
        """
        Get the current highest stable block number (no rollback).
        :param chain_type: The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getMaxStableBlkNumber", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_pos_info(self, chain_type='WAN'):
        """
        Returns the epoch ID and block number when the switch from POW to the POS protocol occurred.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getPosInfo", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_random(self, epoch_id, block_number, chain_type='WAN'):
        """
        Get the random number of the queried epochID and block number.
        :param epoch_id:The epochID you want to search.
        :param block_number:The blockNumber you want to search. If blockNumber is -1, use the latest block.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getRandom", chain_type)
        message['params']['epochID'] = epoch_id
        message['params']['blockNumber'] = block_number
        response = json.loads(self._make_request(message))
        return response['result']

    def get_random_proposers_by_epoch_id(self, epoch_id, chain_type='WAN'):
        """
        Gets Random Number Proposer public keys of the specified epoch.
        :param epoch_id:The epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getRandomProposersByEpochID", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_slot_activity(self, epoch_id, chain_type='WAN'):
        """
        Get the slot leader activity information of the specified epoch.
        :param epoch_id: The epochID you want to search.
        :param chain_type: The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getSlotActivity", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_slot_count(self, chain_type='WAN'):
        """
        Returns the total number of slots in an epoch. This is a constant.
        :param chain_type: The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getSlotCount", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_slot_id(self, chain_type='WAN'):
        """
        Get the current epoch slot ID.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getSlotID", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_slot_time(self, chain_type='WAN'):
        """
        Get the time span of a slot in seconds.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getSlotTime", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    def get_staker_info(self, block_number, chain_type='WAN'):
        """
        Returns an array of validator information for all validators in the specified block number.
        :param block_number:The blockNumber you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getStakerInfo", chain_type)
        message['params']['blockNumber'] = block_number
        response = json.loads(self._make_request(message))
        return response['result']

    def get_time_by_epoch_id(self, epoch_id, chain_type='WAN'):
        """
        Returns the specified epoch's start time in UTC time seconds.
        :param epoch_id:The epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getTimeByEpochID", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_validator_activity(self, epoch_id, chain_type='WAN'):
        """
        Get the validator activity information of the Epoch Leaders and Random Number Proposers of the specified epoch. Returns null for the current Epoch or future Epochs.
        :param epoch_id:The epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getValidatorActivity", chain_type)
        message['params']['epochID'] = epoch_id
        response = json.loads(self._make_request(message))
        return response['result']

    def get_validator_info(self, address, chain_type='WAN'):
        """
        Get the specified validator info by the validator address.
        :param address:The validator address you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getValidatorInfo", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_validator_stake_info(self, address, chain_type='WAN'):
        """
        Get the specified validator staking info by the validator owner's address.
        :param address:The validator owner address you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getValidatorStakeInfo", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_validator_sup_stake_info(self, address, chain_type='WAN'):
        """
        Get supplementary information for the specified validator.
        :param address:The validator address you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getValidatorSupStakeInfo", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_validator_total_incentive(self, address, from_epoch, to_epoch, chain_type='WAN'):
        """
        Get the specified validator's total incentives.
        :param address:The validator address you want to search.
        :param from_epoch:The begin epochID you want to search.
        :param to_epoch:The end epochID you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN', default: 'WAN'.
        :return:
        """
        message = self._new_message("getValidatorTotalIncentive", chain_type)
        message['params']['address'] = address
        if from_epoch is not None:
            message['params']['from'] = from_epoch
        if to_epoch is not None:
            message['params']['to'] = to_epoch
        response = json.loads(self._make_request(message))
        return response['result']

    # Status #
    def get_gas_price(self, chain_type='WAN'):
        """
        Get the current gas price in wei as bigNumber type.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getGasPrice", chain_type)
        response = json.loads(self._make_request(message))
        return response['result']

    # Tokens #
    def get_multi_token_balance(self, address, token_sc_address, chain_type='WAN'):
        """
        Get token balance for multiple addresses of specified token on Wanchain in a single call.
        :param address:An array of addresses being queried.
        :param token_sc_address:The token contract address for specified token. I.e., If chainType is 'WAN', it should be the token address for "WETH" or "WBTC".
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH', default: 'WAN'.
        :return:
        """
        message = self._new_message("getMultiTokenBalance", chain_type)
        message['params']['address'] = address
        message['params']['tokenScAddr'] = token_sc_address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_multi_token_info(self, token_sc_address_array, chain_type='WAN'):
        """
        Get the information for multiple tokens.
        :param token_sc_address_array:The token address array for the tokens that you want to query.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getMultiTokenInfo", chain_type)
        message['params']['tokenScAddrArray'] = token_sc_address_array
        response = json.loads(self._make_request(message))
        return response['result']

    def get_token_allowance(self, token_sc_address, owner_address, spender_address, chain_type='WAN'):
        """
        Get the token allowance for one specific account on one contract for one specific spender account on a certain chain.
        :param token_sc_address:The token contract address for the specified token.
        :param owner_address:The owner address on the specified contract.
        :param spender_address:The spender address on the specified contract.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getTokenAllowance", chain_type)
        message['params']['tokenScAddr'] = token_sc_address
        message['params']['ownerAddr'] = owner_address
        message['params']['spenderAddr'] = spender_address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_token_balance(self, address, token_sc_address, chain_type='WAN'):
        """
        Get token balance for a single address of a specified token on Wanchain.
        :param address:The account being queried.
        :param token_sc_address:The token contract address for specified token. I.e., If chainType is 'WAN', it should be the token address for "WETH" or "WBTC".
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH', default: 'WAN'.
        :return:
        """
        message = self._new_message("getTokenBalance", chain_type)
        message['params']['address'] = address
        message['params']['tokenScAddr'] = token_sc_address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_token_info(self, token_sc_address, chain_type='WAN'):
        """
        Get the info of token contract, like symbol and decimals, on certain chain.
        :param token_sc_address:The token contract address for the specified token.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getTokenInfo", chain_type)
        message['params']['tokenScAddr'] = token_sc_address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_token_supply(self, token_sc_address, chain_type='WAN'):
        """
        Get total amount of certain token on Wanchain.
        :param token_sc_address:The token contract address for the specified token.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH', default: 'WAN'.
        :return:
        """
        message = self._new_message("getTokenSupply", chain_type)
        message['params']['tokenScAddr'] = token_sc_address
        response = json.loads(self._make_request(message))
        return response['result']

    # Transactions #
    def get_trans_by_address(self, address, chain_type='WAN'):
        """
        Get transaction information via the specified address on certain chain.
        :param address:The account's address that you want to search.
        :param chain_type:The chain being queried. Currently supports "WAN".
        :return:
        """
        message = self._new_message("getTransByAddress", chain_type)
        message['params']['address'] = address
        response = json.loads(self._make_request(message))
        return response['result']

    def get_trans_by_address_between_blocks(self, address, start_block_number, end_block_number, chain_type='WAN'):
        """
        Get transaction information via the specified address between the specified startBlockNo and endBlockNo on certain chain.
        Comments:
        if no startBlockNo given, startBlockNo will be set to 0;
        if no endBlockNo given, endBlockNo will be set to the newest blockNumber.
        :param address:The account's address that you want to search.
        :param start_block_number:The startBlockNo that you want to search from.
        :param end_block_number:The endBlockNo that you want to search to.
        :param chain_type:The chain being queried. Currently supports "WAN".
        :return:
        """
        message = self._new_message("getTransByAddressBetweenBlocks", chain_type)
        message['params']['address'] = address
        message['params']['startBlockNo'] = start_block_number
        message['params']['endBlockNo'] = end_block_number
        response = json.loads(self._make_request(message))
        return response['result']

    def get_trans_by_block(self, block_number=None, block_hash=None, chain_type='WAN'):
        """
        Get transaction information in a given block by block number or block hash on certain chain.
        :param block_number:The blockNumber you want to search.
        :param block_hash:The blockHash you want to search.
        :param chain_type:The chain being queried. Currently supports "WAN".
        :return:
        """
        message = self._new_message("getTransByBlock", chain_type)
        if block_number is not None:
            message['params']['blockNumber'] = block_number
        if block_hash is not None:
            message['params']['blockHash'] = block_hash
        response = json.loads(self._make_request(message))
        return response['result']

    def get_transaction_confirm(self, wait_blocks, tx_hash, chain_type='WAN'):
        """
        Get the transaction mined result on certain chain. When the receipt not existed, return directly with 'no receipt was found'; If receipt existed, the receipt will be returned after confirm-block-number blocks.
        :param wait_blocks:The confirm-block-number you want to set.
        :param tx_hash:The txHash you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getTransactionConfirm", chain_type)
        message['params']['waitBlocks'] = wait_blocks
        message['params']['txHash'] = tx_hash
        response = json.loads(self._make_request(message))
        return response['result']

    def get_transaction_receipt(self, tx_hash, chain_type='WAN'):
        """
        Get the receipt of a transaction by transaction hash on certain chain.
        :param tx_hash:The txHash you want to search.
        :param chain_type:The chain being queried. Currently supports 'WAN' and 'ETH'.
        :return:
        """
        message = self._new_message("getTransactionReceipt", chain_type)
        message['params']['txHash'] = tx_hash
        response = json.loads(self._make_request(message))
        return response['result']

    def get_tx_info(self, tx_hash, out_format=None, chain_type='WAN'):
        """
        Get the transaction detail via txHash on certain chain.
        :param tx_hash:The txHash you want to search.
        :param out_format:Whether to get the serialized or decoded transaction, in this case, chainType should be "BTC": Set to false (the default) to return the serialized transaction as hex. Set to true to return a decoded transaction.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH" or "BTC".
        :return:
        """
        message = self._new_message("getTxInfo", chain_type)
        message['params']['txHash'] = tx_hash
        if format is not None:
            message['params']['format'] = out_format
        response = json.loads(self._make_request(message))
        return response['result']

    def send_raw_transaction(self, signed_tx, chain_type='WAN'):
        """
        Submit a pre-signed transaction for broadcast to certain chain.
        :param signed_tx:The signedTx you want to send.
        :param chain_type:The chain being queried. Currently supports "WAN" or "ETH" or "BTC".
        :return:
        """
        message = self._new_message("sendRawTransaction", chain_type)
        message['params']['signedTx'] = signed_tx
        response = json.loads(self._make_request(message))
        return response['result']
