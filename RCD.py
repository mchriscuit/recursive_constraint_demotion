import numpy as np
import re
import argparse

## helper function to make tableau look pretty
def print_tableau(data, p):
    lens = [max(map(len, col)) for col in zip(*data)] # get length of largest element per column in the list of lists
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens) # generate list of formats consisting of x spaces for the characters each row of that column to occupy
    table = [fmt.format(*row) for row in data] # note that {{}} is necessary as the initial { must be escaped first (akin to '\\')

    ## print data
    fill = '=' * (len(p)+5)
    print()
    print(fill, p, fill, sep='\n')
    print('\n'.join(table))
    print()

## argparse to get filename from command line
parser = argparse.ArgumentParser(description='Perform RCD on some dataset.')
parser.add_argument('data', type=str, nargs='?', help='name of the data (.csv)')
args = parser.parse_args()

FILENAME = args.data

## Load file from FILENAME
with open(FILENAME, 'r') as file:
    data = file.readlines()

## clean up data
data = [r.strip().split(',') for r in data]
data = [ ['-' if x == '' else x for x in r] for r in data ]

## formatting data for printing
p = 'Data drawn from \'{}\':'.format(FILENAME)
print_tableau(data, p)

## ============================================================
##                  Computing W and L
## ============================================================
data = np.array(data)
iteration = 1

## some information we need
CONSTRAINTS = data[0][2:]
ORDER = []

def RCD(data=data, ORDER=ORDER, CONSTRAINTS=CONSTRAINTS, iteration=iteration):
    ## simplify list to contain only the candidates and violations
    df = np.array([r for r in data if not re.search('/', r[0])])

    ## go down the rows and compare it to the row of the winning candidate
    t = np.array([[len(re.findall(r'\*', cell)) for cell in r] for r in df])

    ## generate a vector denoting where the winners are
    w_idx = np.squeeze(np.argwhere(df[:,1] == '1'))

    # generate winners
    if t[w_idx].ndim < 2: winners = np.max(np.reshape(t[w_idx], (1,-1))[:,2:], 0)
    else: winners = np.max(t[w_idx][:,2:], 0)

    # generate losers
    losers = np.array(np.delete(t, w_idx, axis=0)[:,2:])

    ## if there are no more losers, break
    if len(losers) == 0: ORDER.append(data[0,2:]); return

    ## otherwise, proceed as normal
    losers = np.max(losers, axis=0)

    ## generate the comparative tableau
    ## positive numbers are winner-preferred; non-positive is loser-preferred
    t = losers - winners

    ## sum over the columns and see which ones are positive; if so, then it is a loser-preferring constraint
    loser_constraints = np.argwhere(t > 0).squeeze(-1)

    ## if the length of loser_constraints is 0, and the code did not end earlier, then we have an ambiguous ranking; throw an error
    if len(loser_constraints) == 0:
        raise ValueError("Unable to find any loser-preferring constraints; is there more than one winner?")
    ORDER.append(data[0,loser_constraints+2])

    ## for these indices, see which candidates are explained and remove them
    # record the indices of the candidates with violations of the loser constraints
    contains_violation = np.array([ [bool(re.search(r'\*$', cell)) for cell in r] for r in data[:,loser_constraints+2] ])
    explained_candidates = np.argwhere(np.sum(contains_violation, axis=1)).squeeze() # recall that we removed the first two columns
    new_data = np.delete(data, explained_candidates, axis=0)
    new_data = np.delete(new_data, loser_constraints+2, axis=1)
    print('Constraints that are winner-preferring: {}'.format(', '.join(data[0,loser_constraints+2])))
    print('Candidates that are explained: {}'.format(', '.join(data[explained_candidates,0])))

    ## also remove winners that no longer have any competitors
    satisfied = []
    candidates = new_data[1:,0]
    for i in range(len(candidates)):
        if i == len(candidates)-1:
            if re.search(r'/', candidates[i-1]): satisfied += [i, i+1]
        else:
            if re.search(r'/', candidates[i-1]) and re.search(r'/', candidates[i+1]): satisfied += [i, i+1]
    satisfied = np.array(satisfied)
    new_data = np.delete(new_data, satisfied, axis=0)

    ## formatting data for printing
    p = 'Tableau at iteration {}'.format(iteration)
    print_tableau(new_data, p)

    ## iterate
    iteration += 1

    ## undergo recursion
    RCD(data=new_data, ORDER=ORDER, CONSTRAINTS=CONSTRAINTS, iteration=iteration)

## perform RCD
RCD()

## ============================================================
##                  Printing the Final Output
## ============================================================
p = 'Final Constraint Ranking:'
fill = '=' * (len(p) + 5)
print(fill, p, fill, sep='\n')
print(' >> '.join(', '.join(c) for c in ORDER))
print()

# reorder columns by ORDER_idx
ORDER_idx = [[np.argwhere(data[0,:] == c).squeeze() for c in constraints] for constraints in ORDER]
ORDER_idx_flattened = [np.argwhere(data[0,:] == c).squeeze() for constraints in ORDER for c in constraints]
organized_data = np.hstack( (data[:,:2], data[:,ORDER_idx_flattened]) )

## insert strict rankings based on the ranking generated
ranking = np.full((organized_data.shape[0], 1), '|')
UR = np.argwhere(list(bool(re.search(r'/', c)) for c in organized_data[:,0])).squeeze()
ranking[UR] = '='

# insert a line break at the beginning of the tableau
inset = 2
organized_data = np.hstack((organized_data[:,:inset], ranking, organized_data[:,inset:]))

# insert a line break at the designated points
for idx in range(len(ORDER_idx)):
    inset += 1 + len(ORDER_idx[idx])
    organized_data = np.hstack((organized_data[:,:inset], ranking, organized_data[:,inset:]))

## print out the full tableaux with the rankings
p = 'Final Tableau'
print_tableau(organized_data, p)
