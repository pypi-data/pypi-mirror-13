import copy
import sys
from random import shuffle

import PyFBA

__author__ = 'Rob Edwards'


def iterate_reactions_to_run(base_reactions, optional_reactions, compounds, reactions, media,
                             biomass_eqn, verbose=False):
    """
    Iterate all the elements in optional_reactions and merge them with base reactions, and then test to see which are
    required for growth

    If you provide an empty set for base_reactions, we test every member of optional_reactions to see if it is required
    for growth.

    This will run as many FBA reactions as there are elements in optional_reactions and only test them one at a time.

    WE

    :param compounds: The compounds dictionary
    :type compounds: dict
    :param base_reactions: a set of reactions that are required for the model but that do not result in growth
    :type base_reactions: set
    :param optional_reactions: a set of reactions that when added to the base_reactions set result in
        growth but for which only a subset may or may not be required.
    :type optional_reactions: set
    :param reactions: the reactions data dictionary
    :type reactions: dict
    :param media: our media object
    :type media: set
    :param biomass_eqn: our biomass equation
    :type biomass_eqn: network.reaction.Reaction
    :param verbose: Print more information
    :type verbose: bool
    :return: The list of reactions that need to be added to base_reactions to get growth
    :rtype: list
    """

    num_elements = len(optional_reactions)
    required_optionals = set()

    for r in range(num_elements):
        removed_reaction = optional_reactions.pop()
        r2r = base_reactions.union(optional_reactions).union(required_optionals)
        status, value, growth = PyFBA.fba.run_fba(compounds, reactions, r2r, media, biomass_eqn)
        if not growth:
            required_optionals.add(removed_reaction)

    return list(required_optionals)


def minimize_additional_reactions(base_reactions, optional_reactions, compounds, reactions, media,
                                  biomass_eqn, verbose=False):
    """
    Given two sets, one of base reactions (base_reactions), and one of optional
    reactions we will attempt to minimize the reactions in the optional
    reactions list by repeatedly bisecting the optional set and testing
    the fba. We return a set of the optional reactions that are required
    for the fba to grow.

    :param compounds: The compounds dictionary
    :type compounds: dict
    :param base_reactions: a set of reactions that are required for the model but that do not result in growth
    :type base_reactions: set
    :param optional_reactions: a set of reactions that when added to the base_reactions set result in
        growth but for which only a subset may or may not be required.
    :type optional_reactions: set
    :param reactions: the reactions data dictionary
    :type reactions: dict
    :param media: our media object
    :type media: set
    :param biomass_eqn: our biomass equation
    :type biomass_eqn: network.reaction.Reaction
    :param verbose: Print more information
    :type verbose: bool
    :return: The set of reactions that need to be added to base_reactions to get growth
    :rtype: set
    """

    base_reactions = set(base_reactions)
    optional_reactions = set(optional_reactions)
    # test that (a) the base_reactions set does not grow and the base_reactions
    # + optional set does grow
    status, value, growth = PyFBA.fba.run_fba(compounds, reactions, base_reactions, media, biomass_eqn)
    if growth:
        sys.stderr.write("The set of 'base' reactions results in growth so we don't need to bisect the optional set\n")
        return set()

    status, value, growth = PyFBA.fba.run_fba(compounds, reactions, base_reactions.union(optional_reactions), media,
                                              biomass_eqn)
    if not growth:
        raise Exception("'base' union 'optional' reactions does not generate growth. We can not bisect the set\n")

    # first, lets see if we can limit the reactions based on compounds present and still get growth
    limited_rxn = PyFBA.gapfill.limit_reactions_by_compound(reactions, base_reactions, optional_reactions)
    status, value, growth = PyFBA.fba.run_fba(compounds, reactions, base_reactions.union(limited_rxn), media,
                                              biomass_eqn)
    if growth:
        if verbose:
            sys.stderr.write("Successfully limited the reactions by compound and reduced " +
                             " from {} to {}\n".format(len(optional_reactions), len(limited_rxn)))
        optional_reactions = limited_rxn

    test = True
    tries = 0
    maxtries = 5
    current_rx_list = list(optional_reactions)
    itera = 0
    sys.stderr.write("At the beginning the base list has {} ".format(len(base_reactions)) +
                     " and the optional list has {} reactions\n".format(len(current_rx_list)))

    left = []
    right = []
    while test:
        itera += 1
        left, right = PyFBA.gapfill.bisections.bisect(current_rx_list)
        # left, right = percent_split(current_rx_list, percent)
        r2r = base_reactions.union(set(left))
        status, value, lgrowth = PyFBA.fba.run_fba(compounds, reactions, r2r, media, biomass_eqn)

        # running the fba takes all the time, so we only run the right half if the left half doesn't grow
        if lgrowth:
            tries = 0
            current_rx_list = left
            if len(left) == 1:
                test = False
                right = []
            if verbose:
                sys.stderr.write("Iteration: {} Try: {} Length: {} and {}".format(itera, tries, len(left), len(right)) +
                                 " Growth: {} and NOT TESTED\n".format(lgrowth))
        else:
            r2r = base_reactions.union(set(right))
            status, value, rgrowth = PyFBA.fba.run_fba(compounds, reactions, r2r, media, biomass_eqn)
            if verbose:
                sys.stderr.write("Iteration: {} Try: {} Length: {} and {}".format(itera, tries, len(left), len(right)) +
                                 " Growth: {} and {}\n".format(lgrowth, rgrowth))

            if rgrowth:
                # the right list grows so we can use it
                tries = 0
                current_rx_list = right
                if len(right) == 1:
                    test = False
                    left = []
            else:
                # neither grows.
                # If there are less than 20 elements we'll just iterate through them all.
                # Otherwise, we can we split the list unevenly and see if we get growth
                uneven_test = True
                if len(current_rx_list) < 20:
                    left = iterate_reactions_to_run(base_reactions, optional_reactions, compounds, reactions, media, biomass_eqn, verbose)
                    right = []
                    test = False
                else:
                    percent = 40
                    left, right = PyFBA.gapfill.bisections.percent_split(current_rx_list, percent)
                    while uneven_test and len(left) > 0 and len(right) > 0:
                        r2r = base_reactions.union(set(left))
                        status, value, lgrowth = PyFBA.fba.run_fba(compounds, reactions, r2r, media, biomass_eqn)
                        r2r = base_reactions.union(set(right))
                        status, value, rgrowth = PyFBA.fba.run_fba(compounds, reactions, r2r, media, biomass_eqn)
                        if verbose:
                            sys.stderr.write(
                                "Iteration: {} Try: {} Length: {} and {}".format(itera, tries, len(left), len(right)) +
                                " Growth: {} and {}\n".format(lgrowth, rgrowth))
                        if lgrowth:
                            tries = 0
                            current_rx_list = left
                            uneven_test = False
                        elif rgrowth:
                            tries = 0
                            current_rx_list = right
                            uneven_test = False
                        else:
                            percent /= 2.0
                            left, right = PyFBA.gapfill.bisections.percent_split(current_rx_list, percent)
                if uneven_test:
                    # we never got growth, so we can't continue
                    # we take another stab and try again
                    tries += 1
                    current_rx_list = left + right
                    shuffle(current_rx_list)
                if tries > maxtries:
                    test = False

    remaining = set(left + right)
    if verbose:
        sys.stderr.write("There are {} reactions remaining: {}\n".format(len(remaining), remaining))
    return remaining
