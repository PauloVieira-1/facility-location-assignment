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

    model = LpProblem("MM_FLP", LpMinimize)

    ### Decision Variables ###
    x = {j: LpVariable(f"x_{j}", cat="Binary") for j in range(nr_fac)}

    y = {(i, j): LpVariable(f"y_{i}_{j}", cat="Binary") for i in range(nr_cust) for j in range(nr_fac)}

    d = [[abs(coor_cust[i][0] - coor_fac[j][0]) + abs(coor_cust[i][1] - coor_fac[j][1]) for j in range(nr_fac)] for i in range(nr_cust)]

    D_max = LpVariable("D_max", lowBound=0)  

    model += D_max  

    ### Constraints ###

    for i in range(nr_cust):
        for j in range(nr_fac):
            model += d[i][j] * y[i, j] <= D_max 
            
    for i in range(nr_cust):
        model += lpSum(y[i, j] for j in range(nr_fac)) == 1

    for i in range(nr_cust):
        for j in range(nr_fac):
            model += y[i, j] <= x[j]
    
    model += lpSum(x[j] for j in range(nr_fac)) == budget

    for i in range(nr_cust):
        model += lpSum(d[i][j] * y[i, j] for j in range(nr_fac)) <= D_max


    # Default return values = No solution found
    obj_val = 0
    setups = [0]*nr_fac
    if model is None:
        return obj_val, setups
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))
    if model.status != 1:
        return model.status, setups
    obj_val = model.objective.value()

    if model.status != 1:
        return model.status
    
    obj_val = model.objective.value()
    setups = [int(x[j].value()) for j in range(nr_fac)]

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
    
    nr_cust = len(coor_cust)
    nr_fac = len(coor_fac)

    model = LpProblem("PM_FLP", LpMaximize)

    ### Decision Variables ###

    x = {j: LpVariable(f"x_{j}", cat="Binary") for j in range(nr_fac)}
    y = {(i, j): LpVariable(f"y_{i}_{j}", cat="Binary") for i in range(nr_cust) for j in range(nr_fac)}

    d = [[abs(coor_cust[i][0] - coor_fac[j][0]) + abs(coor_cust[i][1] - coor_fac[j][1]) for j in range(nr_fac)] for i in range(nr_cust)]

    model += (
        lpSum((subs_fixed - subs_access * d[i][j]) * y[i, j] for i in range(nr_cust) for j in range(nr_fac))
        - lpSum(cost_f * x[j] for j in range(nr_fac))
    )

    ### Constraints ###

    for j in range(nr_fac):
        model += lpSum((subs_fixed - subs_access * d[i][j]) * y[i, j] for i in range(nr_cust)) - cost_f * x[j] >= 0

    for i in range(nr_cust):
        model += lpSum(y[i, j] for j in range(nr_fac)) <= 1

    for i in range(nr_cust):
        for j in range(nr_fac):
            model += y[i, j] <= x[j]


    # Default return values if no solution is found
    obj_val = 0
    setups = [0]*nr_fac

    if model is None:
        return obj_val, setups
    
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))

    if model.status != 1:
        return model.status, setups
    
    obj_val = model.objective.value()

    if model.status != 1:
        return model.status

    obj_val = model.objective.value()


    for i in range(nr_cust):
        for j in range(nr_fac):
            if y[i, j].varValue is not None and int(y[i, j].varValue) == 1:
                setups[j] += 1

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

    nr_cust = len(coor_cust)
    nr_fac = len(coor_fac)
    horizon = nr_fac

    model = LpProblem("PMT_CFLP", LpMaximize)

    ### Decision Variables ###

    facility_open = {j: LpVariable(f"x_{j}", cat="Binary") for j in range(nr_fac)}
    customer_assigned = {(i, j, k): LpVariable(f"y_{i}_{j}_{k}", cat="Binary") for i in range(nr_cust) for j in range(nr_fac) for k in range(horizon)}
    fraction_assigned = {(i, j, k): LpVariable(f"z_{i}_{j}_{k}", cat="Continuous", lowBound=0, upBound=1) for i in range(nr_cust) for j in range(nr_fac) for k in range(horizon)}

    d = [[abs(coor_cust[i][0] - coor_fac[j][0]) + abs(coor_cust[i][1] - coor_fac[j][1]) for j in range(nr_fac)] for i in range(nr_cust)]

    model += lpSum((subs_fixed - subs_access * d[i][j]) * fraction_assigned[i, j, k] for i in range(nr_cust) for j in range(nr_fac) for k in range(horizon))
    
    ### Constraints ###

    # Ensure each customer is assigned to at most one facility per period
    for i in range(nr_cust):
        model += lpSum(customer_assigned[i, j, k] for j in range(nr_fac) for k in range(horizon)) <= 1

    # Ensure a customer is only assigned to an open facility
    for i in range(nr_cust):
        for j in range(nr_fac):
            for k in range(horizon):
                model += customer_assigned[i, j, k] <= facility_open[j]

    # Ensure the total assigned fraction does not exceed facility capacity when open
    for j in range(nr_fac):
        model += lpSum(fraction_assigned[i, j, k] for i in range(nr_cust) for k in range(horizon)) <= cap_f * facility_open[j]

    # Default return values if no solution is found
    obj_val = 0
    setups = [0] * nr_fac

    if model is None:
        return obj_val, setups
    
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))

    if model.status != 1:
        return model.status, setups
    
    obj_val = model.objective.value()

    if model.status != 1:
        return model.status

    obj_val = model.objective.value()


    facility_open_period = {} 
    
    for j in range(nr_fac):
        for k in range(horizon):
            if facility_open[j].varValue is not None and int(facility_open[j].varValue) == 1:
                if j not in facility_open_period:
                    facility_open_period[j] = k
                    setups[k] = j  
                    break

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
