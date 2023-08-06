"""

Environmentally-driven population dynamics model of Aedes albopictus

This package implements the stage- and age-structured population dynamics model of temperate Aedes albopictus (Skuse) as described in Erguler et.al.. The package includes a representative environmental dataset for the Emilia-Romagna region. The package also includes three sets of parameter vectors sampled from different posterior modes offering explanation to the data obtained from surveillance.

References

     Erguler K, Smith-Unna SE, Waldock J, Proestos Y, Christophides GK, Lelieveld J, Parham PE. Large-scale modelling of the environmentally-driven population dynamics of temperate Aedes albopictus (Skuse). PLOS ONE (under review)

See also

     hoppMCMC - an adaptive basin-hopping Markov-chain Monte Carlo algorithm for Bayesian optimisation

Examples

     import albopictus as aa

     # The following line simulates the model at the first environmental grid point
     # of Bologna using the first parameter vector of the posterior mode Q1.
     sim = aa.simPar(aa.vector,aa.clim['BO'][0],aa.param['Q1'][0])

     # This will convert days of simulation into dates for plotting
     dates = aa.getDates(sim['colT'])

     import pylab

     pylab.ylim([0,50])
     pylab.plot(dates,sim['colegg'])
     pylab.show()

"""

# modelAalbopictus - climateData ------------------------- //
from distutils.sysconfig import get_python_lib
import pkg_resources
import numpy
import json
from datetime import datetime, timedelta

clim = json.load(open(pkg_resources.resource_filename(__name__, "data/climate.json"),"r"))
param = json.load(open(pkg_resources.resource_filename(__name__, "data/posterior.json"),"r"))
prior = json.load(open(pkg_resources.resource_filename(__name__, "data/prior.json"),"r"))

provinces = ["Bologna","Ferrara","Modena","Piacenza","Parma","Ravenna","Reggio Emilia"]
prvn = ["BO","FE","MO","PC","PR","RA","RE"]

weeksBefore = 52
finalT = 1827 + weeksBefore*7
begin = datetime(2007,12,31,0,0) - timedelta(days=7*weeksBefore)
def getDates(times):
    """ Convert days of simulation into dates for the Emilia-Romagna dataset """
    return numpy.array([begin + timedelta(days=d) for d in times])

# modelAalbopictus --------------------------------------- //

from readModel import prepareModel

def simPar(model,clim,pr,fT=numpy.nan):
    """
    Simulate the model at a specific environmental grid point with a given parameter vector

    Parameters
    ----------

         model:
              model to be simulated
              currently the only model implemented in this package is 'vector'

         clim:
              environmental dataset to be used
              it must be a dictionary with key 'envar'
              clim['envar'] should hold an array with the following data in the given order and size
                   photoperiod [finalT]
                   mean air temperature [finalT]
                   daily precipitation [finalT]
                   human population density [1]
              the object 'clim' holds an example dataset for the Emilia-Romagna region

         pr:
              an array of size vector.numpar holding the parameter vector

         fT:
              if the required days of simulation is different than finalT, this should be stated using fT
              WARNING: In this case, clim['envar'] should be prepared according to the new duration
              
    """
    if numpy.isnan(fT):
        fT = numpy.array(finalT,dtype=numpy.int32,ndmin=1)
    else:
        fT = numpy.array(fT,dtype=numpy.int32,ndmin=1)
    pr = numpy.array(pr,dtype=numpy.float64,ndmin=1)
    result = numpy.ndarray((model.nummet+1)*fT[0],dtype=numpy.float64)
    success = numpy.arange(1,dtype=numpy.int32)
    ret = model.sim_model(numpy.array(clim['envar']),
                          pr,
                          fT,
                          result,
                          success)
    ret = {
        'colT':result[0:fT[0]],
        'success':success
        }
    for n in range(model.nummet):
        ret[model.metnames[n]] = result[((n+1)*fT[0]):((n+2)*fT[0])]
    return ret

vector = prepareModel(pkg_resources.resource_filename(__name__, "modelAalbopictus.so"))

