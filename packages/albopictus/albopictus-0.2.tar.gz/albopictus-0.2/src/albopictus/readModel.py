import ctypes
import numpy
import numpy.ctypeslib as npct
array_1d_double = npct.ndpointer(dtype=numpy.float64, ndim=1, flags='CONTIGUOUS')
array_1d_int = npct.ndpointer(dtype=numpy.int32, ndim=1, flags='CONTIGUOUS')

def prepareModel(modelname):
    model = ctypes.cdll.LoadLibrary(modelname)
    #
    import atexit
    try:
        model.rng_setup()
    except:
        pass
    try:
        atexit.register(model.rng_destroy)
    except:
        pass
    #
    model.numparModel.restype = None
    model.numparModel.argtypes = [array_1d_int,array_1d_int]
    model.numpar = numpy.arange(1,dtype=numpy.int32)
    model.nummet = numpy.arange(1,dtype=numpy.int32)
    ret = model.numparModel(model.numpar,model.nummet)
    model.numpar = model.numpar[0]
    model.nummet = model.nummet[0]
    #
    try:
        model.param_model.restype = None
        model.param_model.argtypes = [ctypes.POINTER(ctypes.c_char_p),array_1d_double]
        temp = (ctypes.c_char_p * (model.nummet+model.numpar))(256)
        model.param = numpy.array([0 for n in range(model.numpar)],dtype=numpy.float64)
        ret = model.param_model(temp,model.param)
        temp = numpy.array([elm for elm in temp])
        model.metnames = numpy.copy(temp[:model.nummet])
        model.parnames = numpy.copy(temp[-model.numpar:])
    except:
        print "Skipping default parameters"
        model.metnames = numpy.array(["coln%d" %(n) for n in range(model.nummet)])
        model.parnames = numpy.array(["par%d" %(n) for n in range(model.numpar)])
    #
    model.metids = {}
    for elm in model.metnames:
        model.metids[elm] = numpy.where(elm==model.metnames)[0][0]
    #
    model.parids = {}
    for elm in model.parnames:
        model.parids[elm] = numpy.where(elm==model.parnames)[0][0]
    #
    model.sim_model.restype = None
    model.sim_model.argtypes = [array_1d_double,
                                array_1d_double,
                                array_1d_int,
                                array_1d_double,
                                array_1d_int]
    #
    return model
