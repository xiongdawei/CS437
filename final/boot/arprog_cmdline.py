import sys
sys.path.insert(0,r'./')
from arprog import BootLdr
#import ftdi
import argparse
parser = argparse.ArgumentParser(description='AutoRadar Programmer 1.1.0.0')

parser.add_argument('-p', '--port'      , dest='comm_port'          , type=str ,required=True,  help='The uart com port to be used for communicating with the RadarLink(TM) Device')
parser.add_argument('-c', '--connect'   , dest='connect'            , action='store_true',      help='Run the connect sequance process')
parser.add_argument('-d', '--disconnect', dest='disconnect'         , action='store_true',      help='Disconnect from the device')
parser.add_argument('-t', '--target'    , dest='target_image_name'  , choices=['BSS_BUILD' , 'CALIB_DATA', 'CONFIG_INFO','MSS_BUILD','META_IMAGE1','META_IMAGE2','META_IMAGE3','META_IMAGE4'], help='Select the target image name')
parser.add_argument('-e', '--erase'     , dest='erase'              , action='store_true',      help='Erase file from NVMEM storage')
parser.add_argument('-f', '--file'      , dest='source_file'        , help='Source file name to be written into a file on a NVMEM storage')
parser.add_argument('-fr','--format'    , dest='format'             , action='store_true',      help='Format NVMEM storage')
parser.add_argument('-s', '--storage'   , dest='storage'            , choices=('SFLASH', 'SRAM'), help='Storage Type')
parser.add_argument('-mx','--max'       , dest='maxsize'            , type=int,      help='max size of target image')
parser.add_argument('-b', '--batch'     , dest='batchfile'          , type=str ,
                    help='Comma delimited batch file for downloading and activating set of files and activities. Each line in this file should have one of the following structures:1)source file name,target image name, storage name  2)FORMAT,storage name')

args = parser.parse_args()

TempArray = [0] * 163 * 1024 # limiting app image size till 165kb
RawData = ''.join(str(x) for x in TempArray)
max_size = args.maxsize

if(args.target_image_name == None):
    args.target_image_name = "META_IMAGE1"
    print("Meta Image not specified, using "+ args.target_image_name)
batch_file = args.batchfile
comm_port = args.comm_port
ldr = BootLdr(comm_port)
if (None != max_size):
    ldr.SetAppMaxSize(args.maxsize)

if (None != batch_file):
    #process batch
    f = open("codes.txt","w")
    f.write("")
    f.close()
    f = open("batchstatus.txt","w")
    f.write("FAIL\n")
    f.write("Error may be due to not exiting the last function\n")
    f.close()
    ldr.connect(30000,comm_port)
    i = 0
    print ("process batch")
    batchSrc = tuple(open(batch_file,"r"))
    for line in batchSrc:
        i += 1
        vals = line.split(',')
        print ("File %s--"%batch_file)
        #check if download command
        if (3 == len(vals)):
            filename = vals[0].strip()
            target = vals[1].strip()
            storage = vals[2].strip()
            print ("Execute Line %d - Download %s (%s) Storage(%s)"%(i,target,filename,storage))
            ldr.download_file(filename, target,0,0, storage)
        else:
            #check if format command
            if ((2 == len(vals)) and ('FORMAT' == vals[0].strip())):
                storage = vals[1].strip()
                print ("Execute Line %d - Format %s"%(i,storage))
                ldr.erase_storage(storage)
            else:
                #unrecognized command
                print ("Line %d droped!"%(i))

    ldr.disconnect()
    f = open("batchstatus.txt","w")
    f.write("SUCCESS")
    f.close()

else:
    #parse other options
    #connect
    if (True == args.connect):
        ldr.connect(30000,comm_port)
        #ldr.GetVersion()
    else:
        #ldr.skip_connect()
        ldr.connect(30000,comm_port)

    #format storage
    if (True == args.format):
        ldr.erase_storage('SFLASH')

    #erase file
    if (True == args.erase):
        ldr.EraseFile(args.target_image_name)

    #write file
    if (None != args.source_file and None != args.storage):
           ldr.download_file(args.source_file, args.target_image_name, 0,0,args.storage)

    #disconnect
    if (True == args.disconnect):
        ldr.disconnect()

del ldr
