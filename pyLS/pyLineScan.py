# pyLineScan is a package to aid analysis of two-photon linescans 

import os

def xml_getValue(s):
     """
     given an XML string return the value field. It could be a float or a string.
     '<PVStateValue key="dwellTime" value="7.2" />' becomes '7.2'
     """
     s=s.split("value=")[1].split('"')[1]
     try:return float(s)
     except:return str(s)

class LineScan:
    def __init__(self,folder):
        """
        The LineScan class provides an easy object to load and analyze data from PrairieView linescan folders.
        """
        
        # with out the path and name of the linescan
        self.folder=os.path.abspath(folder)
        assert(os.path.exists(self.folder)), self.folder+" doesn't exist"
        self.name=os.path.basename(self.folder)
        print("loading linescan",self.name)
        
        # figure out which files are linescans, XML data, etc
        self.files=sorted(os.listdir(self.folder))
        assert len([x for x in self.files if x.endswith(".env")]), "no .env file found"
        self.fileEnv=[x for x in self.files if x.endswith(".env")]
        assert len([x for x in self.files if x.endswith(".xml")]), "no .xml file found"
        self.fileXml=[x for x in self.files if x.endswith(".xml")][0]
        self.filesR=[x for x in self.files if x.endswith(".tif") and "_Ch1_" in x]
        self.filesG=[x for x in self.files if x.endswith(".tif") and "_Ch2_" in x]
        print("linescans found: %d red and %d green"%(len(self.filesR),len(self.filesG)))
        
        self.loadConf()

    def loadConf(self):
        """
        Load the content of the .env and .xml files to determine the parameters used to acquire the data.
        """
        keys=["dwellTime","scanLinePeriod"]
        self.conf={}
        with open(os.path.join(self.folder,self.fileXml)) as f:
             for line in f.readlines():
                  for key in keys:
                       if key in line:
                            self.conf[key]=xml_getValue(line)
        
if __name__=="__main__":
    LS=LineScan('../data/linescan/realistic/LineScan-06092017-1414-622')
    print("DONE")