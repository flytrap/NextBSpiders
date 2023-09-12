# Generated by the Protocol Buffers compiler. DO NOT EDIT!
# source: tg.proto
# plugin: grpclib.plugin.main
import abc
import typing

import grpclib.const
import grpclib.client

if typing.TYPE_CHECKING:
    import grpclib.server

from . import tg_pb2


class TgBotServiceBase(abc.ABC):
    @abc.abstractmethod
    async def ImportData(
        self, stream: "grpclib.server.Stream[tg_pb2.DataItem, tg_pb2.ImportResponse]"
    ) -> None:
        pass

    def __mapping__(self) -> typing.Dict[str, grpclib.const.Handler]:
        return {
            "/tg.v1.TgBotService/ImportData": grpclib.const.Handler(
                self.ImportData,
                grpclib.const.Cardinality.STREAM_STREAM,
                tg_pb2.DataItem,
                tg_pb2.ImportResponse,
            ),
        }


class TgBotServiceStub:
    def __init__(self, channel: grpclib.client.Channel) -> None:
        self.ImportData = grpclib.client.StreamStreamMethod(
            channel,
            "/tg.v1.TgBotService/ImportData",
            tg_pb2.DataItem,
            tg_pb2.ImportResponse,
        )
