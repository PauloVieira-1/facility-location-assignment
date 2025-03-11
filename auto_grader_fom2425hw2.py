# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 10:35:38 2024

@author: rbroekme
"""
import sys
import os
from contextlib import contextmanager
import pandas as pd
from pylint import lint
from importlib.metadata import version

HOMEWORK = "fom2425hw2"
NR_TESTS = 3                # Will increase during final grading

@contextmanager
def suppress_stdout():
    """ Function to suppress output to console."""
    with open(os.devnull, "w", encoding="utf-8") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def unit_test(test_module, test_nr):
    """ Unit tester."""
    # Init return values
    points = 0
    obj_val = 0
    setups = []
    try:
        if test_nr == 0:        # Given example
            cust_data = [(2, 3), (3, 6), (1, 11), (5, 4), (7, 1),
                         (20, 5), (25, 7), (14, 25), (20, 10), (15, 21),
                         (9, 21), (4, 16), (6, 18), (8, 24), (12, 15),
                         (5.5, 7), (2.5, 19), (11, 1), (22, 13), (17, 6)]
            fac_data = [(12, 1), (3, 15), (20, 10), (2, 2)]
            obj_val, setups = test_module.flp1(2, cust_data, fac_data)
            corr_setups = [1, 1, 0, 0]
            corr_obj_val = 21
        if test_nr == 1:        # Given example
            cust_data = [(2, 3), (3, 6), (1, 11), (5, 4), (7, 1),
                         (20, 5), (25, 7), (14, 25), (20, 10), (15, 21),
                         (9, 21), (4, 16), (6, 18), (8, 24), (12, 15),
                         (5.5, 7), (2.5, 19), (11, 1), (22, 13), (17, 6)]
            fac_data = [(12, 1), (3, 15), (20, 10), (2, 2)]
            obj_val, setups = test_module.flp2(150, 50, 3, cust_data, fac_data)
            corr_setups = [0, 11, 6, 0]
            corr_obj_val = 130
        if test_nr == 2:        # Given example
            cust_data = [(2, 3), (3, 6), (1, 11), (5, 4), (7, 1),
                         (20, 5), (25, 7), (14, 25), (20, 10), (15, 21),
                         (9, 21), (4, 16), (6, 18), (8, 24), (12, 15),
                         (5.5, 7), (2.5, 19), (11, 1), (22, 13), (17, 6)]
            fac_data = [(12, 1), (3, 15), (20, 10), (2, 2)]
            obj_val, setups = test_module.flp3(5, 15, 2, cust_data, fac_data)
            corr_setups = [2, 3, 1, 0]
            corr_obj_val = 243
        if int(obj_val) == corr_obj_val:
            points += 0.5
        if setups == corr_setups:
            points += 0.5
        return points, obj_val, setups, None
    except Exception as test_error:
        return 0, obj_val, setups, str(test_error)

def grade_submissions():
    """ Code to check submitted file with unit tests. """

    # Check version pylint
    print(f"Current pylint version: {version('pylint')}")
    # print(f"Current GLPK version: {version('glpk_cmd')}")
    # Clear the pylint cache
    lint.pylinter.MANAGER.astroid_cache = {}
    
    # Collect the student submissions from the current directory
    files = []
    for file in os.listdir():
        if file.endswith(".py"):
            # Jump over the auto grader file
            if file == 'auto_grader_' + HOMEWORK + '.py':
                continue
            files.append(os.path.splitext(file)[0])

    files.sort(reverse=False)
    print('Files to process:',  len(files))

    # Dataframe with output of the functions per student group
    df_res = pd.DataFrame(files, columns=['FileName'])
    if len(files) > 10:
        # Add columns for group IDs (only for batch grading)
        df_res["Group"] = ""
        df_res["ID1"] = ""
        df_res["ID2"] = ""
    # Add column for the grades
    df_res["Grade"] = 0
    df_res["Static"] = 0.
    df_res["Dynamic"] = 0
    # Add columns for each test
    for test_nr in range(NR_TESTS):
        df_res[f"U{test_nr}_pt"] = 0
        df_res[f"U{test_nr}_return_0"] = ""
        df_res[f"U{test_nr}_return_1"] = ""
        df_res[f"U{test_nr}_error"] = ""

    file_nr = 0
    while file_nr < len(files):
        if len(files) > 10:
            # Only needed for the batch grading
            group_data = files[file_nr].split("_")
            df_res.at[file_nr, "Group"] = group_data[0]
            df_res.at[file_nr, "ID1"] = group_data[1]
            df_res.at[file_nr, "ID2"] = group_data[2]

        # Get student file
        group_module = __import__(files[file_nr])

        # Init scores
        static_score = 0.
        dynamic_score = 0

        with suppress_stdout():
            try:
                results = lint.Run([files[file_nr] + '.py'], do_exit=False)
                static_score = results.linter.stats.global_note
            except UnicodeError:
                # Unknown diacriticals in student names
                static_score = -1.         # Requires attention!
        # Write static score
        df_res.at[file_nr, "Static"] = static_score

        # Execute unit tests
        for test_nr in range(NR_TESTS):
            points, return_0, return_1, error_str = unit_test(group_module, test_nr)
            df_res.at[file_nr, f"U{test_nr}_pt"] = points
            df_res.at[file_nr, f"U{test_nr}_return_0"] = return_0
            df_res.at[file_nr, f"U{test_nr}_return_1"] = return_1
            df_res.at[file_nr, f"U{test_nr}_error"] = error_str
            dynamic_score += points
        # Write dynamic score
        df_res.at[file_nr, "Dynamic"] = dynamic_score

        # Write grade
        df_res.at[file_nr, 'Grade'] = round(0.2*static_score
                                            + 8*(dynamic_score/NR_TESTS), 1)

        file_nr += 1

    # Write the results to Excel
    df_res.to_excel(HOMEWORK + "_results.xlsx")

if __name__ == '__main__':
    grade_submissions()
