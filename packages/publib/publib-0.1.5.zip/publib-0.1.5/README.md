# Publib

*Erwan Pannier - EM2C Laboratory, CentraleSupélec / CNRS UPR 288*

## Description

Produce publication-level quality images on top of Matplotlib, with a 
simple call to couple functions at the start and end of your script. 

[Project GitHub page](https://github.com/rainwear/publib)

For similar librairies, see
[seaborn](http://stanford.edu/~mwaskom/software/seaborn/), which also
add neat high-end API to Matplotlib function calls.

## Use

At the beginning of the script, call:

``` {.sourceCode .python}
set_style()
```

After each new axe is plotted, call:

``` {.sourceCode .python}
fix_style()
```

Note that importing publib will already load the basic style.

A few more styles ('poster', 'article', etc.) can be selected with the
function `set_style()`

Because some matplotlib parameters cannot be changed before the lines
are plotted, they are called through the function `fix_style()` which:

-   changes the minor ticks

-   remove the spines

-   turn the legend draggable by default

## Examples

``` {.sourceCode .python}
#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import publib
a = np.linspace(0,6.28)
plt.plot(a,np.cos(a))   # plotted by publib 'default' style
plt.show()

publib.set_style('article')
plt.plot(a,a**2)
publib.fix_style('article')
plt.show()
```

Run the _test() routine in publib.py for more examples. 
