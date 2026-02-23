#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 14:23:04 2026

@author: lilyparr
"""
WHITE = -1
BLACK = -2

# Validates that the puzzle input is well-formed and feasible before solving
def input_checker(puzzle):
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
        if Valid and len(row) != C: # Checks all lists are the same length i.e. rectangualar shape
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
    return Valid

# Creates domain dictionary for each white cell (0 = no bulb, 1 = bulb)
def create_domains(puzzle): 
    domains = {}
    R = len(puzzle)
    C = len(puzzle[0])
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] == WHITE:
                domains[(r,c)] = [0,1]
    return domains

# Precomputes which white cells are visible from each white cell
def create_visible(puzzle):
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
    return visible
                
            
# Removes a value from a cell’s domain and checks for contradiction
def remove_option(domains,cell,v):
    if v in domains[cell]:
        domains[cell].remove(v)
        if len(domains[cell]) == 0:
            return False
    return True

# Updates the lit grid based on currently forced bulb placements
def update_lit(puzzle,domains, visible):
    C = len(puzzle[0])
    R = len(puzzle)
    lit = [[False for c in range(C)] for r in range(R)]
    for cell,value in domains.items():
        if value == [1]:
            r,c = cell
            lit[r][c] = True
            for rr,cc in visible[cell]:
                lit[rr][cc] = True
    return lit

# Forces a bulb into a cell and updates the visible cells domains
def place_bulb(puzzle,domains,lit, visible,cell):
    completed = remove_option(domains, cell, 0)
    if not completed:
        return False,lit
    for v in visible.get(cell, []):
        if v in domains:
            ok = remove_option(domains, v, 1)
            if not ok:
                return False, lit      
    lit = update_lit(puzzle, domains, visible)
    return True, lit
    
# Applies the last free cell rule to force bulb placements (4.2.4 in report)
def last_free_cell(puzzle, domains, lit, visible):
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
    return True, domains, lit

# Converts domain representation into a printable output grid
def domains_to_output_grid(puzzle, domains):
    R = len(puzzle)
    C = len(puzzle[0])
    output = [[None for x in range(C)] for y in range(R)]
    for r in range(R):
        for c in range(C):
            cell = puzzle[r][c]
            if cell == BLACK:
                output[r][c] = "BLACK"
            elif cell == WHITE:
                d = domains[(r, c)]
                if d == [1]:
                    output[r][c] = "B"
                elif d == [0]:
                    output[r][c] = 0
                else:
                    output[r][c] = "?"
            else:
                output[r][c] = cell

    return output

# Applies single numbered-cell constraints to prune or force neighbours
def isolated_numerical_constraints(puzzle, domains, lit, visible):
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
                elif fc == mc +1 :
                    for z in diagonal_neighbours:
                        if domains[z] == [0,1]:
                            ok = remove_option(domains, z, 1)
                            if not ok:
                                return False, domains, lit
    lit = update_lit(puzzle, domains, visible)
    return True, domains, lit 
                        
# Applies pairwise (cross) numbered constraints for additional pruning  
def cross_numeric_comstraints(puzzle, domains, lit, visible):
    R = len(puzzle)
    C= len(puzzle[0])
    for r in range(R):
        for c in range(C):
            if puzzle[r][c] >0:
                constraint_diagonals = [] 
                a = puzzle[r][c]
                neighbours_a = []
                free_a = []
                bulbs_a = []
                for i in [1,-1]:
                    rr = r+i
                    cc = c+i
                    if 0<= rr < R and puzzle[rr][c] == WHITE:
                        neighbours_a.append((rr,c))
                    if 0<= cc < C and puzzle[r][cc] == WHITE:
                        neighbours_a.append((r,cc))
                for n in neighbours_a:
                    if domains[n] == [1]:
                        bulbs_a.append(n)
                    elif domains[n] == [0,1]:
                        free_a.append(n)
                ba = len(bulbs_a)
                fa = len(free_a)
                ma = a - ba
                if ma < 0 or ma > fa:
                    continue
                if fa != ma + 1:
                    continue
                for i in [1,-1]:
                    for j in [1,-1]:
                        rd = r + i
                        cd = c + j
                        if 0<= rd < R and 0<= cd < C and puzzle[rd][cd] > 0:
                            constraint_diagonals.append((rd,cd))  
                if len(constraint_diagonals) == 0:
                    continue
                for x,y in constraint_diagonals:
                    b = puzzle[x][y]
                    neighbours_b = []
                    free_b = []
                    bulbs_b = []
                    for i in [1,-1]:
                        xx = x+i
                        yy = y+i
                        if 0<= xx < R and puzzle[xx][y] == WHITE:
                            neighbours_b.append((xx,y))
                        if 0<= yy < C and puzzle[x][yy] == WHITE:
                            neighbours_b.append((x,yy))
                    for n in neighbours_b:
                        if domains[n] == [1]:
                            bulbs_b.append(n)
                        elif domains[n] == [0,1]:
                            free_b.append(n)
                    bb =len(bulbs_b)
                    fb = len(free_b)
                    mb = b - bb
                    if mb < 0 or mb > fb:
                        continue
                    if fb != mb +1:
                        continue
                    shared = []
                    for i in neighbours_a:
                        for j in neighbours_b:
                            if i == j and domains[i] == [0,1]:
                                shared.append(i)
                    if len(shared) != 2:
                        continue
                    not_shared_a = [i for i in neighbours_a if i not in shared]
                    not_shared_b = [i for i in neighbours_b if i not in shared]
                    if mb == 1:
                        new_ma = ma -1
                        new_fa = fa -2
                        if new_ma < 0 or new_ma > new_fa:
                            continue
                        if new_ma == 0:
                            for x in not_shared_a:
                                ok = remove_option(domains, x, 1)
                                if not ok:
                                    return False, domains, lit
                        elif new_ma == new_fa:
                            for x in not_shared_a:
                                ok, lit = place_bulb(puzzle, domains, lit, visible, x)
                                if not ok:
                                    return False, domains, lit
                    if ma == 1:
                        new_mb = mb -1
                        new_fb = fb - 2
                        if new_mb < 0 or new_mb > new_fb:
                            continue
                        if new_mb == 0:
                            for x in not_shared_b:
                                ok = remove_option(domains, x, 1)
                                if not ok:
                                    return False, domains, lit
                        elif new_mb == new_fb:
                            for x in not_shared_b:
                                ok, lit = place_bulb(puzzle, domains, lit, visible, x)
                                if not ok:
                                    return False, domains, lit
    lit = update_lit(puzzle, domains, visible)
    return True, domains, lit 
            
# Creates an immutable snapshot of domains for change detection
def domains_snapshot(domains):
    return {cell: tuple(values) for cell, values in domains.items()}

# Repeatedly applies all propagation rules until a fixed point is reached
def propagate(puzzle, domains, lit, visible):
    for _ in range(1000):
        changed = False
        before = domains_snapshot(domains)
        ok, domains, lit = isolated_numerical_constraints(puzzle, domains, lit, visible)
        if not ok:
            return False, domains, lit
        if domains_snapshot(domains) != before:
            changed = True
        before = domains_snapshot(domains)
        ok, domains, lit = cross_numeric_comstraints(puzzle, domains, lit, visible)
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
        if not changed:
            lit = update_lit(puzzle, domains, visible)
            return True, domains, lit

    lit = update_lit(puzzle, domains, visible)
    return True, domains, lit
        
# Checks whether the current assignment is a complete valid solution
def check_solution(puzzle, domains, lit, visible):
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
    return True
           
# Performs forward validity checking to detect early contradictions 
def validity(puzzle, domains, lit, visible):
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
    return True

# Runs propagation only (no guessing) and reports solver status
def solve_1(puzzle):
    if not input_checker(puzzle):
        return {"ok": False,"solved": False,"reason": "invalid input","domains": None,
            "lit": None,"visible": None,"output": None,}
    domains = create_domains(puzzle)
    visible = create_visible(puzzle)
    lit = update_lit(puzzle, domains, visible)
    ok, domains, lit = propagate(puzzle, domains, lit, visible)
    if not ok:
        return {"ok": False,"solved": False,"reason": "contradiction during propagation",
            "domains": domains,"lit": lit, "visible": visible,
            "output": domains_to_output_grid(puzzle, domains),}
    fully_decided = True
    for d in domains.values():
        if d not in ([0], [1]):
            fully_decided = False
            break
    solved = fully_decided and check_solution(puzzle, domains, lit, visible)

    return {"ok": True,"solved": solved,
        "reason": "solved" if solved else "partial (needs guessing/backtracking)",
        "domains": domains,"lit": lit,"visible": visible, 
        "output": domains_to_output_grid(puzzle, domains),}

# Pretty-prints the solved/partial grid to the console
def print_output_grid(output):
    if output is None:
        print("(no output)")
        return
    display_map = {
        "BLACK": "#",
        "B": "💡",
        "?": ".", }

    for row in output:
        pretty = []
        for x in row:
            pretty.append(display_map.get(x, str(x)))
        print(" ".join(pretty))
    print()
         
                    
 # Main public solver wrapper that runs solve_1 and prints results               
def solve(puzzle):
    result = solve_1(puzzle)
    if result["output"] is not None:
        print_output_grid(result["output"])
    if result["ok"]:
        print("Status:", result["reason"])
    else:
        print("Status:", result["reason"])

    return result                   
  
# Computes how many numbered constraints are adjacent to a cell
def constraint_degree(puzzle, cell):
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

    return degree
              
# Chooses a guess cell based on tightest numeric constraint heuristic
def choose_from_constraints(puzzle,domains):
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
            mc =k-bulbs
            fc = len(free)
            if mc <= 0:
                continue
            if fc == 0:
                continue
            slack =fc -mc
            score = (fc,slack,-k)
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

    return best_cell
    
 # Returns all cells that could potentially light the given target cell
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
    
# Chooses a guess cell based on hardest-to-light unlit white cell
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
    for cand in best_candidates:
        size = 0
        if cand in visible:
            size = len(visible[cand])
        if best_guess is None or size > best_vis_size:
            best_guess = cand
            best_vis_size = size
    return best_guess

# Combines heuristics to select the best next guess cell
def choose_guess_cell(puzzle, domains, lit, visible):
    cell = choose_from_constraints(puzzle, domains)
    if cell is not None:
        return cell
    cell = choose_from_visibility(puzzle, domains, lit, visible)
    return cell

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

# Full recursive backtracking search with propagation and pruning
def backtrack_solve(puzzle, domains, lit, visible):
    ok, domains, lit = propagate(puzzle, domains, lit, visible)
    if not ok:
        return False, domains, lit
    if domains_fully_decided(domains):
        if check_solution(puzzle, domains, lit, visible):
            return True, domains, lit
        return False, domains, lit
    cell = choose_guess_cell(puzzle, domains, lit, visible)
    if cell is None:
        return False, domains, lit

    d1 = copy_domains(domains)
    lit1 = copy_lit(lit)
    ok1, lit1 = place_bulb(puzzle, d1, lit1, visible, cell)
    if ok1:
        if validity(puzzle, d1, lit1, visible):
            solved, sol_domains, sol_lit = backtrack_solve(puzzle, d1, lit1, visible)
            if solved:
                return True, sol_domains, sol_lit

    d2 = copy_domains(domains)
    lit2 = copy_lit(lit)
    ok2 = remove_option(d2, cell, 1)
    if ok2:
        if validity(puzzle, d2, lit2, visible):
            solved, sol_domains, sol_lit = backtrack_solve(puzzle, d2, lit2, visible)
            if solved:
                return True, sol_domains, sol_lit
    return False, domains, lit

                
                
     
                            
                            
                            
                            
                            
                            
                            
                
            
    
                
                
                        
                
                        
                    
                        
                        
                        
                        
                        
                
                
                
            

      

 
          


 

    