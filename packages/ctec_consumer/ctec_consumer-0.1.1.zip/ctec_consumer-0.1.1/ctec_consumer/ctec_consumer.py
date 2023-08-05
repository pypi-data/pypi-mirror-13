# encoding: utf-8
import logging
import platform
import signal
import sys
import traceback
from multiprocessing import Pool as ThreadPool

import pika

from models.worker_message import WorkerMessage

reload(sys)
sys.setdefaultencoding('utf-8')

CONSUME_SUCCESS = 0
CONSUME_REDELIVER = 1
CONSUME_REJECT = 2


class Consumer(object):
    def __init__(self, amqp_url, queue, logger=None, prefetch_count=30, thread_num=5, heart_interval=30):
        """
        初始化Consumer
        :param amqp_url: 队列amqp地址
        :param queue: 队列名称
        :param logger: logger对象
        :param prefetch_count: 一次拉取消息数量，默认30
        :param thread_num: 线程或进程数量，默认5
        :param heart_interval: 心跳间隔，默认30秒
        :return:
        """
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url + '?heartbeat_interval=%s' % heart_interval
        self.pool = ThreadPool(thread_num)
        self.queue = queue
        self.handle_message_worker = None
        self.logger = logging if logger is None else logger
        # 限制单个channel可同时拉取的消息数量
        self.prefetch_count = prefetch_count

    def connect(self):
        """
        创建连接
        :return:
        """
        self.logger.info('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.on_connection_open,
                                     stop_ioloop_on_close=False)

    def close_connection(self):
        """
        关闭连接
        :return:
        """
        self.logger.info('Closing connection')
        self._connection.close()

    def add_on_connection_close_callback(self):
        """
        增加连接关闭的回调函数
        :return:
        """
        self.logger.info('Adding connection close callback')
        self._connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        """
        关闭连接回调函数
        :param connection:
        :param reply_code:
        :param reply_text:
        :return:
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                                reply_code, reply_text)
            self._connection.add_timeout(5, self.reconnect)

    def on_connection_open(self, unused_connection):
        """
        连接打开回调函数
        :param unused_connection:
        :return:
        """
        self.logger.info('Connection opened')
        self.add_on_connection_close_callback()
        self.open_channel()

    def reconnect(self):
        """
        重新连接
        :return:
        """
        self._connection.ioloop.stop()

        if not self._closing:
            # 创建一个新连接
            self._connection = self.connect()

            # 打开新的IOLOOP循环
            self._connection.ioloop.start()

    def add_on_channel_close_callback(self):
        """
        增加通道关闭回调函数
        :return:
        """
        self.logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """
        通道关闭回调函数
        :param channel:
        :param reply_code:
        :param reply_text:
        :return:
        """
        self.logger.warning('Channel %i was closed: (%s) %s',
                            channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        """
        通道打开回调函数
        :param channel:
        :return:
        """
        self.logger.info('Channel opened')
        self._channel = channel
        self._channel.basic_qos(prefetch_count=self.prefetch_count)
        self.add_on_channel_close_callback()
        self.start_consuming()

    def add_on_cancel_callback(self):
        """
        增加取消回调函数
        :return:
        """
        self.logger.info('Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """
        取消回调函数
        :param method_frame:
        :return:
        """
        self.logger.info('Consumer was cancelled remotely, shutting down: %r',
                         method_frame)
        if self._channel:
            self._channel.close()

    def acknowledge_message(self, delivery_tag):
        """
        发送ACK
        :param delivery_tag:
        :return:
        """
        self.logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def redeliver_message(self, callback=None, requeue=True):
        """
        发送redeliver
        :param callback:
        :param requeue:
        :return:
        """
        self.logger.info('Redeliver message')
        self._channel.basic_recover(callback, requeue)

    def nack_message(self, delivery_tag):
        """
        发送nack
        :param delivery_tag:
        :return:
        """
        self.logger.info('Reject message %s', delivery_tag)
        self._channel.basic_nack(delivery_tag)

    def reject_message(self, delivery_tag):
        """
        发送reject
        :param delivery_tag:
        :return:
        """
        self.logger.info('Reject message %s', delivery_tag)
        self._channel.basic_reject(delivery_tag, requeue=False)

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """
        消息消费
        :param unused_channel:
        :param basic_deliver:
        :param properties:
        :param body:
        :return:
        """
        self.logger.info('Received message # %s from %s: %s',
                         basic_deliver.delivery_tag, properties.app_id, body)
        try:
            self.pool.apply_async(self.message_worker, (WorkerMessage(basic_deliver, properties, body),),
                                  callback=self.worker_callback)
        except AssertionError:
            self.logger.warning('线程池已关闭！不接受新任务！回退消息到队列！message = %s', body)
            self.nack_message(basic_deliver.delivery_tag)
        except Exception:
            self.logger.error('消息消费失败！delivery_tag = %s', basic_deliver.delivery_tag)
            self.logger.error(traceback.format_exc())
            self.acknowledge_message(basic_deliver.delivery_tag)

    def on_cancelok(self, unused_frame):
        """
        取消完成
        :param unused_frame:
        :return:
        """
        self.logger.info('RabbitMQ acknowledged the cancellation of the consumer')
        self.close_channel()

    def stop_consuming(self):
        """
        停止消费
        :return:
        """
        if self._channel:
            self.logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)

    def start_consuming(self):
        """
        开始消费
        :return:
        """
        self.logger.info('Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.queue)

    def close_channel(self):
        """
        关闭通道
        :return:
        """
        self.logger.info('Closing the channel')
        self.pool.close()
        self.pool.join()
        self._channel.close()

    def open_channel(self):
        """
        打开通道
        :return:
        """
        self.logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def run(self):
        """
        启动
        :return:
        """
        if int(platform.python_version_tuple()[0]) < 3:
            raise Exception('Python版本号低于3，请使用dummy包中的线程版！')
        if self.handle_message_worker is None:
            raise Exception('未注册消息处理方法！')
        else:
            # 增加信号
            signal.signal(signal.SIGTERM, self.stop)
            signal.signal(signal.SIGINT, self.stop)
            self._connection = self.connect()
            self._connection.ioloop.start()

    def stop(self):
        """
        停止
        :return:
        """
        self.logger.info('Stopping')
        self._closing = True
        # 关闭线程池
        self.pool.close()
        self.pool.join()
        # 停止channel
        self.stop_consuming()
        self._connection.ioloop.stop()
        self.logger.info('Stopped')

    def register_worker(self, worker):
        """
        注册实际处理消息的worker
        :param worker: 处理消息方法
        :return:
        """
        self.logger.debug("开始注册worker")
        self.handle_message_worker = worker

    def message_worker(self, worker_message):
        """
        处理消息方法
        :param worker_message: 消息对象
        :return:
        """
        self.logger.debug('开始处理消息，delivery_tag = %s', worker_message.basic_deliver.delivery_tag)
        result = self.handle_message_worker(worker_message)
        self.logger.debug('消息处理完成')
        if result == CONSUME_REJECT:
            self.logger.warn('消息处理失败，被丢弃！%s', worker_message.body)
        return [result, worker_message.basic_deliver.delivery_tag]

    def worker_callback(self, worker_result):
        """
        消息处理回调方法
        :param worker_result: 执行结果对象。数据结构[code,delivery_tag]
        :return:
        """
        if worker_result[0] == CONSUME_SUCCESS:
            self.acknowledge_message(worker_result[1])
        elif worker_result[0] == CONSUME_REDELIVER:
            self.nack_message(worker_result[1])
        elif worker_result[0] == CONSUME_REJECT:
            self.reject_message(worker_result[1])
        else:
            self.logger.warning('未找到处理code。code = %s', worker_result[0])
