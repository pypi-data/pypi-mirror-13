__author__ = 'tdpreece'
__author__ = 'tdpreece'
import logging
import time
import json
from collections import OrderedDict

import stomp

logger = logging.getLogger('tdl.client')
logger.addHandler(logging.NullHandler())


class Client(object):
    def __init__(self, hostname, port, username):
        self.hostname = hostname
        self.port = port
        self.username = username

    def go_live_with(self, implementation_map):
        handling_strategy = RespondToAllRequests(implementation_map)
        self.run(handling_strategy)

    def run(self, handling_strategy):
        try:
            remote_broker = RemoteBroker(self.hostname, self.port, self.username)
            remote_broker.subscribe(handling_strategy)
            time.sleep(1)
            remote_broker.close()
        except Exception as e:
            print('There was a problem processing messages')
            logger.exception('Problem communicating with the broker.')


class RespondToAllRequests(object):
    def __init__(self, implementation_map):
        self.implementation_map = implementation_map

    def process_next_message_from(self, remote_broker, headers, message):
        try:
            decoded_message = json.loads(message)
        except:
            print('Invalid message format')
        method = decoded_message['method']
        params = decoded_message['params']
        id = decoded_message['id']
        if method not in self.implementation_map:
            self.print_user_message(
                params,
                'error = method "{}" did not match any processing rule, (NOT PUBLISHED)'.format(method),
                id,
                method
            )
                    
        implementation = self.implementation_map[method]['test_implementation']
        try:
           result = implementation(params)
           user_result_message = 'resp = {}'.format(result) 
        except Exception as e:
           logger.info('The user implementation has thrown an exception: {}'.format(e.message))
           user_result_message = 'error = user implementation raised exception, (NOT PUBLISHED)'
        else:
            response = OrderedDict([
                ('result', result),
                ('error', None),
                ('id', id),
                ])
            if 'publish' in self.implementation_map[method]['action']:
                remote_broker.acknowledge(headers)
                remote_broker.publish(response)
            else:
                user_result_message = 'resp = {}, (NOT PUBLISHED)'.format(result)

        self.print_user_message(params, user_result_message, id, method)
        if 'stop' in self.implementation_map[method]['action']:
            remote_broker.conn.unsubscribe(1)
            remote_broker.conn.remove_listener('listener')

    def print_user_message(self, params, user_result_message, id, method):
        params_str = ", ".join([str(p) for p in params])
        print('id = {id}, req = {method}({params}), {user_result_message}'.format(id=id, method=method, params=params_str,
                                                                           user_result_message=user_result_message))


class Listener(stomp.ConnectionListener):
    def __init__(self, remote_broker, handling_strategy):
        self.remote_broker = remote_broker
        self.handling_strategy = handling_strategy

    def on_message(self, headers, message):
        self.handling_strategy.process_next_message_from(self.remote_broker, headers, message)



class RemoteBroker(object):
    def __init__(self, hostname, port, username):
        hosts = [(hostname, port)]
        self.conn = stomp.Connection(host_and_ports=hosts, timeout=10)
        self.conn.start()
        self.conn.connect(wait=True)
        self.username = username

    def acknowledge(self, headers):
        self.conn.ack(headers['message-id'], headers['subscription'])

    def publish(self, response):
        self.conn.send(
            body=json.dumps(response, separators=(',', ':')),
            destination='{}.resp'.format(self.username)
        )

    def subscribe(self, handling_strategy):
        listener = Listener(self, handling_strategy)
        self.conn.set_listener('listener', listener)
        self.conn.subscribe(
            destination='{}.req'.format(self.username),
            id=1,
            ack='client-individual'
        )

    def close(self):
        self.conn.disconnect()
