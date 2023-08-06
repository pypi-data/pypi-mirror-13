"""factories for creating mincVolumes"""

from .volumes import mincException,mincVolume

def volumeFromFile(filename, dtype="float", readonly=True, labels=False):
    """creates a new mincVolume from existing file."""
    v = mincVolume(filename=filename, dtype=dtype, readonly=readonly, labels=labels)
    v.openFile()
    return(v)
    
def volumeFromInstance(volInstance, outputFilename, dtype="float", data=False,
                       dims=None, volumeType=None, path=False, labels=False):
    """creates new mincVolume from another mincVolume"""
    v = mincVolume(filename=outputFilename, dtype=dtype, readonly=False, labels=labels)
    v.copyDimensions(volInstance, dims)
    v.copyDtype(volInstance)
    v.createVolumeHandle(volumeType or v.dtype)
    v.copyHistory(volInstance)
    if data:
        if not volInstance.dataLoaded:
            volInstance.loadData()
        v.createVolumeImage()  
        v.data = volInstance.data.copy()
    if path:
        v.copyAttributes(volInstance, path)

    return(v)

def volumeLikeFile(likeFilename, outputFilename, dtype="float", volumeType="ubyte",
                   labels=False):
    """creates a new mincVolume with dimension info taken from an existing file"""
    lf = volumeFromFile(filename=likeFilename, dtype=dtype, labels=labels)
    v = volumeFromInstance(volInstance=lf, outputFilename=outputFilename, 
                           dtype=dtype, volumeType=volumeType,
                           labels=labels)
    lf.closeVolume()
    return(v)

def volumeFromDescription(outputFilename, dimnames, sizes, starts, steps, volumeType="ubyte",
                          dtype="float", labels=False):
    """creates a new mincVolume given starts, steps, sizes, and dimension names"""
    v = mincVolume(filename=outputFilename, dtype=dtype, readonly=False, labels=labels)
    v.createNewDimensions(dimnames, sizes, starts, steps)
    v.createVolumeHandle(volumeType)
    v.createVolumeImage()
    return(v)

def volumeFromData(outputFilename, data, dimnames=("xspace", "yspace", "zspace"),
                   starts=(0,0,0), steps=(1,1,1),
                   volumeType="ubyte", labels=False):
    """creates a mincVolume from a given array"""
    v = volumeFromDescription(outputFilename=outputFilename, sizes=data.shape,
                              dimnames=dimnames, starts=starts, steps=steps,
                              volumeType=volumeType, labels=labels)
    v.dtype = v.getDtype(data)
    v.data = data
    return v
