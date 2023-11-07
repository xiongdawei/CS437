import string
import struct
from idna import valid_contextj
import serial
import subprocess
import time
import os
#import d2xx
#import binascii


DEFUALT_SERIAL_COM_PORT             = 52
DEFUALT_SERIAL_BAUD_RATE            = 115200
#DEFUALT_SERIAL_BAUD_RATE            = 19200*2
DEFAULT_CHUNK_SIZE                  = 240
MAX_FILE_SIZE                       = 1024*1024
MAX_APP_FILE_SIZE                   = 166912

Files = {
"BSS_BUILD"                : struct.pack(">I",0),
"CALIB_DATA"               : struct.pack(">I",1),
"CONFIG_INFO"              : struct.pack(">I",2),
"MSS_BUILD"                : struct.pack(">I",3),
"META_IMAGE1"              : struct.pack(">I",4),
"META_IMAGE2"              : struct.pack(">I",5),
"META_IMAGE3"              : struct.pack(">I",6),
"META_IMAGE4"              : struct.pack(">I",7)
}


Storages = {
"SDRAM"     : struct.pack(">I", 0),
"FLASH"     : struct.pack(">I", 1),
"SFLASH"    : struct.pack(">I", 2),
"EEPROM"    : struct.pack(">I", 3),
"SRAM"      : struct.pack(">I", 4)
}

AR_BOOTLDR_OPCODE_ACK               = struct.pack("B", 0xCC)
AR_BOOTLDR_OPCODE_NACK              = struct.pack("B", 0x33)
AR_BOOTLDR_OPCODE_PING              = struct.pack("B", 0x20)
AR_BOOTLDR_OPCODE_START_DOWNLOAD    = struct.pack("B", 0x21)
AR_BOOTLDR_OPCODE_FILE_CLOSE        = struct.pack("B", 0x22)
AR_BOOTLDR_OPCODE_GET_LAST_STATUS   = struct.pack("B", 0x23)
AR_BOOTLDR_OPCODE_SEND_DATA         = struct.pack("B", 0x24)
AR_BOOTLDR_OPCODE_SEND_DATA_RAM     = struct.pack("B", 0x26)
AR_BOOTLDR_OPCODE_DISCONNECT        = struct.pack("B", 0x27)
AR_BOOTLDR_OPCODE_ERASE             = struct.pack("B", 0x28)
AR_BOOTLDR_OPCODE_FILE_ERASE        = struct.pack("B", 0x2E)
AR_BOOTLDR_OPCODE_GET_VERSION_INFO  = struct.pack("B", 0x2F)

AR_BOOTLDR_SYNC_PATTERN             = struct.pack("B", 0xAA)

AR_BOOTLDR_OPCODE_RET_SUCCESS             = struct.pack("B", 0x40)
AR_BOOTLDR_OPCODE_RET_ACCESS_IN_PROGRESS  = struct.pack("B", 0x4B)
# to specify different device varients
AR_DEVICE_IS_AR12XX               = struct.pack("B", 0x00)
AR_DEVICE_IS_AR14XX                = struct.pack("B", 0x01)
AR_DEVICE_IS_AR16XX                 = struct.pack("B", 0x03)
AR_DEVICE_IS_AR17XX                = struct.pack("B", 0x10)


TRACE_LEVEL_ERROR = 1
TRACE_LEVEL_ACTIVITY = 2
TRACE_LEVEL_INFO = 3
TRACE_LEVEL_DEBUG = 4

ROM_VERSION = 1.0
RUN_COUNT = 0
IGNORE_BYTE_CONDITION = False   # to Ignore reading 2 bytes in some condition; as GetFileInfo()
IS_FILE_ALLOCATED     = False   # to check if SFLASH file allocation done or not
CHIP_VARIANT          = "CC"

SCK_BIT = 0x01
DO_BIT = 0x02
DI_BIT = 0x04
CS_BIT = 0x08

SOP0_BIT = 0x04
SOP1_BIT = 0x08
SOP2_BIT = 0x10

#SOP_VALUE = SOP0_BIT | SOP2_BIT

NRESET_BIT = 0x64
NRESET_BIT_VALUE = 0x64

PAYLOAD_MAX_LENGTH = 0x10000 # 16 bits max

AR_BOARD_CONTROL_SOP_BITS              = struct.pack("B", 0x14)
AR_BOARD_CONTROL_RESET_BITS              = struct.pack("B", 0x00)
AR_BOARD_CONTROL_POWER_UP              = struct.pack("B", 0x40)

