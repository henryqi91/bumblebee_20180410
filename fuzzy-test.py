import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

def mf_trimf(left_bound,right_bound,data):
    center_x = (right_bound - left_bound)/2
    if data < center_x:
        k = (0 - 1) / (left_bound - center_x)
        b = (0 - k * left_bound)
        return k * data + b
    else:
        k = (1 - 0) / (center_x - right_bound)
        b = (1 - k * center_x)
        return k * data + b
    pass

# res = []
x_s = []
y_s = []
left = 1
right = 107
for x in range(1, 107):
    y = mf_trimf(left_bound=0,right_bound=107.5,data=x)
    x_s.append(x)
    y_s.append(y)

# plt.scatter(x,y)
plt.plot(y_s)
plt.show()

def mf_gaussian(center,scale,mean):

    pass

def mamdani_inference():

    pass
