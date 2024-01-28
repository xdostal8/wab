import pika

conn_params = pika.ConnectionParameters(host='rabbitmq')

def publish(msg: str):
    conn = pika.BlockingConnection(conn_params)
    channel = conn.channel()
    channel.basic_publish(
        exchange='',
        routing_key='wab_4',
        body=msg
    )
    conn.close()