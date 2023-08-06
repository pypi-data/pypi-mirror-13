# -*- coding: utf-8 -*-
from random import randint, seed
from unittest import TestCase
from unittest.mock import patch

from pubsub.client import PubSub


class TestPubSubClient(TestCase):

    @classmethod
    def setUpClass(cls):
        seed()
        cls.app_name = 'integration-tests-{}'.format(randint(0, 10**6))
        cls.topic = 'tests.publish_and_pull-{}'.format(randint(0, 10**6))
        cls.pubsub = PubSub('ployst-proto', cls.app_name)
        cls.pubsub.ensure_topic(cls.topic)
        cls.pubsub.ensure_subscription(cls.topic)

    @classmethod
    def tearDownClass(cls):
        cls.pubsub.delete_topic(cls.topic)
        cls.pubsub.delete_subscription(cls.topic)

    def test_publish_pull_and_acknowledge(self):
        one = {'content': 'One'}
        two = {'content': 'Two'}

        self.pubsub.publish(self.topic, [one, two])
        messages = self.pubsub.pull(self.topic, wait=True)

        try:
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[0].payload, one)
            self.assertEqual(messages[1].payload, two)
        finally:
            self.pubsub.acknowledge(self.topic, messages)

    def test_unacked_messages_can_be_pulled_again(self):
        one = {'content': 'One'}
        two = {'content': 'Two'}

        self.pubsub.publish(self.topic, [one, two])
        messages = self.pubsub.pull(self.topic, wait=True)
        # only ack the second message:
        messages[1].ack()

        next_messages = self.pubsub.pull(self.topic, wait=True)
        try:
            self.assertEqual(len(next_messages), 1)
            self.assertEqual(next_messages[0].payload, one)
        finally:
            self.pubsub.acknowledge(self.topic, next_messages)

    def test_pull_doesnt_wait_if_no_messages(self):
        pulled_messages = self.pubsub.pull(self.topic)

        self.assertEqual(pulled_messages, [])

    def test_known_topics_are_not_retrieved(self):
        with patch.object(self.pubsub.topics, 'list') as list_topics:
            self.pubsub.ensure_topic(self.topic)
            self.assertEqual(list_topics.call_count, 0)

    def test_known_subscriptions_are_not_retrieved(self):
        with patch.object(self.pubsub.subscriptions, 'list') as list_subs:
            self.pubsub.ensure_subscription(self.topic)
            self.assertEqual(list_subs.call_count, 0)

    def test_subscriptions_and_topics_can_be_created_in_any_order(self):
        new_topic = self.topic + 'b'

        try:
            pulled_messages = self.pubsub.pull(new_topic)
            self.assertEqual(pulled_messages, [])

            self.pubsub.publish(new_topic, ['Hello'])
            pulled_messages = self.pubsub.pull(new_topic, wait=True)
            self.assertEqual(pulled_messages[0].payload, 'Hello')
        finally:
            self.pubsub.delete_subscription(new_topic)
            self.pubsub.delete_topic(new_topic)
