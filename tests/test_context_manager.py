import pytest
from pytest import raises

from amqp_mock import AmqpServer, HttpServer, Message, Storage, create_amqp_mock

from ._test_utils.amqp_client import AmqpClient
from ._test_utils.steps import given, then, when


@pytest.mark.asyncio
async def test_async_context_manager():
    with given:
        storage = Storage()
        http_server = HttpServer(storage, "localhost", 8080)
        amqp_server = AmqpServer(storage, "localhost", 5674)
        queue = "test_queue"

    with when:
        async with create_amqp_mock(http_server, amqp_server) as mock:
            await mock.client.publish_message(queue, Message("text"))

            async with AmqpClient(amqp_server.host, amqp_server.port) as amqp_client:
                await amqp_client.consume(queue)
                messages = await amqp_client.wait_for(message_count=1)

    with then:
        assert len(messages) == 1


@pytest.mark.asyncio
async def test_sync_context_manager():
    with given:
        storage = Storage()
        http_server = HttpServer(storage, "localhost", 8080)
        amqp_server = AmqpServer(storage, "localhost", 5674)

    with when, raises(Exception) as exception:
        with create_amqp_mock(http_server, amqp_server):
            pass

    with then:
        assert isinstance(exception.value, TypeError)
