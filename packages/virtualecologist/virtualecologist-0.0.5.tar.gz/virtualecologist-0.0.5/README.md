===========
Virtual Ecologist
===========

A set of tools to optimize transect length in an ecological monitoring program.
The primary goal is to reduce transect length without losing the power to
detect a difference between surveys (e.g. seasonal surveys).  

These tools assume that the data are collected from transects (which can be
 variable in length), and each transect contains sequential data collection points.
E.g. A 50 meter transect with 1m2 plots spaced 4 meters apart.   

It also assumes that you are assessing grouped data (e.g. functional groups,
lifeforms, guilds or a custom list of groupings used to cluster species) at an
individual location. For example, lifeforms (forbs, trees) in a remnant forest.


Installation
-----------
```bash
# clone repo
https://github.com/rayblick/Virtual-Ecologist.git
# cd in to root directory
python setup.py install
```

Usage
------------

```python
# Import library
from virtualecologist import virtualecologist as ve
# instantiate virtualecologist
# requires 2 datasets...
example = ve.VirtualEcologist("virtualecologist/data/pilotdata.csv",
                              "virtualecologist/data/fulldata.csv")
# uses pilot data to generate mean error rate
example.train_observer()
# match main data to the mean error rate
# if pilot data not given, you assume a 10% error rate for all groups
example.match_full_dataset()
# print to console a table of groups and error rates
# execution here returns error rate
example.print_table(example.mse_output)
# Main function
# isolate the location and the lifeform to investigate
# produces a figure showing number of plots to reduce
example.calc_mmd(site="swamp", lifeform="shrub")
# generates a stacked barchart for all sites and lifeforms in the dataset
example.create_barchart()
# get the probability density function for your selected lifeform
example.create_pdf_figure()
```

Example
==============

###Sampling design
--------------
Location: single wetland  
Target habitat: hydrological gradient  
Design: stratified-random transects (of variable length)  
Sampling: 1m plots every 4m  
Lifeform: damp tolerant terrestrial plants (Tda)    

**Thresholds:**   

    + Minimum detectable difference of 10%  
    + All transects have to keep at least 4 plots each  


![wc](https://raw.github.com/rayblick/Virtual-Ecologist/master/img/transects2014.jpg)


###Get started
-------------
```python
from virtualecologist import virtualecologist as ve
wc = ve.VirtualEcolgist("path/to/pilotdata.csv","path/to/fulldata.csv")
```

###Train your Virtual Ecolgist:
-------------
```python
wc.train_observer()
# find all cases that are not trained
wc.match_full_dataset()
# print mean square error for each life form
wc.print_table(wc.mse_output)
```

**Tabulated output:**
-------------
```markdown
+----+----------+---------+------------+
| ID | Lifeform |   MSE   | Pilot data |
+----+----------+---------+------------+
| 1  |   ARp    |  22.333 |    yes     |
| 2  |   ATe    | 315.452 |    yes     |
| 3  |   ATl    |  27.273 |    yes     |
| 4  |   ATw    |  306.5  |    yes     |
| 5  |   Ate    | 152.412 |     no     |
| 6  |  T/ATe   | 152.412 |     no     |
| 7  |    T     |  49.021 |    yes     |
| 8  |   Tdr    | 292.731 |    yes     |
| 9  |   Tda    |  53.576 |    yes     |
+----+----------+---------+------------+
```

###Calculate minimum detectable difference
--------------
```python
wc.calc_mmd(site="West Carne", lifeform="Tda")

# console printout
#>>> Max number of plots you can drop (if each transect still has 4 plots) is: 1.57
#>>> The trigger value was exceeded when the minimum number of plots per transect was less than: 17.0

```
The console print out summarizes the figure. In this example I can remove 1.57 plots
from each transect before the minimum detectable difference exceeds 10%. Importantly,
these results are associated with finding a minimum of 17 plots with at least
one species from the target group (Tda).

Note the dashed line in the figure which shows the number of plots with at least one species
from Tdr. Unsurprisingly, as I reduce plots from each transect, the minimum
detectable difference between my observations and the Virtual Ecologist increases
(and so does variability).

![mmd](https://raw.github.com/rayblick/Virtual-Ecologist/master/img/mdd.png)


###Produce probability density function
--------------
```python
# This will produce one figure for each group of plants
wc.create_pdf_figure()
```
![pdf](https://raw.github.com/rayblick/Virtual-Ecologist/master/img/pdf.png)
