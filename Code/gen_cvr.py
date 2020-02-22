"""
Outputs "fake" CVR for consumption by SHANGRLA for elections that are
conducted without CVRs. Note that the need for a CVR where there isn't one
means that we can't audit more than one race at a time with SHANGRLA, since we
can't know which combination of votes appears on which ballot.

This also only works for vote-for-one contests, as again without CVRs we can't
know which combinations of votes appear on which ballots. 
"""

import csv
import os
import time
import sys

from assertion_audit_utils import CVR


def main():
    """
    This is a fairly procedural program, so just wrap it in a main function
    """

    interactive = True
    if len(sys.argv) > 1:
        interactive = False

        if sys.argv[1] == '-t':
            if len(sys.argv) != 3:
                print('Usage: python3 gen_cvr.py -t [res_file_name].csv')
                sys.exit(1)
            res_file_name = sys.argv[2]


    while interactive:
        print('Please specify an election results CSV file of the form:')
        print('\tCandidate Name,Number of Votes')
        print()
        print('E.g.,')
        print('\tCandidate Name, Number of Votes')
        print('\tAlice, 634')
        print('\tBob, 321')
        print('\tCharlie, 13')
        print('\tTotal Votes, 1000')
        print()
        print('Input the file name of the results file: ')

        res_file_name = input()

        if os.path.exists(res_file_name):
            break

        print('Specified file {} does not exist'.format(res_file_name))
        print()
        time.sleep(1)

    res = {}
    total_votes = 0
    try:
        for line in csv.DictReader(open(res_file_name)):
            if line['Candidate Name'] == 'Total Votes':
                total_votes = int(line['Number of Votes'])
            else:
                cand = line['Candidate Name']
                votes = int(line['Number of Votes'])

                res[cand] = votes

    except (KeyError, ValueError) as ex:
        print('Results file is mal-formatted: {}'.format(ex))
        sys.exit(1)

    assert sum(res.values()) <= total_votes, 'Results file shows more votes than reported!'



def gen_cvrs(results, total):
    """
    Generate the CVRS.

    Inputs:
        results - dict of results {'cand': votes, ...}
        total - the total number of votes
    Outputs:
        cvrs - a list of CVR-class objects corresponding to "fake" ballots.
    """

    cvrs = []
    
    cvr_cnt = 0
    for cand in results:
        for ballot in results[cand]:
            cvr_id = 'Gen-{}'.format(cvr_cnt)
            votes = dict.fromkeys(results.keys(), 0)

            votes[cand] = 1

            cvrs.append(CVR(id=cvr_id, votes=votes))

            cvr_id += 1

    phantoms = totals - sum(results.values())

    for p in phantoms:
        cvr_id = 'Gen-{}'.format(cvr_cnt)
        votes = dict.fromkeys(results.keys(), 0)

        cvrs.append(CVR(id=cvr_id, votes=votes, phantom=True))

        cvr_id += 1




if __name__ == '__main__':
    main()
