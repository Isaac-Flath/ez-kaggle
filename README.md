ez_kaggle
================

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

``` python
from ez_kaggle.setup import *
from ez_kaggle.dataset import *
from ez_kaggle.kernel import *
from pathlib import Path
```

``` python
from fastcore.all import *
```

## Install

`pip install ez-kaggle`

## How to use

### Core

This little library is where I’ll be putting snippets of stuff which are
useful on Kaggle. Functionality includes the following:

It defines `IN_KAGGLE` which is `True` if you’re running on Kaggle or
`False` if you are not running on kaggle:

``` python
IN_KAGGLE
```

    False

You can also use the kaggle api directly, even on kaggle with

``` python
api = import_kaggle()
```

### Competition

The competition module gives a `setup_comp` function which:

1.  Gets a path to the data for a competition, downloading it if needed
2.  installs any modules that might be missing or out of data if running
    on Kaggle
3.  Creates a config file with the competition name, paths where
    datasets to be stored, username to use for datasets, and other
    competition configurable items

> Note: All config values have smart defaults that work for almost every
> competition. You don’t have to define any of them, but you’re welcome
> to change them if you’d like.

``` python
setup_comp('titanic')
```

    Inferring dataset_username from credentials
    Inferring model_dataset_name from competition
    Inferring libraries_dataset_name from competition
    Setting required libraries to ['fastkaggle']

### Libraries

The Libraries module gives a function to manage pip libraries as kaggle
datasets, especially useful for no-internet inference competitions

Simply define list your pip requirements in the `fastkaggle.json` config
file and call `create_dependency_dataset` anytime for it to
create/update the dataset with the lastest of those packages in pip.

<div>

> **Tip**
>
> The purpose of this is to create datasets that can be used in no
> internet inference competitions to install libraries using
> `pip install -Uqq library --no-index --find-links=file:///kaggle/input/your_dataset/`

</div>

``` python
create_dependency_dataset()
```

    -----Downloading or Creating Dataset if needed
    -----Checking dataset files against pip
    -----Kaggle dataset already up to date
    isaacflath/libraries-titanic update complete

### Models

The Models module gives functions to manage your models as kaggle
datasets, especially useful for no-internet inference competitions

Simply create and train your normal fastai model.

``` python
from fastai.vision.all import *
import pandas as pd
```

Create a fastai model

``` python
path = untar_data(URLs.MNIST_SAMPLE)
df = pd.read_csv(path/'labels.csv')
dls = ImageDataLoaders.from_df(df,path)
learn = vision_learner(dls, models.resnet18, loss_func=CrossEntropyLossFlat(), ps=0.25)
```

    [W NNPACK.cpp:51] Could not initialize NNPACK! Reason: Unsupported hardware.

Then pass is to `fastkaggle` with a name a version comment for it to be
exported and updated in your competition kaggle dataset (defined in
`fastkaggle.json` config file)

``` python
push_fastai_learner(learn,'model1.pkl','testing fastkaggle')
```

    -----Downloading or Creating Dataset if needed
    models-titanic
    isaacflath/models-titanic update complete

### Notebooks

Notebooks can be pushed to kaggle kernels with `push_notebook`, and
these notebooks can understand if they are running locally or in kaggle
thanks to `is_kaggle`. No need to manage 2 environments, just work on
your own machine and push anytime!

This function:

-   Infers title using nbdev
-   Creates Id by removing punctuation, whitespace and lowecasing title
-   Links you kaggle dataset with your libraries and your kaggle dataset
    with your models to it as defined in `fastkaggle.json`

``` python
push_notebook('index.ipynb')
```

    Kernel version 5 successfully pushed.  Please check progress at https://www.kaggle.com/code/isaacflath/ez-kaggle