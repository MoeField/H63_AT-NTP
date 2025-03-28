import asyncio
import logging

from H63AtBasic import H63AtBasic
from conf import *

cilDelayTime=2

class H63Client(H63AtBasic):
    def __init__(self, port:str, baudrate=115200):
        super().__init__(port, baudrate)
        self.name = f"{CIL_NAME}"
        self.addr = '111122220008'
        self.isStart = False
        self.svrName="Server"

    async def startClient(self):
        if self.isStart:
            logging.info("@cli:\tClient已经启动,无需再次启动")
            return 1
        serConnOk = await self.open_connection()
        if not serConnOk:
            logging.error("Client启动失败:串口未打开")
            return -1
        setModelOk = await self.send_command("AT+SETMODE=0")
        setAddrOk = await self.send_command(f"AT+SETSLEADDR={self.addr}")
        setNameOk = await self.send_command(f"AT+CSETNAME={self.name}")
        logging.info(f"setNameOk:{setNameOk}")
        self.isStart = True
        await asyncio.sleep(cilDelayTime)
        """
        AT+CSLIST                       //搜索并获取服务端列表
        AT+CCONNECT=SERVER              //连接名字为SERVER的服务端
        """
        scnServers,scanOk = await self.send_command("AT+CSLIST")
        scnServers = scnServers.decode('ascii')
        logging.info(f"搜索到的服务端: {scnServers}")
        #svrName,SvrAddr,SvrRssi = scnServers.split(',')# only work if there is only one server

        
        connServer,connOk = await self.send_command(f"AT+CCONNECT={self.svrName}")

        if serConnOk and setModelOk and setAddrOk and setNameOk and scanOk and connOk:
            logging.info("@cli:\tClient启动成功")
            return 0
        else:
            logging.error(f"""@cli:\tClient启动失败::
                SerConnOk:{serConnOk} SetModelOk:{setModelOk}
                SetAddrOk:{setAddrOk} SetNameOk:{setNameOk}
                ScanOk:{scanOk} ConnOk:{connOk}
            """)
            return -1

    async def wait_decodeContent(self)->str:
        """
        等待接收数据
        """
        logging.info("@cli:\t@Client::等待接收数据::")
        respHex = await self._wait_response()
        respStr = respHex.decode('ascii')
        return respStr

    async def send_EncodeData(self,data:str):
        """
        发送数据
        """
        #data to hex
        dataHex = data.encode('ascii').hex()

        sendOk = await self.send_command(f"AT+CSEND={dataHex}")
        return sendOk

    async def closeClient(self):
        if self.isStart:
            self.isStart = False
            await self.send_command("AT+CCONNECT=0")
            await self.close_connection()
            logging.info("@cli:\tClient关闭成功")
        else:
            logging.error("Client未启动,无需关闭")