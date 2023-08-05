__author__ = 'babak'


from struct import *
import math
import numpy as np
from boto.s3.connection import S3Connection

class nifti:
    sizeof_hdr = 0
    binaryData = ""
    dim        = []
    DT_NONE   = 0
    DT_BINARY = 1
    NIFTI_TYPE_UINT8 = 2
    NIFTI_TYPE_INT16 = 4
    NIFTI_TYPE_INT32 = 8
    NIFTI_TYPE_FLOAT32 = 16
    NIFTI_TYPE_COMPLEX64 = 32
    NIFTI_TYPE_FLOAT64 = 64
    NIFTI_TYPE_RGB24 = 128
    DT_ALL = 255
    NIFTI_TYPE_INT8 = 256
    NIFTI_TYPE_UINT16 = 512
    NIFTI_TYPE_UINT32 = 768
    NIFTI_TYPE_INT64 = 1024
    NIFTI_TYPE_UINT64 = 1280
    NIFTI_TYPE_FLOAT128 = 1536
    NIFTI_TYPE_COMPLEX128 = 1792
    NIFTI_TYPE_COMPLEX256 = 2048

    bytesPerVoxel = {DT_NONE:0,DT_BINARY:-1,NIFTI_TYPE_UINT8:1,
                     NIFTI_TYPE_INT16:2,NIFTI_TYPE_INT32:4,
                     NIFTI_TYPE_FLOAT32:4,NIFTI_TYPE_COMPLEX64:8,
                     NIFTI_TYPE_FLOAT64:8,NIFTI_TYPE_RGB24:3,
                     DT_ALL:0,NIFTI_TYPE_INT8:1,NIFTI_TYPE_UINT16:2,
                     NIFTI_TYPE_UINT32:4,NIFTI_TYPE_INT64:8,
                     NIFTI_TYPE_UINT64:8,NIFTI_TYPE_FLOAT128:16,
                     NIFTI_TYPE_COMPLEX128:16,NIFTI_TYPE_COMPLEX256:32}

    def __init__(self,filename="",awsKey="",awsSec=""):
        self.dim = []
        self.binaryData = ""
        self.sizeof_hdr = 0
        self.TDIM = 0
        if (filename[0:6]=="s3n://"):
            if len(awsKey)==0 or len(awsSec)==0:
                (awsKey,awsSec) = self.readKeyFromFile("/dataset/amazonKey.txt")

            conn = S3Connection(awsKey, awsSec)
            bucketName = filename[6:].split("/")[0]
            bucket = conn.get_bucket(bucketName)
            key = bucket.get_key(filename[6+len(bucketName):])
            self.binaryData = key.get_contents_as_string()
        else:
            with open(filename,"r") as f:
                self.binaryData = f.read()

    def readKeyFromFile(self,amazonKeyFile):
        awsAccessKeyId= ""
        awsSecretAccessKey = ""
        with open(amazonKeyFile,"r") as f:
            for line in f.readlines():
                if line.find("awsAccessKeyId=")>=0:
                    awsAccessKeyId = line[15:].rstrip()
                if line.find("awsSecretAccessKey=")>=0:
                    awsSecretAccessKey = line[19:].rstrip()

        return (awsAccessKeyId,awsSecretAccessKey)

    def unpackDimInfo(self, b):
        s = []
        s.append(int(b) & 3)
        s.append((int(b)>>2) & 3)
        s.append((int(b)>>4) & 3)
        return s

    def unpackUnits(self, b):
        s = []
        s.append(int(b) & 007)
        s.append(int(b) & 070)
        return s

    def readHeader(self, str=""):
        if (len(str)==0):
            str = self.binaryData
        newstr = str[0:40] # skip 40 bytes
        s      = unpack("h",newstr[0:2])[0]
        if ((s<1) or (s>7)):
            big_endian = False
            big_endian_char = "<"
        else:
            big_endian = True
            big_endian_char = ">"

        newstr     = str
        self.sizeof_hdr = unpack(big_endian_char+"i",newstr[0:4])[0]
        newstr = newstr[4:]

        data_type_string         = newstr[0:10]
        newstr 					 = newstr[10:]

        db_name                  = newstr[0:18]
        newstr 					 = newstr[18:]

        self.extents					 = unpack(big_endian_char+"i",newstr[0:4])[0]
        newstr 					 = newstr[4:]

        self.session_error			 = unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr 					 = newstr[2:]

        self.regular                  = unpack("B",newstr[0])[0]
        newstr 					 = newstr[1:]

        ss 						 = self.unpackDimInfo(unpack("B",newstr[0])[0])
        newstr					 = newstr[1:]
        self.freq_dim  				 = ss[0]
        self.phase_dim 				 = ss[1]
        self.slice_dim 				 = ss[2]

        for i in range(0,8):
            self.dim.append(unpack(big_endian_char+"h",newstr[0:2])[0])
            newstr = newstr[2:]

        if (self.dim[0] > 0):
            self.XDIM = self.dim[1]
        if (self.dim[0] > 1):
            self.YDIM = self.dim[2]
        if (self.dim[0] > 2):
            self.ZDIM = self.dim[3]
        if (self.dim[0] > 3):
            self.TDIM = self.dim[4]

        self.intent = []
        for i in range(0,3):
            self.intent.append(unpack(big_endian_char+"f",newstr[0:4]))
            newstr = newstr[4:]

        self.intent_code = unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr      = newstr[2:]

        self.datatype    = unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr      = newstr[2:]

        self.bitpix  	= unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr      = newstr[2:]

        self.slice_start = unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr      = newstr[2:]

        self.pixdim = []
        for i in range(0,8):
            self.pixdim.append(unpack(big_endian_char+"f",newstr[0:4])[0])
            newstr      = newstr[4:]

        self.qfac       = math.floor(self.pixdim[0])

        self.vox_offset = unpack(big_endian_char+"f",newstr[0:4])[0]
        newstr     = newstr[4:]

        self.scl_slope  = unpack(big_endian_char+"f",newstr[0:4])[0]
        newstr     = newstr[4:]

        self.scl_inter  = unpack(big_endian_char+"f",newstr[0:4])[0]
        newstr     = newstr[4:]

        self.slice_end  = unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr     = newstr[2:]

        self.slice_code = unpack("B",newstr[0])[0]
        newstr     = newstr[1:]


        self.xyzt_units = unpack("B",newstr[0])[0]
        newstr     = newstr[1:]
        ss         = self.unpackUnits(self.xyzt_units)
        self.xyz_unit_code = ss[0];
        self.t_unit_code   = ss[1];

        self.cal_max    = unpack(big_endian_char+"f",newstr[0:4])[0]
        newstr     = newstr[4:]

        self.cal_min    = unpack(big_endian_char+"f",newstr[0:4])[0]
        newstr     = newstr[4:]

        self.slice_duration = unpack(big_endian_char+"f",newstr[0:4])[0]
        newstr         = newstr[4:]

        self.toffset    = unpack(big_endian_char+"f",newstr[0:4])[0]
        newstr     = newstr[4:]

        self.glmax = unpack(big_endian_char+"i",newstr[0:4])[0]
        newstr     = newstr[4:]

        self.glmin = unpack(big_endian_char+"i",newstr[0:4])[0]
        newstr     = newstr[4:]


        self.descrip             = newstr[0:80]
        newstr 			    = newstr[80:]

        self.aux_file            = newstr[0:24]
        newstr 			    = newstr[24:]

        self.qform_code = unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr     = newstr[2:]

        self.sform_code = unpack(big_endian_char+"h",newstr[0:2])[0]
        newstr     = newstr[2:]

        self.quatern    = []
        for i in range(0,3):
            self.quatern.append(unpack(big_endian_char+"f",newstr[0:4])[0])
            newstr     = newstr[4:]

        self.qoffset   = []
        for i in range(0,3):
            self.qoffset.append(unpack(big_endian_char+"f",newstr[0:4])[0])
            newstr     = newstr[4:]

        self.srow_x    = []
        for i in range(0,4):
            self.srow_x.append(unpack(big_endian_char+"f",newstr[0:4])[0])
            newstr     = newstr[4:]

        self.srow_y    = []
        for i in range(0,4):
            self.srow_y.append(unpack(big_endian_char+"f",newstr[0:4])[0])
            newstr     = newstr[4:]

        self.srow_z    = []
        for i in range(0,4):
            self.srow_z.append(unpack(big_endian_char+"f",newstr[0:4])[0])
            newstr     = newstr[4:]


        self.intent_name = newstr[0:16]
        newstr      = newstr[16:]

        self.magic 		= newstr[0:4]
        newstr		= newstr[4:]

    def readBlob(self, str=binaryData):
        ZZZ = self.ZDIM
        if (self.dim[0] == 2):
            ZZZ = 1
        TTT = self.TDIM
        if (self.dim[0] < 4):
            TTT = 1
        ttt = 0
        blob_size = TTT * self.XDIM * self.YDIM * ZZZ * self.bytesPerVoxel[self.datatype]
        skip_head =  self.vox_offset
        skip_data = (ttt * blob_size)
        b = str[int(skip_head + skip_data):int(skip_head + skip_data+blob_size)]
        return b

    def readData(self,str=""):
        if (len(str)==0):
            str = self.binaryData

        newstr = self.readBlob(str)
        ZZZ = self.ZDIM
        if (self.dim[0] == 2):
            ZZZ = 1
        TTT = self.TDIM
        if (self.dim[0] < 4):
            TTT = 1
        data = np.zeros((TTT,ZZZ*self.YDIM*self.XDIM))

        if (self.datatype==self.NIFTI_TYPE_INT8):
            tpcode = "b"
        if (self.datatype==self.NIFTI_TYPE_UINT8):
            tpcode = "B"
        if (self.datatype==self.NIFTI_TYPE_INT16):
            tpcode = "h"
        if (self.datatype==self.NIFTI_TYPE_UINT16):
            tpcode = "H"
        if (self.datatype==self.NIFTI_TYPE_INT32):
            tpcode = "i"
        if (self.datatype==self.NIFTI_TYPE_UINT32):
            tpcode = "I"
        if (self.datatype==self.NIFTI_TYPE_INT64):
            tpcode = "q"
        if (self.datatype==self.NIFTI_TYPE_UINT64):
            tpcode = "Q"
        if (self.datatype==self.NIFTI_TYPE_FLOAT32):
            tpcode = "f"
        if (self.datatype==self.NIFTI_TYPE_FLOAT64):
            tpcode = "d"

        numbytes = self.bytesPerVoxel[self.datatype]

        data = np.array(unpack(tpcode*ZZZ*self.YDIM*self.XDIM*TTT,newstr[0:numbytes*ZZZ*self.YDIM*self.XDIM*TTT]))

        if (self.scl_slope!=0):
            data = data * self.scl_slope + self.scl_inter
        data.shape = (TTT,ZZZ*self.YDIM*self.XDIM)
        self.binaryData = ""
        return data


