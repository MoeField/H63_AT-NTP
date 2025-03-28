import asyncio
import aioserial
from typing import Optional
import logging

"""
# AT 命令语法
前缀 AT 或 at 必须加在每个命令行的开头。输入<CR>将终止命令行。通常，命令后面跟随形式为
<CR><LF><response><CR><LF>的响应。在本文档中，仅示出响应，省略<CR><LF>。

# AT 命令响应
当 AT 命令处理器处理完一条命令后，将响应 OK、ERROR ，表示已经准备接收新命令。
在返回最终的 OK, ERROR 之前，会发送请求的响应消息。
AT 命令响应的格式为：
<CR><LF>+CMD1: <parameters><CR><LF>
<CR><LF>OK<CR><LF>
或者
<CR><LF><parameters><CR><LF>
<CR><LF>OK<CR><LF>
"""

END_OF_COMMAND = b'\r\n'
END_OF_RESPONSE = b'\r\n'
OK_RESPONSE = b'OK\r\n'
ERROR_RESPONSE = b'ERROR\r\n'

class H63AtBasic:
    def __init__(self, port:str, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn: Optional[aioserial.AioSerial] = None

    async def open_connection(self)->bool:
        if self.serial_conn and self.serial_conn.is_open:
            logging.info("@Base::串口已经打开")
            return True
        try:
            self.serial_conn = aioserial.AioSerial(port=self.port,baudrate=self.baudrate,timeout=2)
            logging.info(f"@Base::成功打开串口: {self.port}")
            return True
        except Exception as e:
            logging.error(f"@Base::打开串口失败: {str(e)}")
            return False

    async def close_connection(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info(f"@Base::成功关闭串口: {self.port}")
            return True
        else:
            logging.warning("@Base::串口未打开")
            return False

    async def __getAtCmdResponse(self)->(bytes, bool):
        response = bytearray()
        responseLine = bytearray()
        # 读取响应直到遇到结束标记
        while True:
            data = await self.serial_conn.read_async(1)
            if data:
                responseLine += data
                if responseLine.endswith(ERROR_RESPONSE):
                    logging.warning(f"\tERROR响应,\t{response}")
                    return response, False

                if responseLine.endswith(OK_RESPONSE):
                    logging.info(f"\tOK响应,\t{response}")
                    return response, True

                if responseLine.endswith(END_OF_RESPONSE):
                    response += responseLine[:-len(END_OF_RESPONSE)]+b';'
                    responseLine = bytearray()

                elif len(responseLine) > 128:
                    responseLine = responseLine[:-1]
                    return response, False


    async def send_command(self,command:str)->(bytes,bool):
        logging.info(f"\n@Base::发送命令:\t{command}")
        if not self.serial_conn or not self.serial_conn.is_open:
            raise ConnectionError("@Base::串口未打开")
        try:
            command_bytes = command.encode('ascii')
            await self.serial_conn.write_async(command_bytes + END_OF_COMMAND)
            #logging.info(f"发送命令: {command}",end='\t\t')
            response = await self.__getAtCmdResponse()
            #logging.info(f"响应: {response}")
            return response
        except Exception as e:
            #logging.info(f"发送命令失败: {str(e)}")
            return (b'', False)
    
    async def _wait_response(self)->bytes:
        """
        接受其他模块的响应
        +SRECVDATA:<name>,<data>
        """
        data = b''
        
        while True:
            buff = await self.serial_conn.read_async(1)
            if buff:
                data += buff
                if data.endswith(END_OF_RESPONSE):
                    data = data[:-len(END_OF_RESPONSE)]
                    break
        while True:
            buff = await self.serial_conn.read_async(1)
            if buff:
                data += buff
                if data.endswith(END_OF_RESPONSE):
                    data = data[:-len(END_OF_RESPONSE)]
                    break

        logging.info(f"@basic:\t接收到数据: {data}")
        return data
