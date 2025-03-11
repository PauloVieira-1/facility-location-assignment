# -*- coding: utf-8 -*-
from pulp import LpProblem, LpMaximize, LpMinimize, LpVariable, GLPK, lpSum


BIG_M = 100000

def flp1(budget, coor_cust, coor_fac):
    """Solving the minmax facility location problem (MM_FLP).

    This function generates the MM_FLP formulation in PuLP
    and solves it using the GLPK solver.

    Parameters
    ----------
    budget       : number of facilities to open
    coor_cust    : list of tuples with the coordinates of each customer
    coor_fac     : list of tuples with the coordinates of each facility

    Returns
    -------
    obj_val      : the objective value after optimization
    setups       : a list with the setup decision per facility
    """


    nr_cust = len(coor_cust)
    nr_fac = len(coor_fac)

    model = LpProblem("MinMaxDistance", LpMinimize)

    ### Decision Variables ###

    d = [[0]*nr_fac for _ in range(nr_cust)] # represents the distance between each customer and facility 
    
    for i in range(nr_cust):
        for j in range(nr_fac): 
            d[i][j] = ((coor_cust[i][0] - coor_fac[j][0])**2 + (coor_cust[i][1] - coor_fac[j][1])**2)**0.5

    x = {i : LpVariable(name = f"x1_{i}", cat="Binary") for i in range(nr_cust)} # represents decison to open facility for customer or not 

    ### Model ###

    model += lpSum(d[i][j] * x[i] for i in range(nr_cust) for j in range(nr_fac)) 


    ### Constraints ###

    model += lpSum(x[i] for i in range(nr_fac)) == budget
    model += lpSum(x[i] - BIG_M) <= 0

    # Solve the model
    # Default return values = No solution found
    obj_val = 0
    setups = [0]*nr_fac
    if model is None:
        # You did not decide to develop a optimization model
        return obj_val, setups
    # Solve the constructed model with GLPK within 10 seconds
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))
    if model.status != 1:
        # Model did not result in an optimal solution
        return model.status, setups
    # Retrieve the objective value
    obj_val = model.objective.value()
    # Retrieve the facilities that you decide to open

    if model.status != 1:
        return model.status
    
    obj_val = model.objective.value()

    for i in range(nr_cust):
        setups[i] = int(x[i].value())

    return obj_val, setups

def flp2(cost_f, subs_fixed, subs_access, coor_cust, coor_fac):
    """Solving the profit maximizing facility location problem (PM_FLP).

    This function generates the PM_FLP formulation in PuLP
    and solves it using the GLPK solver.

    Parameters
    ----------
    cost_f       : cost to open a facility [EUR]
    subs_fixed   : fixed part of the subscription fee [EUR]
    subs_access  : compensation for the distance to the facility [EUR/km]
    coor_cust    : list of tuples with the coordinates of each customer
    coor_fac     : list of tuples with the coordinates of each facility

    Returns
    -------
    obj_val      : the objective value after optimization
    setups       : a list with the setup decision per facility
    """

    # Define parameters
    nr_cust = len(coor_cust)
    nr_fac = len(coor_fac)
    # YOUR CODE HERE

    # Declare model
    model = None    # TEMPORARY: replace with your model declaration

    # Add decision variables
    # YOUR CODE HERE

    # Add the objective function
    # YOUR CODE HERE

    # Add the constraints to the model
    # YOUR CODE HERE

    # Solve the model
    # Default return values = No solution found
    obj_val = 0
    setups = [0]*nr_fac
    if model is None:
        # You did not decide to develop a optimization model
        return obj_val, setups
    # Solve the constructed model with GLPK within 10 seconds
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))
    if model.status != 1:
        # Model did not result in an optimal solution
        return model.status, setups
    # Retrieve the objective value
    obj_val = model.objective.value()
    # Retrieve for each facility the customers that you decide to offer a subscription
    # YOUR CODE HERE

    return obj_val, setups

def flp3(cap_f, subs_fixed, subs_access, coor_cust, coor_fac):
    """Solving the profit maximizing capacitated facility location problem
    over a planning horizon (PMT_CFLP).

    This function generates the PMT_CFLP formulation in PuLP
    and solves it using the GLPK solver.

    Parameters
    ----------
    cap_f        : capacity of an open facility [units]
    subs_fixed   : fixed part of the subscription fee [EUR/period]
    subs_access  : compensation for the distance to the facility [EUR/km.period]
    coor_cust    : list of tuples with the coordinates of each customer
    coor_fac     : list of tuples with the coordinates of each facility

    Returns
    -------
    obj_val      : the objective value after optimization
    setups       : a list with the setup decision per period
    """

    # Define parameters
    nr_cust = len(coor_cust)
    nr_fac = len(coor_fac)
    horizon = nr_fac
    # YOUR CODE HERE

    # Declare model
    model = None    # TEMPORARY: replace with your model declaration

    # Add decision variables
    # YOUR CODE HERE

    # Add the objective function
    # YOUR CODE HERE

    # Add the constraints to the model
    # YOUR CODE HERE

    # Solve the model
    # Default return values = No solution found
    obj_val = 0
    setups = [-1]*horizon
    if model is None:
        # You did not decide to develop a optimization model
        return obj_val, setups
    # Solve the constructed model with GLPK within 10 seconds
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))
    if model.status != 1:
        # Model did not result in an optimal solution
        return model.status, setups
    # Retrieve the objective value
    obj_val = model.objective.value()
    # Retrieve the sequence in which you open the facilities
    # YOUR CODE HERE

    return obj_val, setups

if __name__ == '__main__':
    # Below you can experiment with your functions
    cust_data = [(2, 3), (3, 6), (1, 11), (5, 4), (7, 1),
                 (20, 5), (25, 7), (14, 25), (20, 10), (15, 21),
                 (9, 21), (4, 16), (6, 18), (8, 24), (12, 15),
                 (5.5, 7), (2.5, 19), (11, 1), (22, 13), (17, 6)]
    fac_data = [(12, 1), (3, 15), (20, 10), (2, 2)]
    min_cost_a, setups_a = flp1(2, cust_data, fac_data)
    print(f"MM_FLP solution: costs={min_cost_a},"
          +f" with setups {setups_a}")

    cust_data = [(2, 3), (3, 6), (1, 11), (5, 4), (7, 1),
                 (20, 5), (25, 7), (14, 25), (20, 10), (15, 21),
                 (9, 21), (4, 16), (6, 18), (8, 24), (12, 15),
                 (5.5, 7), (2.5, 19), (11, 1), (22, 13), (17, 6)]
    fac_data = [(12, 1), (3, 15), (20, 10), (2, 2)]
    profit_b, setups_b = flp2(150, 50, 3, cust_data, fac_data)
    print(f"PM_FLP solution: profit={profit_b},"
          +f" with {setups_b} subscriptions")

    cust_data = [(2, 3), (3, 6), (1, 11), (5, 4), (7, 1),
                 (20, 5), (25, 7), (14, 25), (20, 10), (15, 21),
                 (9, 21), (4, 16), (6, 18), (8, 24), (12, 15),
                 (5.5, 7), (2.5, 19), (11, 1), (22, 13), (17, 6)]
    fac_data = [(12, 1), (3, 15), (20, 10), (2, 2)]
    # fac_data = [(23, 4), (16, 25), (2, 2)]
    profit_c, setups_c = flp3(5, 15, 2, cust_data, fac_data)
    print(f"PMT_CFLP solution: profit={profit_c},"
          +f" with setup sequence {setups_c}")