def normalize(scan):
    mn     = np.mean(scan,axis=0)
    out    = scan - mn
    nrm    = np.sqrt(np.sum(np.power(out,2),axis=0))
    out    = out/nrm
    return out

# Time x Voxel
def globalsignalregression(scan):
    sz   = scan.shape
    gs   = np.matrix(np.mean(scan,axis=1))
    Pn   = np.eye(sz[0]) - gs.T*np.linalg.inv(gs*gs.T)*gs
    out  = Pn*scan
    return out

# Time x Voxel
def parcellate(d,p):
    (nt,nv)  = d.shape
    regions  = np.sort(list(set(p)-set([0])))
    out      = np.zeros((nt,regions.shape[0]))
    rcounter = 0
    for r in regions:
        temp = d[:,np.where(p==r)[0]].mean(axis=1)
        temp.shape = (nt)
        out[:,rcounter] = temp
        rcounter        = rcounter + 1
    return out

def readNiftiFile(filename,awsAccessKeyId,awsSecretAccessKey):
    nii    = nifti(filename,awsAccessKeyId,awsSecretAccessKey)
    nii.readHeader()
    dataRaw      = nii.readData()
    return dataRaw

def preProcess(data,parcellation):
    dataPrep       = globalsignalregression(data)
    dataParcel     = parcellate(dataPrep,parcellation)
    dataNormalized = normalize(dataParcel)
    return dataNormalized

