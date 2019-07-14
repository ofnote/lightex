### Train multiple EfficientNet models on Imagenette

Code based on [this](https://github.com/lukemelas/EfficientNet-PyTorch) repository.

[Imagenette](https://github.com/fastai/imagenette) is a smaller subset of 10 easily classified classes from Imagenet,



### ImageNette

Download one of the [Imagenette](https://github.com/fastai/imagenette) datasets, and unzip into the `data-dir`. Ensure `train` and `val` folders are present in `data-dir`.


### Standalone commands

Original commands to evaluate pre-trained models: 
```bash
# Evaluate small EfficientNet on CPU
python main.py data -e -a 'efficientnet-b0' --pretrained 
```
```bash
# Evaluate medium EfficientNet on GPU
python main.py data -e -a 'efficientnet-b3' --pretrained --gpu 0 --batch-size 128
```
```bash
# Evaluate ResNet-50 for comparison
python main.py data -e -a 'resnet50' --pretrained --gpu 0
```
