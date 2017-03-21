import cv2
import sys
import numpy as np
from random import randint

def getPatchesError(target, targetL, texture, textureL, patchSize):
    target = target.astype(np.int32)
    texture = texture.astype(np.int32)
    diff = target[targetL[0]:targetL[0]+patchSize, targetL[1]:targetL[1]+patchSize] - texture[textureL[0]:textureL[0]+patchSize, textureL[1]:textureL[1]+patchSize]
    return np.sum(diff**2)**0.5

def getOverlapError(output, outputL, texture, textureL, patchSize, overlapW):
    output = output.astype(np.int32)
    texture = texture.astype(np.int32)
    # top
    if outputL[0]>=overlapW:
        diffH = output[outputL[0]-overlapW: outputL[0], outputL[1]:outputL[1]+patchSize] - texture[textureL[0]-overlapW:textureL[0], textureL[1]:textureL[1]+patchSize]
    else:
        diffH = 0
    # left
    if outputL[1]>=overlapW:        
        diffV = output[outputL[0]:outputL[0]+patchSize, outputL[1]-overlapW:outputL[1]] - texture[textureL[0]:textureL[0]+patchSize, textureL[1]-overlapW:textureL[1]]
    else:
        diffV = 0
    return (np.sum(diffH**2)+np.sum(diffV**2))**0.5


def getListofBestPatches(target, texture, texture_RGB, output, size_texture, pL, patchSize, overlapW, errorTH, iterationtime):
    # get the list of patches on texture which is similiart to the patch in the target
    # pL: patch location
    # errorTH: the maximum value of the SSD error which is allowed
    patchLList = [] # the list patches' location
    # iteration of each random patch in texture 
    for iter in range(iterationtime):
        i = randint(overlapW, size_texture[0]-patchSize)
        j = randint(overlapW, size_texture[1]-patchSize)
        patchError = 0.8*getPatchesError(target, pL, texture, (i,j), patchSize)
        overlapError = 0.2*getOverlapError(output, pL, texture_RGB, (i,j), patchSize, overlapW)
        if patchError+overlapError < errorTH:
            patchLList.append((i, j))
        elif patchError+overlapError < errorTH/2:
            return [(i,j)]
    # iteration of all pathes in texture image
    '''
    for i in range(size_texture[0]-patchSize):
        for j in range(size_texture[1]-patchSize):
            patchError = getPatchesError(target, pL, texture, (i,j), patchSize)
            if patchError < errorTH:
                patchLList.append((i, j))
            elif patchError < errorTH/2:
                return [(i,j)]
    '''
                
    return patchLList

def fillImage(output, outputPL, texture, texturePL, patchSize):
    output[outputPL[0]:outputPL[0]+patchSize, outputPL[1]:outputPL[1]+patchSize] = texture[texturePL[0]:texturePL[0]+patchSize, texturePL[1]:texturePL[1]+patchSize]
    return output

def getBoundaryH(output, outputPL, texture, texturePL, patchSize, overlapW):
    output = output.astype(np.int)
    texture = texture.astype(np.int)
    costMatrix = np.zeros((overlapW, patchSize), np.int)
    DPmap = np.zeros((overlapW, patchSize), np.int)
    costMatrix[:, 0] = np.sum((output[outputPL[0]-overlapW:outputPL[0], outputPL[1]]-texture[texturePL[0]-overlapW:texturePL[0], texturePL[1]])**2)
    # build cost matrix and DPmap
    for j in range(1, patchSize):
        for i in range(overlapW):
            singlecost = np.sum((output[outputPL[0]-overlapW+i, outputPL[1]+j]-texture[texturePL[0]-overlapW+i, texturePL[1]+j])**2)
            costMatrix[i,j] = min(costMatrix[max(i-1,0):min(i+1,overlapW-1), j-1])
            if(i-1>=0 and costMatrix[i,j]==costMatrix[i-1,j-1]):
                DPmap[i,j]=i-1
            elif(costMatrix[i,j]==costMatrix[i,j-1]):
                DPmap[i,j] = i
            else :
                DPmap[i,j] = i+1
            costMatrix[i,j] += singlecost
    # get boundary
    boundary = np.zeros(patchSize, np.int)
    boundary[patchSize-1] = np.argmin(costMatrix[:,patchSize-1])
    for j in range(patchSize-2, 0-1, -1):
        boundary[j] = DPmap[boundary[j+1], j+1]
    return boundary

def getBoundaryV(output, outputPL, texture, texturePL, patchSize, overlapW):
    output = output.astype(np.int)
    texture = texture.astype(np.int)
    costMatrix = np.zeros((patchSize, overlapW), np.int)
    DPmap = np.zeros((patchSize, overlapW), np.int)
    costMatrix[0, :] = np.sum((output[outputPL[0], outputPL[1]-overlapW:outputPL[1]]-texture[texturePL[0], texturePL[1]-overlapW:texturePL[1]])**2)
    # build cost matrix and DPmap
    for i in range(1, patchSize):
        for j in range(overlapW):
            singlecost = np.sum((output[outputPL[0]+i, outputPL[1]-overlapW+j]-texture[texturePL[0]+i, texturePL[1]-overlapW+j])**2)
            costMatrix[i,j] = min(costMatrix[i-1, max(j-1,0):min(j+1,overlapW-1)])
            if(j-1>=0 and costMatrix[i,j]==costMatrix[i-1,j-1]):
                DPmap[i,j]=j-1
            elif(costMatrix[i,j]==costMatrix[i-1,j]):
                DPmap[i,j] = j
            else :
                DPmap[i,j] = j+1
            costMatrix[i,j] += singlecost
    # get boundary
    boundary = np.zeros(patchSize, np.int)
    boundary[patchSize-1] = np.argmin(costMatrix[patchSize-1,:])
    for i in range(patchSize-2, 0-1, -1):
        boundary[i] = DPmap[i+1, boundary[i+1]]
    return boundary

