import pika
import os, json

class MessageConfiguration():
    def __init__(self, host=None, port=None, socket_timeout=None, login=None, password=None, sender_exchange=None, sender_routing_key=None, receiver_queue=None, receiver_exchange=None, receiver_routing_key=None):
        self.host = host
        self.port = port
        self.socket_timeout = socket_timeout
        self.login = login
        self.password = password
        self.sender_exchange = sender_exchange
        self.sender_routing_key = sender_routing_key
        self.receiver_queue = receiver_queue
        self.receiver_exchange = receiver_exchange
        self.receiver_routing_key = receiver_routing_key
    
    def load_config_from_json(self):
        config_values = MessageConfiguration.get_config_from_json(config_path='./message_config.json')
        if config_values != None:
            self.host = config_values['host']
            self.port = config_values['port']
            self.socket_timeout = config_values['socket_timeout']
            self.login = config_values['login']
            self.password = config_values['password']
            self.sender_exchange = config_values['sender_exchange']
            self.sender_routing_key = config_values['sender_routing_key']
            self.receiver_queue = config_values['receiver_queue']
            self.receiver_exchange = config_values['receiver_exchange']
            self.receiver_routing_key = config_values['receiver_routing_key']
        else:
            exit(-1)

    @staticmethod
    def get_config_from_json(config_path: str):
        if not os.path.exists(config_path):
            return None

        file = open(config_path)
        data = json.load(file)
        config = data['config']
        file.close()
        return config
    

class MessageSender():
    '''
    Sends messages according to specified send settings.
    '''
    
    @staticmethod
    def send(configuration: MessageConfiguration, data: str):
        credentials = pika.PlainCredentials(configuration.login, configuration.password)
        connection_parameters = pika.ConnectionParameters(host=configuration.host, 
                                                              port=configuration.port, 
                                                              credentials=credentials, 
                                                              socket_timeout=configuration.socket_timeout)
                
        connection = pika.BlockingConnection(connection_parameters)
        channel = connection.channel()

        body = json.dumps({
                "transaction": {
                    "data": data
                }
            })

        channel.exchange_declare(exchange=configuration.sender_exchange, exchange_type='direct')
        channel.basic_publish(exchange=configuration.sender_exchange, 
                                  routing_key=configuration.sender_routing_key, 
                                  body=body)
                    
        connection.close()