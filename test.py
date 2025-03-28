from H63Server import H63Server
from H63Client import H63Client
from conf import *

import asyncio
import logging
import time

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def DerverProc():
    com1 = H63Server(port='COM11')
    doOpen=await com1.startServer()
    print(f"ServerOpenStatus::{doOpen}")

    while True:
        resp0= await com1.wait_decodeContent()
        timeNow = time.time()

        await asyncio.sleep(0.01)
        print(f"\nTIME: {timeNow}",end='\t\n')
        print(f"Data:\t{resp0}",end='\t,')
        if '+CONNECT' in resp0:
            print("Server:连接成功")
            continue
        elif '+SRECVDATA' in resp0:
            print("Server:接收到数据")

            if END_STR_HEX in resp0:
                print("\n\nServer:结束接收")
                await com1.send_EncodeData(f"TimeNow[s] {timeNow}, CloseServer")
                break

        await com1.send_EncodeData(f"TimeNow[s] {timeNow}")
    await com1.closeServer()


async def ClientProc():
    com2 = H63Client(port='COM12')
    doOpen=await com2.startClient()
    print(f"ClientConnectStatus::{doOpen}")
    await asyncio.sleep(1)
    sendOk = await com2.send_EncodeData("Hello,Server!")
    revDat1 = await com2.wait_decodeContent()

    await asyncio.sleep(1)
    counterXX=0

    while True:
        timeNow = time.time()

        sendTimeOk =await com2.send_EncodeData(f"TimeNow[c] {timeNow}")
        revDat2 = await com2.wait_decodeContent()
        print(f"Client::[{counterXX}]发送数据: {sendTimeOk}")
        print(f"Client::[{counterXX}]接收数据: {revDat2}")
        counterXX+=1
        await asyncio.sleep(1)
        if counterXX>10:
            #send end
            sendEndOk =await com2.send_EncodeData("END")
            print(f"\n\nClient::[{counterXX}]发送结束: {sendEndOk}")
            break
    await com2.closeClient()


async def main():
    # 并行执行服务端和客户端协程
    await asyncio.gather(
        DerverProc(),
        ClientProc()
    )

if __name__ == "__main__":
    asyncio.run(main())