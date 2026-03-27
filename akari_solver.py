#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 14:23:04 2026

@author: lilyparr
"""

WHITE = -1
BLACK = -2

# Validates that the puzzle input is well-formed and feasible before attempting to solve
def input_checker(puzzle):#Input = the puzzle grid
    Valid = True
    if not isinstance(puzzle, list): #Check the input is a list
        print("Puzzle inputted incorrectly")
        return False
    if Valid and puzzle == []: #Checks the input is non-empty
        print("Puzzle inputted incorrectly")
        return False
    if not isinstance(puzzle[0], list):
        print("Puzzle inputted incorrectly")
        return False
    if puzzle[0] == []:
        print("Puzzle inputted incorrectly")
        return False
    C = len(puzzle[0])
    for row in puzzle :
        if Valid and not isinstance(row,list): #Checks each input in the list is a list
            print("Puzzle inputted incorrectly")
            return False
        if Valid and len(row) != C: # Checks all lists are the same length i.e. rectangular shape
            Valid = False 
            break
        for i in row:
            if Valid and not isinstance(i,int): #Checks if each cell input is an integer
                Valid = False
                break
            if Valid and (i>4 or i<-2) : # Between -2 and 4
                Valid = False
                break
            if not Valid:
                print("Puzzle inputted incorrectly")
                return False
    for y in range(len(puzzle)): # Checks if there is enough available white squares around a numbered black square.
        for x in range(len(puzzle[0])):
            k = puzzle[y][x]
            if 0<=k<=4:
                adj_white = 0
                if y-1 >=0 and puzzle[y-1][x] == WHITE:
                    adj_white += 1
                if y+1 < len(puzzle) and puzzle[y+1][x] == WHITE:
                    adj_white += 1
                if x-1 >=0 and puzzle[y][x-1] == WHITE:
                    adj_white += 1 
                if x+1 < len(puzzle[0]) and puzzle[y][x+1] == WHITE:
                    adj_white += 1
                if adj_white < k:
                    Valid = False
                    break
        if not Valid:
            break
    if not Valid:
        print("Puzzle inputted incorrectly")
    return Valid # Outputs Valid, a Boolean Variable indicating wether the puzzle is correctly formatted

# Creates domain dictionary for each white cell (0 = no bulb, 1 = bulb)
def create_domains(puzzle): # Inputs the puzzle
    domains = {}
    R = len(puzzle)
    C = len(puzzle[0])
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] == WHITE:
                domains[(r,c)] = [0,1]
    return domains #Outputs our dictionary Domains

# Precomputes which white cells are visible from each white cell
def create_visible(puzzle):# Input is the puzzle grid
    R = len(puzzle)
    C = len(puzzle[0])
    visible = {}
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] != WHITE:
                continue
            vis = []
            rr = r - 1
            while rr >= 0 and puzzle[rr][c] == WHITE:
                vis.append((rr, c))
                rr -= 1
            rr = r + 1
            while rr < R and puzzle[rr][c] == WHITE:
                vis.append((rr, c))
                rr += 1
            cc = c - 1
            while cc >= 0 and puzzle[r][cc] == WHITE:
                vis.append((r, cc))
                cc -= 1
            cc = c + 1
            while cc < C and puzzle[r][cc] == WHITE:
                vis.append((r, cc))
                cc += 1
            visible[(r, c)] = vis
    return visible #Output is our dictionary Visible
                
            
# Removes a value from a cell’s domain and checks for contradiction
def remove_option(domains,cell,v):#Inputs Domains, the cell you want to remove an option from, and the value you wish to remove from the cells domain
    if v in domains[cell]:
        domains[cell].remove(v)
        if len(domains[cell]) == 0:
            return False
    return True # Returns True or False as an indicator of whether this removal causes any contradictions

# Creates an updated lit grid based on currently forced bulb placements, where lit informs of a cells illumination status
def update_lit(puzzle, domains, visible): # Inputs the puzzle grid, domains and visible
    C = len(puzzle[0])
    R = len(puzzle)
    lit = [[False for c in range(C)] for r in range(R)]
    for cell,value in domains.items():
        if value == [1]:
            r,c = cell
            lit[r][c] = True
            for rr,cc in visible[cell]:
                lit[rr][cc] = True
    return lit # Returns the created lit

# "Places a bulb" by removing 0 as an option from the domains and updating lit
def place_bulb(puzzle,domains,lit, visible,cell): #Inputs the puzzle grid, domains, the most recent lit, visible and cell you want to place a bulb in
    completed = remove_option(domains, cell, 0)
    if not completed:
        return False,lit
    for v in visible.get(cell, []):
        if v in domains:
            ok = remove_option(domains, v, 1)
            if not ok:
                return False, lit      
    lit = update_lit(puzzle, domains, visible)
    return True, lit # Outputs an indicator of whether this causes any contradictions and the new updated lit
    
# Applies the last free cell rule to force bulb placements (4.2.4 in report)
def last_free_cell(puzzle, domains, lit, visible): #Inputs the puzzle grid , domains,lit and visible
    while True:
        lit = update_lit(puzzle, domains, visible)
        changed_round = False
        for t in list(domains.keys()):
            r, c = t
            if lit[r][c]:
                continue
            candidates = set([t] + visible.get(t, []))
            possible = [u for u in candidates if (u in domains and 1 in domains[u])]
            if len(possible) == 0:
                return False, domains, lit
            if len(possible) == 1:
                last_cell = possible[0]
                ok, lit = place_bulb(puzzle, domains, lit, visible, last_cell)
                if not ok:
                    return False, domains, lit
                changed_round = True
        if not changed_round:
            break
    lit = update_lit(puzzle, domains, visible)
    return True, domains, lit #Ouputs an error indicator and the updated domains and lit

# Converts domain representation into a printable output grid used in the final solver
def domains_to_solution_grid(puzzle, domains):#Inputs the puzzle grid and domains
    R = len(puzzle)
    C = len(puzzle[0])
    out = [[None for x in range(C)] for x in range(R)]
    for r in range(R):
        for c in range(C):
            cell = puzzle[r][c]
            if cell == BLACK:
                out[r][c] = "⬛"
            elif cell == WHITE:
                if domains[(r, c)] == [1]:
                    out[r][c] = "💡"
                else:
                    out[r][c] = "X"
            else:
                out[r][c] = str(cell)

    return out # Returns our nicely formatted output grid

# Applies singular numbered-cell deductions to prune or force neighbours (seen in 4.2.2)
def isolated_numerical_constraints(puzzle, domains, lit, visible): #Inputs the puzzle grid, domains, lit and visible
    R = len(puzzle)
    C= len(puzzle[0])
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] >= 0:
                k = puzzle[r][c]
                neighbours = []
                diagonal_neighbours = []
                free_cells = []
                bulbs = []
                for i in [1,-1]:
                    rr = r+i
                    cc = c+i
                    if 0<= rr < R and puzzle[rr][c] == WHITE:
                        neighbours.append((rr,c))
                    if 0<= cc < C and puzzle[r][cc] == WHITE:
                        neighbours.append((r,cc))
                for i in [1,-1]:
                    for j in [1,-1]:
                        rd = r + i
                        cd = c + j
                        if 0<= rd < R and 0<= cd < C and puzzle[rd][cd] == WHITE:
                            diagonal_neighbours.append((rd,cd))   
                for n in neighbours:
                    if domains[n] == [1]:
                        bulbs.append(n)
                    elif domains[n] == [0,1]:
                        free_cells.append(n)
                bc = len(bulbs)
                fc = len(free_cells)
                mc = k - bc
                if mc == 0:
                    for x in free_cells:
                        ok = remove_option(domains, x, 1)
                        if not ok:
                            return False, domains, lit
                elif mc == fc:
                    for y in free_cells:
                        ok, lit = place_bulb(puzzle, domains, lit, visible, y)
                        if not ok:
                            return False, domains, lit
    lit = update_lit(puzzle, domains, visible)
    return True, domains, lit  #Outputs an error indicator and the updated domains and lit
                        

# Creates the list of white neighbours a cell has (useful for the technique described in 4.2.3)
def adjacent_white_neighbours(puzzle, r, c):# Inputs the puzzle grid and the coordinates of the cell
    R = len(puzzle)
    C = len(puzzle[0])
    neighbours = []
    if r - 1 >= 0 and puzzle[r - 1][c] == WHITE:
        neighbours.append((r - 1, c))
    if r + 1 < R and puzzle[r + 1][c] == WHITE:
        neighbours.append((r + 1, c))
    if c - 1 >= 0 and puzzle[r][c - 1] == WHITE:
        neighbours.append((r, c - 1))
    if c + 1 < C and puzzle[r][c + 1] == WHITE:
        neighbours.append((r, c + 1))
    return neighbours# Output is a list of adjacent white cell coordinates

# Computes the current information about a numbered wall constraint needed for cross_numeric_constraints
def remaining_constraint_info(puzzle, domains, r, c):# Inputs the puzzle grid, domains and the coordinates of the numbered cell
    k = puzzle[r][c]
    neighbours = adjacent_white_neighbours(puzzle, r, c)
    bulbs = []
    free = []
    for cell in neighbours:
        if domains[cell] == [1]:
            bulbs.append(cell)
        elif domains[cell] == [0, 1]:
            free.append(cell)
    missing = k - len(bulbs)
    return missing, set(free) # Outputs the number of bulbs still required and the set of undecided neighbouring cells

# Applies cross-constraint reasoning between pairs of numbered cells (technique described in 4.2.3)
def cross_numeric_constraints(puzzle, domains, lit, visible):# Inputs the puzzle grid, domains, lit grid and visible
    R = len(puzzle)
    C = len(puzzle[0])
    numbered_cells = []
    for r in range(R):
        for c in range(C):
            if 0 <= puzzle[r][c] <= 4:
                numbered_cells.append((r, c))
    for i in range(len(numbered_cells)):
        r1, c1 = numbered_cells[i]
        m1, f1 = remaining_constraint_info(puzzle, domains, r1, c1)
        if m1 < 0 or m1 > len(f1):
            return False, domains, lit
        for j in range(i + 1, len(numbered_cells)):
            r2, c2 = numbered_cells[j]
            if abs(r1 - r2) > 2 or abs(c1 - c2) > 2:
                continue
            m2, f2 = remaining_constraint_info(puzzle, domains, r2, c2)
            if m2 < 0 or m2 > len(f2):
                return False, domains, lit
            if f1 and f1.issubset(f2):
                extra = f2 - f1
                diff = m2 - m1
                if diff < 0 or diff > len(extra):
                    return False, domains, lit
                if diff == 0:
                    for cell in extra:
                        ok = remove_option(domains, cell, 1)
                        if not ok:
                            return False, domains, lit
                elif diff == len(extra):
                    for cell in extra:
                        ok, lit = place_bulb(puzzle, domains, lit, visible, cell)
                        if not ok:
                            return False, domains, lit
            if f2 and f2.issubset(f1):
                extra = f1 - f2
                diff = m1 - m2
                if diff < 0 or diff > len(extra):
                    return False, domains, lit
                if diff == 0:
                    for cell in extra:
                        ok = remove_option(domains, cell, 1)
                        if not ok:
                            return False, domains, lit
                elif diff == len(extra):
                    for cell in extra:
                        ok, lit = place_bulb(puzzle, domains, lit, visible, cell)
                        if not ok:
                            return False, domains, lit
    lit = update_lit(puzzle, domains, visible)
    return True, domains, lit #Outputs an error indicator and the updated domains and lit

# Creates an immutable snapshot of the current domains so changes can be detected during propagation.
def domains_snapshot(domains):
    return {cell: tuple(values) for cell, values in domains.items()}

# Repeatedly applies all propagation rules in sequence until no further
# domain changes occur (fixed point) or a contradiction is detected.
def propagate(puzzle, domains, lit, visible): #Inputs the puzzle grid, domains, lit and visible
    for x in range(1000):
        changed = False
        before = domains_snapshot(domains)
        ok, domains, lit = isolated_numerical_constraints(puzzle, domains, lit, visible)
        if not ok:
            return False, domains, lit
        if domains_snapshot(domains) != before: # Compare domain snapshots before and after each rule to detect progress
            changed = True
        before = domains_snapshot(domains)
        ok, domains, lit = cross_numeric_constraints(puzzle, domains, lit, visible)
        if not ok:
            return False, domains, lit
        if domains_snapshot(domains) != before:
            changed = True
        before = domains_snapshot(domains)
        ok, domains, lit = last_free_cell(puzzle, domains, lit, visible)
        if not ok:
            return False, domains, lit
        if domains_snapshot(domains) != before:
            changed = True
        if not changed: # Stop once a full pass produces no further domain changes
            lit = update_lit(puzzle, domains, visible)
            return True, domains, lit
    lit = update_lit(puzzle, domains, visible)
    return True, domains, lit # outputs an error indicator and the updated domains and lit
        
# Checks whether the current assignment is a complete valid solution.
# This requires all white cells to be lit, no bulbs to see each other,
# and every numbered wall to have exactly the correct number of adjacent bulbs.
def check_solution(puzzle, domains, lit, visible): #Inputs the puzzle, domains, lit and visible
    lit = update_lit(puzzle, domains, visible)
    R = len(puzzle)
    C = len(puzzle[0])
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] == WHITE and not lit[r][c]:
                return False
            if (r, c) in domains and domains[(r, c)] == [1]:
                for v in visible.get((r, c), []):
                    if domains.get(v) == [1]:
                        return False
            if 0<=puzzle[r][c]<=4:
                k = puzzle[r][c]
                neighbours = []
                bulbs = []
                for i in [1,-1]:
                    rr = r+i
                    cc = c+i
                    if 0<= rr < R and puzzle[rr][c] == WHITE:
                        neighbours.append((rr,c))
                    if 0<= cc < C and puzzle[r][cc] == WHITE:
                        neighbours.append((r,cc))
                for n in neighbours:
                    if domains[n] == [1]:
                        bulbs.append(n)
                if k != len(bulbs):
                    return False
    return True # Returns True if the current assignment is a complete valid solution and False otherwise
           
# Checks whether the current partial assignment is still consistent.
# Unlike check_solution, this does not require all cells to be decided or lit,
# only that no contradiction has already been created.
def validity(puzzle, domains, lit, visible): # Inputs the puzzle grid, domains, lit and visible
    lit = update_lit(puzzle, domains, visible)
    R = len(puzzle)
    C = len(puzzle[0])
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] == WHITE:
                if domains[(r,c)] == []:
                    return False
                elif (not lit[r][c]) and (domains[(r, c)] == [0]):
                    candidates = [(r, c)] + visible.get((r, c), [])
                    possible = [v for v in candidates if (v in domains) and (domains[v] != [0])]
                    if len(possible) == 0:
                        return False
            if 0<=puzzle[r][c]<=4:
                k = puzzle[r][c]
                neighbours = []
                bulbs = []
                free = []
                for i in [1,-1]:
                    rr = r+i
                    cc = c+i
                    if 0<= rr < R and puzzle[rr][c] == WHITE:
                        neighbours.append((rr,c))
                    if 0<= cc < C and puzzle[r][cc] == WHITE:
                        neighbours.append((r,cc))
                for n in neighbours:
                    if domains[n] == [0,1]:
                        free.append(n)
                    if domains[n] == [1]:
                        bulbs.append(n)
                if len(bulbs)>k:
                    return False
                if len(bulbs)+len(free)<k:
                    return False
            if (r, c) in domains and domains[(r, c)] == [1]:
                for v in visible.get((r, c), []):
                    if domains.get(v) == [1]:
                        return False
    return True # Outputs True if the current assignements are valid and False otherwise

               
# Computes how many numbered constraints are adjacent to a cell
def constraint_degree(puzzle, cell):# Input is the puzzle grid and the cell you want to gain the information about
    r = cell[0]
    c = cell[1]
    R = len(puzzle)
    C = len(puzzle[0])
    degree = 0
    if r - 1 >= 0:
        if 0 <= puzzle[r - 1][c] <= 4:
            degree += 1
    if r + 1 < R:
        if 0 <= puzzle[r + 1][c] <= 4:
            degree += 1
    if c - 1 >= 0:
        if 0 <= puzzle[r][c - 1] <= 4:
            degree += 1
    if c + 1 < C:
        if 0 <= puzzle[r][c + 1] <= 4:
            degree += 1
    return degree # Returns the variable degree representing how many numbered constraints there are adjacent to a cell
              
#Will be for our search heuristics for the backtracker, chooses a guess cell based on tightest numeric constraint heuristic
def choose_from_constraints(puzzle,domains): # Input is the puzzle grid and domains
    R = len(puzzle)
    C = len(puzzle[0])
    best_score= None
    best_free_cells = None
    for r in range(R):
        for c in range(C):
            k = puzzle[r][c]
            if not 0<=k<=4:
                continue
            neighbours = []
            bulbs = []
            free = []
            for i in [1,-1]:
                rr = r+i
                cc = c+i
                if 0<= rr < R and puzzle[rr][c] == WHITE:
                    neighbours.append((rr,c))
                if 0<= cc < C and puzzle[r][cc] == WHITE:
                    neighbours.append((r,cc))
            for n in neighbours:
                if domains[n] == [0,1]:
                    free.append(n)
                if domains[n] == [1]:
                    bulbs.append(n)
            mc =k-len(bulbs)
            fc = len(free)
            if mc <= 0:
                continue
            if fc == 0:
                continue
            slack =fc -mc
            score = (fc,slack,-k) # Score walls lexicographically by (fewest free neighbours, smallest slack, largest k)
            if best_score is None or score< best_score:
                best_score = score
                best_free_cells = free
    if best_free_cells == None:
        return None
    best_cell = None
    best_degree = -1
    for cell in best_free_cells:
        deg = constraint_degree(puzzle, cell)
        if best_cell is None or deg > best_degree:
            best_cell = cell
            best_degree = deg
    return best_cell # Output is the chosen cell based on this heuristic
    
# Returns all undecided cells that could still place a bulb and illuminate the target cell.
def lighting_candidates_for_cell(domains, visible, cell): 
    candidates = []
    if cell in domains:
        if 1 in domains[cell]:
            candidates.append(cell)
    if cell in visible:
        for v in visible[cell]:
            if v in domains:
                if 1 in domains[v]:
                    candidates.append(v)
    return candidates
    
# Chooses a guess cell by selecting an unlit white cell with the fewest remaining possible 
#lighting candidates, then choosing the candidate that would illuminate the largest region.
def choose_from_visibility(puzzle, domains, lit, visible):
    lit = update_lit(puzzle, domains, visible)
    R = len(puzzle)
    C = len(puzzle[0])
    best_target = None
    best_count = None
    best_candidates = None
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] != WHITE:
                continue
            if lit[r][c]:
                continue
            cell = (r, c)
            candidates = lighting_candidates_for_cell(domains, visible, cell)
            count = len(candidates)
            if count == 0:
                return None  
            if best_target is None or count < best_count:
                best_target = cell
                best_count = count
                best_candidates = candidates
    if best_target is None:
        return None
    best_guess = None
    best_vis_size = -1
    for cand in best_candidates: # Prefer candidates that would illuminate the largest visible region
        size = 0
        if cand in visible:
            size = len(visible[cand])
        if best_guess is None or size > best_vis_size:
            best_guess = cand
            best_vis_size = size
    return best_guess

## Chooses the next branching cell by first trying the constraint-based heuristic,
# then the visibility-based heuristic, and finally falling back to any undecided cell.
def choose_guess_cell(puzzle, domains, lit, visible):
    cell = choose_from_constraints(puzzle, domains)
    if cell is not None:
        return cell
    cell = choose_from_visibility(puzzle, domains, lit, visible)
    if cell is not None:
        return cell
    for cell, d in domains.items():
        if d == [0,1]:
            return cell
    return None

# Deep-copies the domains dictionary for safe backtracking
def copy_domains(domains):
    new_domains = {}
    for cell, d in domains.items():
        new_domains[cell] = d[:]
    return new_domains

# Deep-copies the lit grid for safe backtracking
def copy_lit(lit):
    return [row[:] for row in lit]

# Checks whether every domain has been fully decided
def domains_fully_decided(domains):
    for cell in domains:
        d = domains[cell]
        if d != [0] and d != [1]:
            return False
    return True

# Recursively solves the puzzle by alternating propagation and branching.
#We output a error indicator, domains (which is solved if first variable is TRUE), lit and 
# an indicator of whether backtracking was used 
def backtrack_solve(puzzle, domains, lit, visible):
    ok, domains, lit = propagate(puzzle, domains, lit, visible) # First applies propagation to simplify the current state.
    if not ok:
        return False, domains, lit, False
    if check_solution(puzzle, domains, lit, visible):# If the puzzle is solved, returns the solution.
        return True, domains, lit, False
    if domains_fully_decided(domains):
        return False, domains, lit, False
    cell = choose_guess_cell(puzzle, domains, lit, visible) # Otherwise chooses a guess cell, branches on bulb / no-bulb, and backtracks on failure.
    if cell is None:
        return False, domains, lit, False
    d1 = copy_domains(domains)
    lit1 = copy_lit(lit)
    ok1, lit1 = place_bulb(puzzle, d1, lit1, visible, cell) # First branch: try placing a bulb in the chosen cell
    if ok1:
        if validity(puzzle, d1, lit1, visible):
            solved, sol_domains, sol_lit, used_bt = backtrack_solve(puzzle, d1, lit1, visible)
            if solved:
                return True, sol_domains, sol_lit, True
    d2 = copy_domains(domains)
    lit2 = copy_lit(lit)
    ok2 = remove_option(d2, cell, 1) # Second branch: try forcing the chosen cell to be empty
    if ok2:
        if validity(puzzle, d2, lit2, visible):
            solved, sol_domains, sol_lit, used_bt = backtrack_solve(puzzle, d2, lit2, visible)
            if solved:
                return True, sol_domains, sol_lit, True 
    return False, domains, lit, True
                
def print_solution_grid(grid):
    for row in grid:
        print(" ".join(row))
    print()

# Main solver function.
# Validates the input puzzle, initialises all data structures, runs the solver, and prints the 
#final solution grid if a solution is found.
def solve_akari(puzzle):
    if not input_checker(puzzle):
        print("Invalid puzzle input.")
        return False, False
    domains = create_domains(puzzle)
    visible = create_visible(puzzle)
    lit = update_lit(puzzle, domains, visible)
    solved, domains, lit, used_backtracking = backtrack_solve(puzzle, domains, lit, visible)
    if not solved:
        print("No solution found.")
        return False, used_backtracking
    grid = domains_to_solution_grid(puzzle, domains)
    print_solution_grid(grid)
    return True, grid, used_backtracking       

    

     
                            

                    
                        
                        
                        
                        
                        
                
                
                
            

      

 
          


 

    