import numpy as np
import os
import scipy.misc as misc
import random
from PIL import Image
#------------------------Class for reading training and  validation data---------------------------------------------------------------------
class Data_Reader:


################################Initiate folders were files are and list of train images############################################################################
    def __init__(self, ImageDir,GTLabelDir="", BatchSize=1,Suffle=True):
        #ImageDir directory were images are
        #GTLabelDir Folder wehere ground truth Labels map are save in png format (same name as corresponnding image in images folder)
        self.NumFiles = 0 # Number of files in reader
        self.Epoch = 0 # Training epochs passed
        self.itr = 0 #Iteration
        #Image directory
        self.Image_Dir=ImageDir # Image Dir
        if GTLabelDir=="":# If no label dir use
            self.ReadLabels=False
        else:
            self.ReadLabels=True
        self.Label_Dir = GTLabelDir # Folder with ground truth pixels was annotated (optional for training only)
        self.OrderedFiles=[]
        # Read list of all files
        self.OrderedFiles += [each for each in os.listdir(self.Image_Dir) if each.endswith('.PNG') or each.endswith('.JPG') or each.endswith('.TIF') or each.endswith('.GIF') or each.endswith('.png') or each.endswith('.jpg') or each.endswith('.tiff') or each.endswith('.gif') ] # Get list of training images
        self.BatchSize=BatchSize #Number of images used in single training operation
        self.NumFiles=len(self.OrderedFiles)
        self.OrderedFiles.sort() # Sort files by names
        self.SuffleBatch() # suffle file list
####################################### Suffle list of files in  group that fit the batch size this is important since we want the batch to contain images of the same size##########################################################################################
    def SuffleBatch(self):
        self.SFiles = []
        Sf=np.array(range(np.int32(np.ceil(self.NumFiles/self.BatchSize)+1)))*self.BatchSize
        random.shuffle(Sf)
        self.SFiles=[]
        for i in range(len(Sf)):
            for k in range(self.BatchSize):
                  if Sf[i]+k<self.NumFiles:
                      self.SFiles.append(self.OrderedFiles[Sf[i]+k])
###########################Read and augment next batch of images and labels#####################################################################################
    def ReadAndAugmentNextBatch(self):
        if self.itr>=self.NumFiles: # End of an epoch
            self.itr=0
            self.SuffleBatch()
            self.Epoch+=1
        batch_size=np.min([self.BatchSize,self.NumFiles-self.itr])
        

#-----------Augument Images and labeles-------------------------------------------------------------------

        for f in range(batch_size):
#.............Read image and labels from files.........................................................
           Img = misc.imread(self.Image_Dir + "/" + self.SFiles[self.itr])
           Img=Img[:,:,0:3]
           LabelName=self.SFiles[self.itr][0:-5]+".tif"# Assume Label name is same as image only with png ending
           if self.ReadLabels:
              Label= misc.imread(self.Label_Dir + "/" + LabelName)
           self.itr+=1
#............Set Batch image size according to first image in the batch...................................................
           if f==0:
                Sy,Sx,Depth=Img.shape
                Sy = np.int32(Sy)
                Sx = np.int32(Sx)
                Images = np.zeros([batch_size,Sy,Sx,3], dtype=np.float)
                if self.ReadLabels: Labels= np.zeros([batch_size,Sy,Sx,1], dtype=np.int)


#--------------------------  add noise----------------------------------------------

           #Img = np.float32(Img)
           ran_number = random.random()
           degree = ran_number*360
           Im = Image.fromarray(Img)
           Img = Im.rotate(degree, expand = True)
           Img = misc.imresize(Img, [Sy, Sx], interp = 'nearest')
           if self.ReadLabels:
               Lab = Image.fromarray(Label)
               Label = Lab.rotate(degree, expand = True)
               Label = misc.imresize(Label, [Sy, Sx], interp = 'nearest')
                
           Img = np.float32(Img) 
           if np.random.rand() <0.4:
               Img *=np.ones(Img.shape)*0.95 + np.random.rand(Img.shape[0],Img.shape[1],Img.shape[2])*0.1
           Img[Img>255]=255
           Img[Img<0]=0    
#----------------------Add images and labels to to the batch----------------------------------------------------------
           Images[f]=Img
           if self.ReadLabels:
                  Labels[f,:,:,0]=Label

#.......................Return aumented images and labels...........................................................
        if self.ReadLabels:
            return Images, Labels# return image and pixelwise labels
        else:
            return Images# Return image




######################################Read next batch of images and labels with no augmentation######################################################################################################
    def ReadNextBatchClean(self): #Read image and labels without agumenting
        if self.itr>=self.NumFiles: # End of an epoch
            self.itr=0
            #self.SuffleBatch()
            self.Epoch+=1
        batch_size=np.min([self.BatchSize,self.NumFiles-self.itr])

        for f in range(batch_size):
##.............Read image and labels from files.........................................................
           Img = misc.imread(self.Image_Dir + "/" + self.OrderedFiles[self.itr])
           Img=Img[:,:,0:3]
           LabelName=self.OrderedFiles[self.itr][0:-5]+".tif"# Assume label name is same as image only with png ending
           if self.ReadLabels:
              Label= misc.imread(self.Label_Dir + "/" + LabelName)
           self.itr+=1
#............Set Batch size according to first image...................................................
           if f==0:
                Sy,Sx,Depth=Img.shape
                Images = np.zeros([batch_size,Sy,Sx,3], dtype=np.float)
                if self.ReadLabels: Labels= np.zeros([batch_size,Sy,Sx,1], dtype=np.int)

#...................Load image and label to batch..................................................................
           Images[f] = Img
           if self.ReadLabels:
              Labels[f, :, :, 0] = Label
#...................................Return images and labels........................................
        if self.ReadLabels:
               return Images, Labels  # return image and and pixelwise labels
        else:
               return Images  # Return image

