import asyncio
import logging

from H63AtBasic import H63AtBasic
from conf import *

class H63Server(H63AtBasic):
    def __init__(self, port:str, baudrate=115200):
        super().__init__(port, baudrate)
        self.name = 'Server'
        self.addr = '111122220009'
        self.isStart = False
    
    async def startServer(self):
        if self.isStart == True:
            logging.warning("@Srv:\tServer已经启动,无需再次启动")
            return 1
        serConnOk = await self.open_connection()
        if not serConnOk:
            logging.error("@Srv:\tServer启动失败:串口未打开")
            return -1

        setModelOk = await self.send_command("AT+SETMODE=1")
        setAddrOk = await self.send_command(f"AT+SETSLEADDR={self.addr}")
        setNameOk = await self.send_command(f"AT+SSETNAME={self.name}")
        setServerOk = await self.send_command("AT+SSERVER=1")
        if serConnOk and setModelOk and setAddrOk and setNameOk and setServerOk:
            logging.info("@Srv:\tServer启动成功")
            self.isStart = True
            return 0
        else:
            logging.error(f"""@Srv:\tServer启动失败:: 
                SerConnOk:{serConnOk} SetModelOk:{setModelOk} 
                SetAddrOk:{setAddrOk} SetNameOk:{setNameOk} 
                SetServerOk:{setServerOk}
            """)
            return -1
    
    async def wait_decodeContent(self)->str:
        """
        等待接收数据
        """
        logging.info("@Srv:\t等待接收数据:")
        respHex = await self._wait_response()
        respStr = respHex.decode('ascii')
        return respStr

    async def send_EncodeData(self,data:str):
        """
        发送数据
        """
        dataHex = data.encode('ascii').hex()
        sendOk = await self.send_command(f"AT+SSEND={CIL_NAME},{dataHex}")
        return sendOk

    async def closeServer(self):
        if self.isStart:
            self.isStart = False
            await self.send_command("AT+SSERVER=0")
            await self.close_connection()
            logging.info("@Srv:\tServer关闭成功")
        else:
            logging.error("@Srv:\tServer未启动,无需关闭")
