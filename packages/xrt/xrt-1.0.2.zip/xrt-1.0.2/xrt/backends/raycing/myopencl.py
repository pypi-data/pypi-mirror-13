# -*- coding: utf-8 -*-
r"""
Initialization code of pyopencl.
"""
__author__ = "Konstantin Klementiev, Roman Chernikov"
__date__ = "22 Jan 2016"
import numpy as np
import os
try:
    import pyopencl as cl
    os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'
    isOpenCL = True
except ImportError:
    isOpenCL = False

__dir__ = os.path.dirname(__file__)
_DEBUG = 20


class XRT_CL(object):
    def __init__(self, filename, targetOpenCL='auto', precisionOpenCL='auto'):
        self.cl_filename = filename
        self.lastTargetOpenCL = None
        self.lastPrecisionOpenCL = None
        self.set_cl(targetOpenCL, precisionOpenCL)
        self.cl_is_blocking = False

    def set_cl(self, targetOpenCL='auto', precisionOpenCL='auto'):
        if (targetOpenCL == self.lastTargetOpenCL) and\
                (precisionOpenCL == self.lastPrecisionOpenCL):
            return
        self.lastTargetOpenCL = targetOpenCL
        self.lastPrecisionOpenCL = precisionOpenCL
        if not isOpenCL:
            raise EnvironmentError("pyopencl is not available!")
        else:
            if isinstance(targetOpenCL, (tuple, list)):
                iDevice = []
                targetOpenCL = list(targetOpenCL)
                if isinstance(targetOpenCL[0], int):
                    nPlatform, nDevice = targetOpenCL
                    platform = cl.get_platforms()[nPlatform]
                    iDevice.extend([platform.get_devices()[nDevice]])
                else:
                    for target in targetOpenCL:
                        if isinstance(target, (tuple, list)):
                            target = list(target)
                            if len(target) > 1:
                                nPlatform, nDevice = target
                                platform = cl.get_platforms()[nPlatform]
                                iDevice.extend(
                                    [platform.get_devices()[nDevice]])
                            else:
                                nPlatform = target[0]
                                platform = cl.get_platforms()[nPlatform]
                                iDevice.extend(platform.get_devices())
            elif isinstance(targetOpenCL, int):
                nPlatform = targetOpenCL
                platform = cl.get_platforms()[nPlatform]
                iDevice = platform.get_devices()
            elif isinstance(targetOpenCL, str):
                iDeviceCPU = []
                iDeviceGPU = []
                iDeviceAcc = []
                iDevice = []
                for platform in cl.get_platforms():
                    CPUdevices = []
                    GPUdevices = []
                    AccDevices = []
                    try:  # at old pyopencl versions:
                        CPUdevices =\
                            platform.get_devices(
                                device_type=cl.device_type.CPU)
                        GPUdevices =\
                            platform.get_devices(
                                device_type=cl.device_type.GPU)
                        AccDevices =\
                            platform.get_devices(
                                device_type=cl.device_type.ACCELERATOR)
                    except cl.RuntimeError:
                        pass

                    if len(CPUdevices) > 0:
                        if len(iDeviceCPU) > 0:
                            if CPUdevices[0].vendor == \
                                    CPUdevices[0].platform.vendor:
                                iDeviceCPU = CPUdevices
                        else:
                            iDeviceCPU.extend(CPUdevices)
                    iDeviceGPU.extend(GPUdevices)
                    iDeviceAcc.extend(AccDevices)
                if _DEBUG > 10:
                    print("OpenCL: bulding {0} ...".format(self.cl_filename))
                    print("OpenCL: found {0} CPU{1}".format(
                          len(iDeviceCPU) if len(iDeviceCPU) > 0 else 'none',
                          's' if len(iDeviceCPU) > 1 else ''))
                    print("OpenCL: found {0} GPU{1}".format(
                          len(iDeviceGPU) if len(iDeviceGPU) > 0 else 'none',
                          's' if len(iDeviceGPU) > 1 else ''))
                    print("OpenCL: found {0} other accelerator{1}".format(
                          len(iDeviceAcc) if len(iDeviceAcc) > 0 else 'none',
                          's' if len(iDeviceAcc) > 1 else ''))

                if targetOpenCL.upper().startswith('GPU'):
                    iDevice.extend(iDeviceGPU)
                elif targetOpenCL.upper().startswith('CPU'):
                    iDevice.extend(iDeviceCPU)
                elif targetOpenCL.upper().startswith('ALL'):
                    iDevice.extend(iDeviceGPU)
                    iDevice.extend(iDeviceCPU)
                    iDevice.extend(iDeviceAcc)
                else:  # auto
                    if len(iDeviceGPU) > 0:
                        iDevice = iDeviceGPU
                    elif len(iDeviceAcc) > 0:
                        iDevice = iDeviceAcc
                    else:
                        iDevice = iDeviceCPU
                if len(iDevice) == 0:
                    targetOpenCL = None
            else:  # None
                targetOpenCL = None

        if targetOpenCL is not None:
            cl_file = os.path.join(os.path.dirname(__file__), self.cl_filename)
            with open(cl_file, 'r') as f:
                kernelsource = f.read()
            if precisionOpenCL == 'auto':
                try:
                    for device in iDevice:
                        if device.double_fp_config == 63:
                            precisionOpenCL = 'float64'
                        else:
                            raise AttributeError
                except AttributeError:
                    precisionOpenCL = 'float32'
            if _DEBUG > 10:
                print('precisionOpenCL = {0}'.format(precisionOpenCL))
            if precisionOpenCL == 'float64':
                self.cl_precisionF = np.float64
                self.cl_precisionC = np.complex128
                kernelsource = kernelsource.replace('float', 'double')
            else:
                self.cl_precisionF = np.float32
                self.cl_precisionC = np.complex64
            self.cl_queue = []
            self.cl_ctx = []
            self.cl_program = []
            for device in iDevice:
                cl_ctx = cl.Context(devices=[device])
                self.cl_queue.extend([cl.CommandQueue(cl_ctx, device)])
                self.cl_program.extend(
                    [cl.Program(cl_ctx, kernelsource).build(
                        options=["-I "+__dir__])])
                self.cl_ctx.extend([cl_ctx])

            self.cl_mf = cl.mem_flags
