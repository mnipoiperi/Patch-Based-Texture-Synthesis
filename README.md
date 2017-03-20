# Patch-Based-Texture-Synthesis
It's an implementation of Efros and Freeman's "Image Quilting and Texture Synthesis" 2001

The output depends on two factors : PatchSize and OverlapWidth
The running time depends on Sample Image dimensions, Desired Image dimensions, ThresholdConstant and PatchSize

## To run the code, copy the following into your command line
'python PatchBasedSynthesis.py /image/source.jpg Patch_Size Overlap_Width Initial_Threshold_error'

for example
'python PatchBasedSynthesis.py corn.jpg 30 5 78.0'

# Patch_Based-Texture-Transform-Synthesis
To run the code
'python PatchBasedTextureTransform.py target-image texture-image patch-size overlap-width initial-threshold-error using-edge'

for example
'python PatchBasedTextureTransform.py input/target_minion.jpg input/texture3.jpg 10 6 9 0'

