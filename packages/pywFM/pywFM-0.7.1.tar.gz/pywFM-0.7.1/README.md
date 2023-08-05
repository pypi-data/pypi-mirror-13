pywFM
======

pywFM is a Python wrapper for Steffen Rendle's [libFM](http://libfm.org/). libFM is a **Factorization Machine** library:

> Factorization machines (FM) are a generic approach that allows to mimic most factorization models by feature engineering. This way, factorization machines combine the generality of feature engineering with the superiority of factorization models in estimating interactions between categorical variables of large domain. libFM is a software implementation for factorization machines that features stochastic gradient descent (SGD) and alternating least squares (ALS) optimization as well as Bayesian inference using Markov Chain Monte Carlo (MCMC).

For more information regarding Factorization machines and libFM, read Steffen Rendle's paper: [Factorization Machines with libFM, in ACM Trans. Intell. Syst. Technol., 3(3), May. 2012](http://www.csie.ntu.edu.tw/~b97053/paper/Factorization%20Machines%20with%20libFM.pdf)

**Don't forget to acknowledge `libFM` (i.e. cite the paper [Factorization Machines with libFM](http://libfm.org/#publications)) if you publish results produced with this software.**


### Motivation
While using Python implementations of Factorization Machines, I felt that the current implementations ([pyFM](https://github.com/coreylynch/pyFM) and [fastFM](https://github.com/ibayer/fastFM/)) had many *[f](https://github.com/coreylynch/pyFM/issues/3)l[a](https://github.com/ibayer/fastFM/blob/master/examples/warm_start_als.py#L45)w[s](https://github.com/ibayer/fastFM/issues/13)*. Then I though, why re-invent the wheel? Why not use the original libFM?

Sure, it's not Python native yada yada ... But at least we have a bulletproof, battle-tested implementation that we can guide ourselves with.

### Installing
`pywFM` was develop for Python 2.7 (feel free to PR a Python 3 transition). Install using `pip`:
```shell
pip install pywFM
```

Binary installers for the latest released version are available at the [Python package index](http://pypi.python.org/pypi/pywFM/).

### Dependencies
* numpy
* scipy
* sklearn
* pandas

### Example

Very simple example taken from Steffen Rendle's paper: Factorization Machines with libFM.

```py
import pywFM
import numpy as np
import pandas as pd

features = np.matrix([
#     Users  |     Movies     |    Movie Ratings   | Time | Last Movies Rated
#    A  B  C | TI  NH  SW  ST | TI   NH   SW   ST  |      | TI  NH  SW  ST
    [1, 0, 0,  1,  0,  0,  0,   0.3, 0.3, 0.3, 0,     13,   0,  0,  0,  0 ],
    [1, 0, 0,  0,  1,  0,  0,   0.3, 0.3, 0.3, 0,     14,   1,  0,  0,  0 ],
    [1, 0, 0,  0,  0,  1,  0,   0.3, 0.3, 0.3, 0,     16,   0,  1,  0,  0 ],
    [0, 1, 0,  0,  0,  1,  0,   0,   0,   0.5, 0.5,   5,    0,  0,  0,  0 ],
    [0, 1, 0,  0,  0,  0,  1,   0,   0,   0.5, 0.5,   8,    0,  0,  1,  0 ],
    [0, 0, 1,  1,  0,  0,  0,   0.5, 0,   0.5, 0,     9,    0,  0,  0,  0 ],
    [0, 0, 1,  0,  0,  1,  0,   0.5, 0,   0.5, 0,     12,   1,  0,  0,  0 ]
])
target = [5, 3, 1, 4, 5, 1, 5]

fm = pywFM.FM(task='regression', num_iter=5)

# split features and target for train/test
# first 5 are train, last 2 are test
model = fm.run(features[:5], target[:5], features[5:], target[5:])
print model.predictions
# you can also get the model weights
print model.weights
```

You can also use numpy's `array`, sklearn's `sparse_matrix`, and even pandas' `DataFrame` as features input.

### Usage

*Don't forget to acknowledge `libFM` (i.e. cite the paper [Factorization Machines with libFM](http://libfm.org/#publications)) if you publish results produced with this software.*

##### **`FM`**: Class that wraps `libFM` parameters. For more information read [libFM manual](http://www.libfm.org/libfm-1.42.manual.pdf)

```
Parameters
----------
task : string, MANDATORY
        regression: for regression
        classification: for binary classification
num_iter: int, optional
    Number of iterations
    Defaults to 100
init_stdev : double, optional
    Standard deviation for initialization of 2-way factors
    Defaults to 0.1
k0 : bool, optional
    Use bias.
    Defaults to True
k1 : bool, optional
    Use 1-way interactions.
    Defaults to True
k2 : int, optional
    Dimensionality of 2-way interactions.
    Defaults to 8
learning_method: string, optional
    sgd: parameter learning with SGD
    sgda: parameter learning with adpative SGD
    als: parameter learning with ALS
    mcmc: parameter learning with MCMC
    Defaults to 'mcmc'
learn_rate: double, optional
    Learning rate for SGD
    Defaults to 0.1
r0_regularization: int, optional
    bias regularization for SGD and ALS
    Defaults to 0
r1_regularization: int, optional
    1-way regularization for SGD and ALS
    Defaults to 0
r2_regularization: int, optional
    2-way regularization for SGD and ALS
    Defaults to 0
rlog: bool, optional
    Enable/disable rlog output
    Defaults to True.
verbose: bool, optional
    How much infos to print
    Defaults to False.
silent: bool, optional
    Completly silences all libFM output
    Defaults to False.
temp_path: string, optional
    Sets path for libFM temporary files. Usefull when dealing with large data.
    Defaults to None (default mkstemp behaviour)
```

##### **`FM.run`**: run factorization machine model against train and test data
```

Parameters
----------
x_train : {array-like, matrix}, shape = [n_train, n_features]
    Training data
y_train : numpy array of shape [n_train]
    Target values
x_test: {array-like, matrix}, shape = [n_test, n_features]
    Testing data
y_test : numpy array of shape [n_test]
    Testing target values

Return
-------
Returns `namedtuple` with the following properties:

predictions: array [n_samples of x_test]
   Predicted target values per element in x_test.
global_bias: float
    If k0 is True, returns the model's global bias w0
weights: array [n_features]
    If k1 is True, returns the model's weights for each features Wj
pairwise_interactions: numpy matrix [n_features x k2]
    Matrix with pairwise interactions Vj,f
rlog: pandas dataframe [nrow = num_iter]
    `pandas` DataFrame with measurements about each iteration
```

### Docker
This repository includes `Dockerfile` for development and for running `pywFM`.

* Run `pywFM` examples ([Dockerfile](examples/Dockerfile)): if you are only interested in running the examples. `Dockerfile` defaults to the `simple.py` example (the one in this README).
```shell
# to build image
docker build --rm=true -t jfloff/pywfm-run .
# to run image
docker run --rm -v "$(pwd)":/home/pywfm-run -w /home/pywfm-run -ti jfloff/pywfm-run
```

* Development of `pywFM` ([Dockerfile](Dockerfile)): useful if you want to make changes to the repo. `Dockerfile` defaults to bash for easier development.
```shell
# to build image
docker build --rm=true -t jfloff/pywfm-dev .
# to run image
docker run --rm -v "$(pwd)":/home/pywfm-dev -w /home/pywfm-dev -ti jfloff/pywfm-dev
```


### Future work
* Migrate to Python3
* Improve the `save_model` / `load_model` so we can have a more defined init-fit-predict cycle (perhaps we could inherit from [sklearn.BaseEstimator](http://scikit-learn.org/stable/modules/generated/sklearn.base.BaseEstimator.html))
* Include current missing `libFM` options that are not part of `pywFM` model:
  * `meta`: filename for meta information about data set
  * `validation`: filename for validation data (only for SGDA)

*I'm no factorization machine expert, so this library was just an effort to have `libFM` as fast as possible in Python. Feel free to suggest features, enhancements; to point out issues; and of course, to post PRs.*


### License

MIT (see LICENSE.txt file)
