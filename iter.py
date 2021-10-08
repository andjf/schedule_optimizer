#!/usr/bin/env python3
#title           :iter.py
#description     :Make selections of from given "bins"
#author          :Andrew Ferrin
#date            :October 7, 2021
#usage           :import iter.py
#python_version  :3.9.2  

from typing import Any, List, Iterator


def __get_result(bins: List[List[Any]], indices: List[int]) -> List[Any]:
    """ Returns current result based on the bin indices

    Returns the current result in the form of a list based 
    on the indices that you want to use for each bin.

    Example: 
        bins: ["AB", "CD", "EF"]
        indices: [1, 0, 1]

        return value: ["B", "C", "F"]

    Parameters
    ----------
    `bins`: `List[List[Any]]`
        The bins where each bin has multiple options to choose from
    `indices`: `List[int]`
        The indices that you would like to select from each respective bin

    Returns
    -------
    `List[Any]`
        A list of the items selected from each respective bin based on the given indices
    """
    return [bins[i][index] for i, index in enumerate(indices)]


def __advance(bins: List[List[Any]], indices: List[int]) -> bool:
    """ Advances the indices

    Advances the indices list such that the next element that is
    selected will give a unique result.

    Example: 
        `bins`: `["AB", "CD", "EF"]`
        `indices`: `[1, 0, 1]`

        `advance(bins, indices)` => `True`
        `indices`: `[1, 1, 0]`

        `advance(bins, indices)` => `True`
        `indices`: `[1, 1, 1]`

        `advance(bins, indices)` => `False`

    Parameters
    ----------
    `bins`: `List[List[Any]]`
        The bins where each bin has multiple options to choose from
    `indices`: `List[int]`
        The indices that you would like to select from each respective bin

    Returns
    -------
    `bool`
        `True` if advance was successful, `False` if there are no more possible advancements
    """

    # Calls helper function, starting at the last bin
    return __advance_helper(bins, indices, len(bins) - 1)


def __advance_helper(bins: List[List[Any]], indices: List[int], index: int) -> bool:
    """ recursive helper function for `advance`

    Advances the indices list such that the next element that is
    selected will give a unique result.

    Parameters
    ----------
    `bins`: `List[List[Any]]`
        The bins where each bin has multiple options to choose from
    `indices`: `List[int]`
        The indices that you would like to select from each respective bin
    `index`: int
        The current index being advanced

    Returns
    -------
    `bool`
        `True` if advance was successful, `False` if there are no more possible advancements
    """

    # If there are more possible advancements
    if index >= 0:
        # Advance the current index
        indices[index] += 1
        # Check if that advancement went past the
        # boundaries of that index's bin.
        if indices[index] == len(bins[index]):
            # If so, reset the current index
            indices[index] = 0
            # And advance the previous bin
            return __advance_helper(bins, indices, index - 1)
        # Advancement was successful
        return True
    # Nothing more to advance
    return False


def get_all_possibilities(bins: List[List[Any]]) -> List[List[Any]]:
    """ All possible ways to choose from the given `bins`

    Loops through all 

    See main for example

    Parameters
    ----------
    `bins`: `List[List[Any]]`
        The bins that you would like to choose from

    Returns
    -------
    `List[List[Any]]`
        A list of all possible ways to choose from the given `bins`
    """
    i = [0] * len(bins)
    results = [__get_result(bins, i)]
    while __advance(bins, i):
        results.append(__get_result(bins, i))
    return results


def get_all_possibilities_iter(bins: List[List[Any]]) -> Iterator[List[Any]]:
    """ All possible ways to choose from the given `bins`

    Loops through all and yields when if finds the next one

    Parameters
    ----------
    `bins`: `List[List[Any]]`
        The bins that you would like to choose from

    Returns
    -------
    `Iterator[List[Any]]`
        An iterator that iterates through all possible ways to choose from the given `bins`
    """
    i = [0] * len(bins)
    yield __get_result(bins, i)
    while __advance(bins, i):
        yield __get_result(bins, i)


def main() -> None:
    """
    Main method for testing functions
    """
    bins = [[1, 2, -1, 0], [3, 4], [5, 6]]
    print(f"Printing all possible ways to select from {bins}")

    p = get_all_possibilities(bins)
    print("\n".join(map(str, p)))

    """
    # Alternatively...
    for p in get_all_possibilities_iter(bins):
        print(p)
    """


if __name__ == "__main__":
    main()
