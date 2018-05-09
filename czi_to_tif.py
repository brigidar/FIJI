#@UIService uiService
#@LogService log

#-----------------------DESCRIPTION--------------------------------------------------------------------
#adapted from sbesson czi.py script (https://gist.github.com/sbesson/42bcb21dc30f3644c17aabb6f5a1d917)
#run in FIJI
#requires empty output folder
#requires imput folder with all the czi files that you want to convert
#Author: Brigida Rusconi
#Date: 05/09/2018
#Version: 0.1
#-----------------------DESCRIPTION--------------------------------------------------------------------

# read in and display ImagePlus object(s)
from loci.plugins import BF
from loci.common import Region
from loci.plugins.in import ImporterOptions
from loci.plugins.util import LociPrefs
from ij import Prefs
from loci.formats import ImageReader
from loci.formats import MetadataTools
from ij import IJ
from ij import ImagePlus
from ome.units import UNITS
import os, sys
# ZEISS STUFF
from loci.formats.in import ZeissCZIReader
from loci.formats.in import DynamicMetadataOptions

def getImageSeries(imps, series):
    imp = imps[series]
    # get the stack
    imgstack = imp.getImageStack()
    slices = imgstack.getSize()
    log.info("Show Series #        : " + str(series))
    log.info("ImgStack.getSize()   : " + str(slices))
    return imp


#get total amount of scenes
def getTotal(imagefile,setflat=True):
    options = DynamicMetadataOptions()
    options.setBoolean("zeissczi.attachments", False)
    czireader = ZeissCZIReader()
    czireader.setFlattenedResolutions(setflat)
    czireader.setId(imagefile)
    seriesCount = czireader.getSeriesCount()
    czireader.close()
    return seriesCount
#save to tiff
def getCZIinfo(imagefile, showimage=False, setreslevel=0, setflat2=False, openallseries=True, showomexml=False,setconcat=False,filepath1="./"):
    options = DynamicMetadataOptions()
    options.setBoolean("zeissczi.attachments", False)
    czireader = ZeissCZIReader()
    czireader.setFlattenedResolutions(setflat2)
    czireader.setMetadataOptions(options)
    czireader.setId(imagefile)
    lc = czireader.getSeriesCount()
    #get the first occurence of each pyramid stack
    location=list()
    for i in range(0, int(seriesCount)-2):
        location.append(czireader.coreIndexToSeries(i))
        c=0
    #log.info(location)
    loc2=list()
    for i,v in enumerate(location):
    	if i==0:
        	loc2.append(i)
    	elif i>0 and v!=c:
        	loc2.append(i)
        	c=v
    log.info(str(loc2))
    # get OME data
    omeMeta = MetadataTools.createOMEXMLMetadata()
    # Set the preferences in the ImageJ plugin
    Prefs.set("bioformats.zeissczi.include.attachments", str(True).lower())
    if showimage:

        # read in and display ImagePlus(es) with arguments
        options = ImporterOptions()
        options.setOpenAllSeries(openallseries)
        options.setShowOMEXML(showomexml)
        options.setConcatenate(setconcat)
        options.setId(imagefile)

        # open the ImgPlus
        imps = BF.openImagePlus(options)
        name_list=imagefile.split('/')
        name=name_list[len(name_list)-1]
        out_path=filepath1  + "/"+name+"_Preview.tif"
        log.info(name)
        imp=getImageSeries(imps, seriesCount-1)
        imp.show()
        IJ.run("RGB Color")
        imp.close()
        IJ.saveAs("tiff", out_path)
        IJ.run("Close")
        out_path=filepath1  + "/"+name+"_Label.tif"
        imp=getImageSeries(imps, (seriesCount-2))
        imp.show()
        IJ.run("RGB Color")
        imp.close()
        IJ.saveAs("tiff", out_path)
        IJ.run("Close")
        c=1
        for series in loc2:
        	out_path=filepath1  + "/"+name+"Scene_" + str(c) + ".tif"
        	imp=getImageSeries(imps, series)
        	imp.show()
        	IJ.run("RGB Color")
        	imp.close()
        	IJ.saveAs("tiff", out_path)
        	IJ.run("Close")
        	c+=1
    czireader.close()
# clear the console automatically when not in headless mode
uiService.getDefaultUI().getConsolePane().clear()

inputDir = IJ.getDir("Choose input Directory")
#only grabs files in case there are any folders in the directory
#https://stackoverflow.com/questions/11968976/list-files-in-only-the-current-directory

dir_array1 = [f for f in os.listdir(inputDir) if os.path.isfile(os.path.join(inputDir,f))]
#does not generate a tiff file or folder for the thumbnail pictures of the preview and label
dir_array=[f for f in dir_array1 if "pt" not in f]
log.info(dir_array1)
log.info(dir_array)
dir_length = len(dir_array)




#create an output directory inside the folder with all the other ones
for i,image in enumerate(dir_array):
	fp=inputDir + "output"
	if not os.path.exists(fp):
		os.mkdir(fp)
	filepath=fp+"/" + dir_array[i]
	if not os.path.exists(filepath):
		os.mkdir(filepath)
	imag= inputDir + image
	seriesCount=getTotal(imag)
	getCZIinfo(imag,showimage=True,filepath1=filepath)