def quiltH(output, outputPL, texture, texturePL, patchSize, overlapW, boundary):
        for j in range(patchSize):
            output[outputPL[0]+boundary[j]:outputPL[0]+overlapW, outputPL[1] + j] = texture[texturePL[0]+boundary[j]:texturePL[0]+overlapW, texturePL[1]+j]
        return output

def quiltV(output, outputPL, texture, texturePL, patchSize, overlapW, boundary):
        for i in range(patchSize):
            output[outputPL[0]+i, outputPL[1]+boundary[i]:outputPL[1]+overlapW] = texture[texturePL[0]+i, texturePL[1]+boundary[i]:texturePL[1]+overlapW]
        return output

def quiltPatches(output, outputPL, texture, texturePL, patchSize, overlapW):
    # top
    if outputPL[0]>=overlapW:
        boundaryH = getBoundaryH(output, outputPL, texture, texturePL, patchSize, overlapW)
        output = quiltH(output, outputPL, texture, texturePL, patchSize, overlapW, boundaryH)
    # left
    if outputPL[1]>=overlapW:
        boundaryV = getBoundaryV(output, outputPL, texture, texturePL, patchSize, overlapW)
        output = quiltV(output, outputPL, texture, texturePL, patchSize, overlapW, boundaryV)
    return output

if __name__ == "__main__":
    ###  Image Loading and initialization ###
    # get parameters from argv
    inputName  = str(sys.argv[1])
    textureName  = str(sys.argv[2])
    outputName = str(sys.argv[3])
    patchSize  = int(sys.argv[4])
    overlapSize = int(sys.argv[5])
    initialThresConstant = float(sys.argv[6])
    #inputName = 'target_resize.jpg' 
    #textureName = 'texture_brown_resize.jpg'
    #patchSize = 10
    #overlapSize = 3
    #initialThresConstant = 5 #78.0
    # initialize
    img_input_RGB = cv2.imread(inputName)
    img_input = cv2.cvtColor(img_input_RGB, cv2.COLOR_BGR2GRAY)
    if(int(sys.argv[6])==1):
        img_input = cv2.Canny(img_input,100,200)
    img_texture_RGB = cv2.imread(textureName)
    img_texture = cv2.cvtColor(img_texture_RGB, cv2.COLOR_BGR2GRAY)
    if(int(sys.argv[6])==1):
        img_texture = cv2.Canny(img_texture,100,200)
    size_input = img_input.shape
    size_texture = img_texture.shape
    img_out = np.zeros(img_input_RGB.shape, np.uint8)
    
    ### Begin with random patch ###
    # for texture transform, this step is not necessray

    ### for loop to find the all corresponding patches on output image ###
    print('total num of patches: ' + str(int(np.ceil(size_input[0]/patchSize)*np.ceil(size_input[1]/patchSize))))
    numPatchCompleted = 0
    for i in range(int(np.ceil(size_input[0]/patchSize))):
        for j in range(int(np.ceil(size_input[1]/patchSize))):
            # get patch's location
            patchLOut = [i*patchSize, j*patchSize]
            if patchLOut[0]+patchSize>=size_input[0] :
                patchLOut[0] = size_input[0]-patchSize
            if patchLOut[1]+patchSize>=size_input[1] :
                patchLOut[1] = size_input[1]-patchSize
            # setting of threshold of patch-error            
            errorTHofPatch = initialThresConstant * patchSize * patchSize
            listPL = []
            while(len(listPL)==0):
                # get list of the best matches
                listPL = getListofBestPatches(img_input, img_texture, img_texture_RGB,img_out, size_texture, patchLOut, patchSize, overlapSize,errorTHofPatch, 200)
                errorTHofPatch *= 1.1
                if errorTHofPatch*1.1!=initialThresConstant*patchSize*patchSize:
                    print('increase threshold of patch error')
            print('List length:' + str(len(listPL)))
            # random get patch in list and put patch onto output image
            patchL = listPL[randint(0, len(listPL)-1)]
            img_out = fillImage(img_out, patchLOut, img_texture_RGB, patchL, patchSize)
            # Quilt
            img_out = quiltPatches(img_out, patchLOut, img_texture_RGB, patchL, patchSize, overlapSize)
            # print commend line
            numPatchCompleted += 1
            print('completed num of patches: ' + str(numPatchCompleted))

    cv2.imwrite('results\\' + outputName, img_out)
    cv2.imshow('input', img_input_RGB)
    cv2.imshow('output', img_out)
    cv2.waitKey(0)