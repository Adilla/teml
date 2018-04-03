# Ivie
Declarative intermediate language for program optimizations


## 1 - Dependencies

### Redbaron

Documentation: https://redbaron.readthedocs.io/en/latest/#

Github repository: https://github.com/PyCQA/redbaron

#### Installation

```
pip install redbaron
```

### PyCParser

Github repository: https://github.com/eliben/pycparser

#### Installation

```
pip install pycparser
```

## 2 - How to generate code with Ivie

#### Generate C code from Ivie source

```
python ivic.py FILE_NAME.ivie
```     

#### Generate Ivie code from C source

```
python civi.py FILE_NAME.c
```
