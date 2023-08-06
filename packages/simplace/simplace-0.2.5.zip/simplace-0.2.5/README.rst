Run and control simulations in the simulation framework Simplace.

You need to install the Simplace simulation 
framework http://www.simplace.net/

Example usage:

    >>> import simplace
    >>> sh = simplace.initSimplace('/ws/','/simplacerun/simulation/','/out/')
    >>> simplace.openProject(sh, '/sol/Maize.sol.xml')
    >>> simid = simplace.createSimulation(sh, {'vLUE':3.2,'vSLA':0.023})
    >>> simplace.runSimulations(sh)
    >>> result = resultToList(getResult(sh,'YearlyOutput',simid))
    >>> simplace.closeProject(sh)
    >>> print(result['BiomassModule.Yield'])
    805.45
    
The module requires Java >= 8.0 and an appropriate jpype package (JPype1-py3
for Python 3.x, JPype1 for Python 2.x).
