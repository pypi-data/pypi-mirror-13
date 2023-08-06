"""
Runs F2PY version of the supersmoother and compares to the Python version. 

For verification only. 
"""
import numpy.random

import supsmu

from ace import supersmoother

numpy.random.seed(4144674543) # for consistency

def runsupsmu():
    noise = numpy.random.standard_normal(100) / 3.0

    x = numpy.linspace(0, 1, 100)
    y = 4 * x ** 2 + noise
    weight = numpy.ones(100)
    results = numpy.zeros(100)
    sc = numpy.zeros((100, 7))

    supsmu.supsmu(x, y, weight, 1, 0.0, 1.0, results, sc)
    print(results)


    smoother = supersmoother.SuperSmoother()
    smoother._bass_enhancement = 1.0
    smoother.specify_data_set(x, y)
    smoother.compute()

    import pylab
    pylab.plot(x, results)
    pylab.plot(x, y, '.')
    pylab.plot(smoother.x, smoother.smooth_result, label='Nick smoother')
    pylab.legend()
    pylab.show()


if __name__ == '__main__':
    runsupsmu()




