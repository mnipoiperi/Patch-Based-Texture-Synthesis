import cv2
import sys
import numpy as np
from random import randint

def getPatchesError(target, targetL, texture, textureL, patchSize):
    target = target.astype(np.int32)
    texture = texture.astype(np.int32)
    diff = target[targetL[0]:targetL[0]+patchSize, targetL[1]:targetL[1]+patchSize] - texture[textureL[0]:textureL[0]+patchSize, textureL[1]:textureL[1]+patchSize]
    return np.sum(diff**2)**0.5

def getListofBestPatches(target, texture, size_texture, pL, patchSize, errorTH, iterationtime):
    # get the list of patches on texture which is similiart to the patch in the target
    # pL: patch location
    # errorTH: the maximum value of the SSD error which is allowed
    patchLList = [] # the list patches' location
    # iteration of each random patch in texture 
    for iter in range(iterationtime):
        i = randint(0, size_texture[0]-patchSize)
        j = randint(0, size_texture[1]-patchSize)
        patchError = getPatchesError(target, pL, texture, (i,j), patchSize)
        if patchError < errorTH:
            patchLList.append((i, j))
        elif patchError < errorTH/2:
            return [(i,j)]
    return patchLList

def fillImage(output, outputPL, texture, texturePL, patchSize):
    output[outputPL[0]:outputPL[0]+patchSize, outputPL[1]:outputPL[1]+patchSize] = texture[texturePL[0]:texturePL[0]+patchSize, texturePL[1]:texturePL[1]+patchSize]
    return output

if __name__ == "__main__":
    ###  Image Loading and initialization ###
    # get parameters from argv
    #inputName  = str(sys,argv[1])
    #textureName  = str(sys,argv[2])
    #patchSize  = int(sys.argv[3])
    #overlapSize = int(sys.argv[4])
    #initialThresConstant = float(sys.argv[5])
    inputName = 'target.jpg' 
    textureName = 'texture2_resize.jpg'
    patchSize = 23
    overlapSize = 1
    initialiThresConstant = 1 #78.0
    # initialize
    img_input = cv2.imread(inputName)
    img_input = cv2.cvtColor(img_input, cv2.COLOR_BGR2GRAY)
    img_texture = cv2.imread(textureName)
    img_texture = cv2.cvtColor(img_texture, cv2.COLOR_BGR2GRAY)
    size_input = img_input.shape
    size_texture = img_texture.shape
    img_out = np.zeros(size_input, np.uint8)
    
    ### Begin with random patch ###
    # for texture transform, this step is not necessray

    ### for loop to find the all corresponding patches on output image ###
    print('total num of patches: ' + str(int(np.ceil(size_input[0]/patchSize)*np.ceil(size_input[1]/patchSize))))
    numPatchCompleted = 0
    for i in range(int(np.ceil(size_input[0]/patchSize))):
        for j in range(int(np.ceil(size_input[1]/patchSize))):
            # get patch's location
            patchLocation = [i*patchSize, j*patchSize]
            if patchLocation[0]+patchSize>=size_input[0] :
                patchLocation[0] = size_input[0]-patchSize
            if patchLocation[1]+patchSize>=size_input[1] :
                patchLocation[1] = size_input[1]-patchSize
            # setting of threshold of patch-error            
            errorTHofPatch = initialiThresConstant * patchSize * patchSize
            listPL = []
            while(len(listPL)==0):
                # get list of the best matches
                listPL = getListofBestPatches(img_input, img_texture, size_texture, patchLocation, patchSize, errorTHofPatch, 200)
                errorTHofPatch *= 1.1
                if errorTHofPatch*1.1!=initialiThresConstant*patchSize*patchSize:
                    print('increase threshold of patch error')
            print('List length:' + str(len(listPL)))
            # random get patch in list and put patch onto output image
            patchL = listPL[randint(0, len(listPL)-1)]
            img_out = fillImage(img_out, patchLocation, img_texture, patchL, patchSize)
            # print commend line
            numPatchCompleted += 1
            print('completed num of patches: ' + str(numPatchCompleted))

    cv2.imshow('input', img_input)
    cv2.imshow('output', img_out)
    cv2.waitKey(0)