AR_BOARD_CONTROL_PORTC_CONFIG = 0xDA
AR_BOARD_CONTROL_PORTD_CONFIG = 0x1F

class BootLdr:

    def __init__(self, com_port, trace_level =3):
        self.com_port = com_port
        self.baudrate = DEFUALT_SERIAL_BAUD_RATE
        self.chunksize = DEFAULT_CHUNK_SIZE
        self.FileList = Files
        self.StorageList = Storages
        self.trace_level = trace_level
        self.IGNORE_BYTE_CONDITION = False
        self.IS_FILE_ALLOCATED = False
        self.MAX_APP_FILE_SIZE = MAX_APP_FILE_SIZE
        self.CHIP_VARIANT = CHIP_VARIANT
        self.ROM_VERSION = ROM_VERSION
        #Paylaod increased to 8
        self.cmdStatusSize = 8
        self.connected = False


    def configureSOP(self, description):
        """Configure the FTDI interface as a SPI master"""
        self._trace_msg(TRACE_LEVEL_ERROR,"--- Enter SOP Write!!!")
        d = d2xx.listDevices(d2xx.OPEN_BY_DESCRIPTION)
        h = d2xx.open(3)
        h.setBitMode(0x0,0x0)
        h.setBitMode(AR_BOARD_CONTROL_PORTD_CONFIG, 0x1)
        h.write(AR_BOARD_CONTROL_SOP_BITS)
        self._trace_msg(TRACE_LEVEL_ERROR,"--- SOP Write Done!!!")
        h.close()

    def configureReset(self, description):
        """Configure the FTDI interface as a SPI master"""
        self._trace_msg(TRACE_LEVEL_ERROR,"--- Enter nReset Write!!!")
        d = d2xx.listDevices(d2xx.OPEN_BY_DESCRIPTION)
        h = d2xx.open(2)
        h.setBitMode(0x0,0x0)
        h.setBitMode(AR_BOARD_CONTROL_PORTC_CONFIG, 0x1)
        h.write(AR_BOARD_CONTROL_RESET_BITS)
        time.sleep(0.100)
        h.write(AR_BOARD_CONTROL_POWER_UP)
        self._trace_msg(TRACE_LEVEL_ERROR,"--- nReset Write Done!!!")
        h.close()

    def _trace_msg(self,level:int,str:string):
        if (level <= self.trace_level):
            print ("%s"%(str))

    def _comm_open(self):
        f = open("batchstatus.txt",'a')
        f.write("[Enter]: Opening Comm port: " + self.com_port + '\n')
        f.close()
        if(self._is_connected()):
            f = open("batchstatus.txt",'a')
            f.write("[Exit]: Opening Comm port: " + self.com_port + '\n')
            f.close()
            return True
        self.comm = serial.Serial(port=str(self.com_port), baudrate=self.baudrate)
        if self.comm.isOpen():
            self.comm.reset_input_buffer()
            self.connected = True
            self._trace_msg(TRACE_LEVEL_INFO,"INFO : Port Opened")
            f = open("batchstatus.txt",'a')
            f.write("[Exit]: Opening Comm port" + self.com_port)
            f.close()
            return True
        else:
            self._trace_msg(TRACE_LEVEL_ERROR,"ERROR: Error While Opening Port!!!")
            return False

    def _comm_close(self):
        if(self._is_connected()):
            self.comm.close()
            self.connected = False
            self.comm = None

    def _is_connected(self):
        return self.connected

    def _send_packet(self,data:bytes):
        checksum = 0
        for b in data:
            checksum += b
        msgSize = len(data)+2
        sMsgSize = struct.pack(">H",msgSize)
        sChecksum = struct.pack("B",checksum & 0xff)
        self.comm.write(AR_BOOTLDR_SYNC_PATTERN)
        self.comm.write(sMsgSize)
        self.comm.write(sChecksum)
        self.comm.write(data)

    def _receive_packet(self, Length:int):
        #if not self.IGNORE_BYTE_CONDITION:
        #    Header = self.comm.read(2)
        Header = self.comm.read(3)
        #self._trace_msg(TRACE_LEVEL_ACTIVITY, "Header" + binascii.hexlify(Header))
        PacketLength , CheckSum  = struct.unpack(">HB", Header)
        PacketLength -= 2 # Compensate for the header
        if (Length != PacketLength):
            self._trace_msg(TRACE_LEVEL_DEBUG, "Requested length={:d}, actual={:d}".format(Length, PacketLength))
            raise Exception("Error, Mismatch between requested and actual packet length: act {:d}, req {:d}".format(PacketLength, Length))
        Payload = self.comm.read(PacketLength)
        if (len(Payload) != Length):
            raise Exception("Error, Timeout while receiving packet's payload")
        #self.comm.write(AR_BOOTLDR_OPCODE_ACK) # Ack the packet
        CalculatedCheckSum=0
        for byte in Payload:
            CalculatedCheckSum += byte
        CalculatedCheckSum &= 0xFF
        if (CalculatedCheckSum != CheckSum):
            self._trace_msg(TRACE_LEVEL_ERROR, "ERROR: Calculated: 0x{:x}.  Received: 0x{:x}".format(CalculatedCheckSum, CheckSum))
            raise Exception("Checksum error on received packet")
        return Payload

    def _read_ack(self):
            self._trace_msg(TRACE_LEVEL_DEBUG, "wait for ack")
            length = self.comm.read(2)
            chksum = self.comm.read(1)
            self.comm.read(1) # 0x00
            a = self.comm.read(1)
            #self._trace_msg(TRACE_LEVEL_ACTIVITY, "Length" + binascii.hexlify(length))
            #self._trace_msg(TRACE_LEVEL_ACTIVITY, "chksum" + binascii.hexlify(chksum))
            #self._trace_msg(TRACE_LEVEL_ACTIVITY, "a" + binascii.hexlify(a))
            while (not ((a == AR_BOOTLDR_OPCODE_ACK) or (a == AR_BOOTLDR_OPCODE_NACK))):
                a = self.comm.read(1)
            self._trace_msg(TRACE_LEVEL_DEBUG,"ACK got from device")
            if (a == AR_BOOTLDR_OPCODE_ACK):
                self._trace_msg(TRACE_LEVEL_DEBUG,"receive ack")
                return True
            elif (a == AR_BOOTLDR_OPCODE_NACK):
                self._trace_msg(TRACE_LEVEL_DEBUG,"receive nack")
                return False
            else:
                self._trace_msg(TRACE_LEVEL_ERROR,"ERROR: Received unexpected data!!!!!")
                raise Exception("No ACK")
            return False

    def _send_command(self,data:bytes):
        self._trace_msg(TRACE_LEVEL_DEBUG,"send command")
        self._send_packet(data)
        ackStatus = self._read_ack()
        if(not ackStatus):
            self._send_packet(AR_BOOTLDR_OPCODE_GET_LAST_STATUS)
            #self._trace_msg(TRACE_LEVEL_ACTIVITY, "Cmd Size" + str(self.cmdStatusSize))
            retStatus = self._receive_packet(self.cmdStatusSize)
            value = int.from_bytes(retStatus,"little")
            self._trace_msg(TRACE_LEVEL_ERROR,"Nack Received, Err Code: " + self._get_hex_string(value))
            f = open("codes.txt","a")
            f.write(self._get_hex_string(value))
            f.close()
        return ackStatus

    def _send_start_download(self,file_id,file_size,max_size,mirror_enabled,storage):
        self._trace_msg(TRACE_LEVEL_ERROR,"INFO: Send start download command")
        data = AR_BOOTLDR_OPCODE_START_DOWNLOAD + \
            struct.pack(">I",file_size) + Storages[storage] + \
            Files[file_id] + struct.pack(">I",mirror_enabled)
        self._send_command(data)
        return True

    def _send_file_close(self,file_id):
        self._trace_msg(TRACE_LEVEL_DEBUG,"send file close command")
        data = AR_BOOTLDR_OPCODE_FILE_CLOSE + \
            Files[file_id]
        self._send_command(data)
        return True

    def _get_hex_string(self,value):
        hexString = hex(value)
        hexString = hexString[2:]
        while(len(hexString) < 16):
            hexString = "0" + hexString
        return "0x" + hexString
    
    def _send_sram_file_close(self , file_id    ):
        self._trace_msg(TRACE_LEVEL_DEBUG,"Send SRAM file close command")
        data = AR_BOOTLDR_OPCODE_FILE_CLOSE + \
            Files[file_id]
        self._send_packet(data)
        ackStatus = self._read_ack()
        #self._send_packet(AWR_BOOTLDR_OPCODE_GET_LAST_STATUS)
        retStatus = self._receive_packet(8)
        value = int.from_bytes(retStatus,"little")
        if(value != 0):
            self._trace_msg(TRACE_LEVEL_INFO, "MetaImage Download Err Code: " + self._get_hex_string(value))
            f = open("codes.txt","a")
            f.write(self._get_hex_string(value))
            f.close()
        else:
            self._trace_msg(TRACE_LEVEL_INFO, "SRAM Download Success")
        self._trace_msg(TRACE_LEVEL_DEBUG,"Send SRAM file close command")
        return ackStatus 

    def _send_chunk(self,buff:bytes,bufflen:int):
        self._trace_msg(TRACE_LEVEL_DEBUG,"send chunk")
        data = AR_BOOTLDR_OPCODE_SEND_DATA + buff
        return self._send_command(data)

    def _send_chunkRAM(self,buff:bytes,bufflen:int):
        self._trace_msg(TRACE_LEVEL_DEBUG,"send chunk")
        data = AR_BOOTLDR_OPCODE_SEND_DATA_RAM + buff
        return self._send_command(data)

    def _check_operation_status(self):
        self._trace_msg(TRACE_LEVEL_DEBUG,"Status request")
        data = AR_BOOTLDR_OPCODE_GET_LAST_STATUS
        RetCode = AR_BOOTLDR_OPCODE_RET_ACCESS_IN_PROGRESS
        while (AR_BOOTLDR_OPCODE_RET_ACCESS_IN_PROGRESS == RetCode):
            self._send_packet(data)
            if (False == self._read_ack()):
                return False
            #Response payload size increased to 8
            Response = self.comm.read(11)
            self.comm.write(AR_BOOTLDR_OPCODE_ACK)
            RetCode = Response[3]
        if (AR_BOOTLDR_OPCODE_RET_SUCCESS == RetCode):
            return True
        else:
            return False


    #******************* APIs *******************

    def connect_with_reset(self,timeout,com_port,reset_command):
        #self._trace_msg(TRACE_LEVEL_ACTIVITY,"Configure SOP")
        #self.configureSOP('AR-MB-EVM-1_FD01')
        #self._trace_msg(TRACE_LEVEL_ACTIVITY,"Configure NRESET")
        #self.configureReset('AR-MB-EVM-1_FD01')
        self._trace_msg(TRACE_LEVEL_ACTIVITY,"connect to device")
        self.__init__(com_port, trace_level=3)
        global RUN_COUNT
        if (self._comm_open()):
            self._trace_msg(TRACE_LEVEL_INFO,"set break signal")
            self.comm.timeout = timeout # For this command only since port is closed @ the end
            self.comm.break_condition = True
            time.sleep(0.100)
            if (reset_command != ""):
                subprocess.call(reset_command)
            elif(RUN_COUNT ==0):
                self._trace_msg(TRACE_LEVEL_ACTIVITY,"--- please restart the device ---")
                RUN_COUNT += 1
            if (self._read_ack()):
                self._trace_msg(TRACE_LEVEL_ACTIVITY,"connection succeeded")
                self.comm.break_condition = False
                #self._trace_msg(TRACE_LEVEL_INFO,"get storage list")
                #self._send_packet(AR_BOOTLDR_OPCODE_GET_STORAGE_LIST)
                #if (self._read_ack()):
                 #   self.storage_list = self.comm.read(1)
                  #  self._trace_msg(TRACE_LEVEL_INFO,"receive storage list")
                #else:
                  #  self.storage_list = 0
                   # self._trace_msg(TRACE_LEVEL_ERROR,"--- error during get stoarge list!!!")
            else:
                self._trace_msg(TRACE_LEVEL_ACTIVITY,"connection refused")
            self._comm_close()
            self._trace_msg(TRACE_LEVEL_DEBUG,"exit bootldr connect")
        else:
            self._trace_msg(TRACE_LEVEL_ERROR,"ERROR: Unable to estalish connection!")

    def skip_connect(self):
        self.connected = True

    def connect(self,timeout, com_port):
        self._trace_msg(TRACE_LEVEL_ACTIVITY,"Connecting Com Port....")
        self.connect_with_reset(timeout,com_port,"")

    def disconnect(self):
        self._trace_msg(TRACE_LEVEL_ACTIVITY,"disconnecting device....")
        self._comm_close()
        self._trace_msg(TRACE_LEVEL_DEBUG,"exit disconnect")

    def PingDevice(self):
        self._trace_msg(TRACE_LEVEL_ACTIVITY,"Pinging device....")
        self._comm_open()
        self._send_packet(AR_BOOTLDR_OPCODE_PING)
        Status = self._read_ack()
        self._comm_close()
        return Status


    def GetVersion(self):
        self._trace_msg(TRACE_LEVEL_ACTIVITY,"Reading version info")
        self._comm_open()
        self._send_packet(AR_BOOTLDR_OPCODE_GET_VERSION_INFO)
        Status = self._read_ack()
        try:
            if (False == Status):
                RetValue =  False
                raise Exception("No ack")
            Length = self.comm.read(2)
            self.comm.read(1) # Read the checksum and throw it
            #RxLength = struct.unpack(">H", Length)[0] - 2
            #if (RxLength != 28):
            #    raise Exception("Error, version response should be 28 bytes, device is sending {:d}".format(RxLength))
            VersionData = self.comm.read(12)
            #print ("getversion "+"".join(chr(Length))+"".join(chr(VersionData[16])))
            #self.comm.write(AR_BOOTLDR_OPCODE_ACK) # Ack the version packet
            RetValue = VersionData
        except:
            pass
        finally:
            self._comm_close()
        return RetValue



    def download_file(self,filename,file_id,mirror_enabled,max_size,storage):
        f = open("batchstatus.txt",'a')
        f.write("[Enter]: Download file\n" + filename + '\n' + file_id + '\n' + storage + '\n' )
        f.close()
        fSize = os.path.getsize(filename)
        #Status payload is 8
        self.cmdStatusSize = 8
        status = True
        self._trace_msg(TRACE_LEVEL_ACTIVITY,"downloading [%s] size [%d]"%(file_id,fSize))
        if (fSize>0) and (fSize < MAX_FILE_SIZE):
            if (max_size < fSize):
                max_size = fSize
            fSrc = open(filename,"rb")
            if (self._comm_open()):
                if (self._send_start_download(file_id,fSize,max_size,mirror_enabled,storage)):
                    offset = 0
                    while (offset < fSize):
                        buff = fSrc.read(self.chunksize)
                        bufflen = len(buff)
                        if(storage == "SRAM"):
                            if (not self._send_chunkRAM(buff,bufflen)):
                                self._trace_msg(TRACE_LEVEL_ERROR,"NACK Received while Download")
                                status = False
                                break
                        else:
                            if (not self._send_chunk(buff,bufflen)):
                                self._trace_msg(TRACE_LEVEL_ERROR,"NACK Received while Download")
                                status = False
                                break
                        offset += bufflen
                        progress = int(40.0 * float(offset)/float(fSize))
                        print ("[" + progress*"=" + ">" + (40 - progress)*" " + "]" + "\r",end="")
                print()
                if(storage   == "SRAM" and status):
                    self._send_sram_file_close(file_id)
                elif(status):
                    self._send_file_close(file_id)
                self._comm_close()
            else:
                self._trace_msg(TRACE_LEVEL_ERROR,"ERROR: Fail during connecting, File not Uploaded!")
            fSrc.close()
        else:
            self._trace_msg(TRACE_LEVEL_ERROR,"ERROR: Invalid file size")
        f = open("batchstatus.txt",'a')
        f.write("[Exit]: Download file\n" + filename + '\n' + file_id + '\n' + storage + '\n' )
        f.close()
        self._trace_msg(TRACE_LEVEL_DEBUG,"exit download file")

    def erase_storage(self,storage,location_offset=0,capacity=0):
        f = open("batchstatus.txt",'a')
        f.write("[Enter]: Format SFLASH\n")
        f.close()
        self._trace_msg(TRACE_LEVEL_ACTIVITY,"erase storage [%s]"%(storage))
        if (self._comm_open()):
            data = AR_BOOTLDR_OPCODE_ERASE + Storages[storage] + \
                struct.pack(">I",location_offset) + struct.pack(">I",capacity)
            self._send_packet(data)
            if (self._read_ack()):
                self._trace_msg(TRACE_LEVEL_INFO,"erase storage ok")
        self._comm_close()
        f = open("batchstatus.txt",'a')
        f.write("[Exit]: Format SFLASH\n")
        f.close()
        self._trace_msg(TRACE_LEVEL_DEBUG,"exit erase storage")

