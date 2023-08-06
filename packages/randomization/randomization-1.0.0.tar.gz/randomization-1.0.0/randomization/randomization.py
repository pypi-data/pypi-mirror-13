"""
Randomization is a module that provides functions to create random group
assignments to be used in clinical trials
"""

import math
import random

def cumsum(numbers):
    """ Calculates the cumulative sum of a numeric list.

    This function operates on the list *in place*.

    Args:
        numbers: a list of numbers.

    Examples:
        >>> numbers = [1, 2, 3]
        >>> cumsum(numbers)
        >>> print(numbers)
        [1, 3, 6]
    """
    if len(numbers) >= 2:
        for i in range(1, len(numbers)):
            numbers[i] += numbers[i - 1]
    # If the length of numbers is less than 2, nothing happens.

def simple(n_subjects, n_groups, p=None, seed=None):
    """ Create a randomization list using simple randomization.

    Simple randomization randomly assigns each new subject to a group
    independent of the assignment of the previous members.

    Args:
        n_subjects: The number of subjects to randomize.
        n_groups: The number of groups to randomize subjects to.
        p: (optional) The probability that a subject will be randomized to a
            group.  The length of p must be equal to n_groups.
        seed: (optional) The seed to provide to the RNG.

    Raises:
        ValueError: If the length of `p` is not equal to `n_groups`.

    Returns:
        list: a list of length `n_subjects` of integers representing the
            groups each subject is assigned to.

    Notes:
        Simple Randomization is prone to long runs of a single group and
        may yield highly unbalanced lists.

    References:
        To be added
    """

    random.seed(seed)
    groups = []
    if p is None:
        for _ in range(0, n_subjects):
            groups.append(random.randint(1, n_groups))
    else:
        if len(p) is not n_groups:
            raise ValueError("The length of `p` must be equal to `n_groups`.")
        cumsum(p)
        for _ in range(0, n_subjects):
            test = random.random()
            # Find which group the next obs should be assigned to.
            # HACKY - Let's make this better
            group = 0
            for elem in p:
                if elem < test:
                    group += 1
                else:
                    break
            groups.append(group)
    return groups

def complete(subjects, seed=None):
    """ Create a randomization list using complete randomization.

    Complete randomization randomly shuffles a list of group labels.  This
    ensures that the resultant list is retains the exact balance desired.
    This randomization is done in place.

    Args:
        subjects: A list of group labels to randomize.
        seed: (optional) The seed to provide to the RNG.

    Notes:
        Complete Randomization is prone to long runs of a single group.

    Returns:
        list: a list of length `len(subjects)` of the group labels of the
            subjects.

    Examples:
        >>> subjects = ["a", "a", "a", "b", "b", "b"]
        >>> complete(subjects)
        ["a", "b", "b", a", "a", "b"]
    """

    random.seed(seed)
    # We do not want to do the shuffle in place because it would break with
    # the pattern of the rest of the randomization functions
    groups = subjects[:]
    random.shuffle(groups)
    return groups

def block(n_subjects, n_groups, block_length, seed=None):
    """ Create a randomization list using block randomization.

    Block randomization takes blocks of group labels of length `block_length`,
    shuffles them and adds them to the randomization list.  This is done to
    prevent long runs of a single group. Usually `block_length` is equal
    to 4 or 6.

    Args:
        n_subjects: The number of subjects to randomize.
        n_groups: The number of groups to randomize subjects to.
        block_length: The length of the blocks.  `block` should be equal to
            :math:`k * n_{groups}, k > 1`.
        seed: (optional) The seed to provide to the RNG.

    Returns:
        list: a list of length `n_subjects` of integers representing the
            groups each subject is assigned to.

    Notes:
        The value of `block_length` should be a multiple of `n_groups` to
        ensure proper balance.
    """

    random.seed(seed)
    block_form = []
    for i in range(0, block_length):
        # If n_groups is not a factor of block_length, there will be unbalance.
        block_form.append(i % n_groups)

    count = 0
    groups = []

    while count < n_subjects:
        random.shuffle(block_form)
        groups.extend(block_form)
        count += block_length

    # If `n_subjects` is not a multiple of `block_length`, only return the
    # first `n_subjects` elements of `groups`
    return groups[:n_subjects]

def random_block(n_subjects, n_groups, block_lengths, seed=None):
    """ Create a randomization list by block randomization with random blocks.

    Block randomization takes blocks of group labels of length `block_length`,
    shuffles them and adds them to the randomization list.  This is done to
    prevent long runs of a single group. Usually `block_length` is equal
    to 4 or 6.

    Block randomization with random blocks adds an extra layer of randomness by
    changing the length of each new block added.  This is done in order to
    hide patterns that may arise if the block length becomes known.

    Args:
        n_subjects: The number of subjects to randomize.
        n_groups: The number of groups to randomize subjects to.
        block_lengths: A list of the length of the blocks.
        seed: (optional) The seed to provide to the RNG.

    Returns:
        list: a list of length `n_subjects` of integers representing the
            groups each subject is assigned to.

    Notes:
        Each value in `block_lengths` should be a multiple of `n_groups`
        to ensure proper balance.

    Todo:
        - Implement weights for block lengths
    """
    random.seed(seed)
    n_block_lengths = len(block_lengths)
    blocks = []
    for block_length in block_lengths:
        block_form = []
        for i in range(0, block_length):
            block_form.append(i % n_groups)
        blocks.append(block_form)
    count = 0
    groups = []
    while count < n_subjects:
        this_block = blocks[random.randint(0, n_block_lengths - 1)]
        random.shuffle(this_block)
        groups.extend(this_block)
        count += len(this_block)
    # Due to the random selection of block lengths, you cannot guarentee that
    # `len(groups) is n_subjects` therefore we only return the first `n_subjects`
    # elements of `groups`
    return groups[:n_subjects]

def random_treatment_order(n_subjects, n_treatments, seed=None):
    """ Create a randomization list for studies where the subject recieves
    multiple treatments.

    If a subject will recieve multiple treatments, those treatments should be
    randomized.

    Args:
        n_subjects: The number of subjects to randomize.
        n_treatments: The number of treatments a subject will
        seed: (optional) The seed to provide to the RNG.

    Returns:
        list: a list of length `n_subjects` of lists of length `n_treatments`.
            Each sublist is treatment order of the subject.
    """

    random.seed(seed)
    treatment = []
    for i in range(0, n_treatments):
        treatment.append(i)
    groups = []
    for i in range(0, n_subjects):
        random.shuffle(treatment)
        groups.append(treatment)
    return groups

def efrons_biased_coin(n_subjects, bias=None, seed=None):
    """ Create a randomization list using Efron's Biased Coin

    Efron's Biased Coin weights the assignment of a new subject by adjusting the
    probability of the Bernoulli random variable used to determine the next
    group according to which group is under represented.  The adjusted
    probability is a fixed value determined by `bias`.
    This method is only approriate for 2 groups.

    Args:
        n_subjects: The number of subjects to randomize.
        bias: (optional) The probability the new subject will be assigned to
            the under represented group.  The default is 0.67.
        seed: (optional) The seed to provide to the RNG.

    Raises:
        ValueError: If the length of `bias` is not in [0, 1].

    Returns:
        list: a list of length `n_subjects` of integers representing the
            groups each subject is assigned to.

    Notes:
        Exact balance between groups is not guaranteed when using Efron's
        Biased Coin, but it is usually very close to balanced.
    """
    random.seed(seed)
    if bias is None:
        bias = 0.67
    else:
        if bias >= 1 or bias <= 0:
            raise ValueError("`bias` must be in [0, 1].")
    group_0_count = 0.0
    groups = []
    for i in range(0, n_subjects):
        if group_0_count / (i + 1) == 0.5 or i is 0:
            # Balance
            cut = 0.5
        elif group_0_count / (i + 1) < 0.5:
            # Too few from Group 0
            cut = 1 - bias
        else:
            # Too few from Group 1
            cut = bias
        test = random.random()
        if test > cut:
            group = 0
        else:
            group = 1
        groups.append(group)
        if group == 0:
            group_0_count += 1
    return groups


def weis_urn(n_subjects, seed=None):
    """ Create a randomization list using Wei's Urn.

    Wei's Urn weights the assignment of a new subject by adjusting the
    probability of the Bernoulli random variable used to determine the next
    group according to which group is under represented.  The adjusted
    probability is a dynamic value.

    Suppose that :math:`N_{r}` is the total number of subjects already randomize
    and :math:`N_{r0}` is the number of subjects already randomized that were
    randomized to Group 0.  The probability that the next subject will be
    randomized to Group 0 is:

    .. math::
        p_{0} = 1 - \\frac{N_{r0}}{N_{r}}

    This method is only approriate for 2 groups.

    Args:
        n_subjects: The number of subjects to randomize.
        seed: (optional) The seed to provide to the RNG.

    Returns:
        list: a list of length `n_subjects` of integers representing the
            groups each subject is assigned to.

    Notes:
        Exact balance between groups is not guaranteed when using Wei's
        Urn, but it is usually very close to balanced.
    """

    random.seed(seed)
    group_0_count = 0.0
    groups = []
    for i in range(0, n_subjects):
        if i > 0:
            cut = 1 - group_0_count / (i + 1)
        else:
            cut = 0.5
        test = random.random()
        if test < cut:
            group = 0
        else:
            group = 1
        groups.append(group)
        if group is 0:
            group_0_count += 1
    return groups

def stratification(n_subjects_per_strata, n_groups, block_length=4, seed=None):
    """ Create a randomization list for each strata using Block Randomization.

    If a study has several strata, each strata is seperately randomized using
    block randomization.

    Args:
        n_subjects_per_strata: A list of the number of subjects for each strata.
        n_groups: The number of groups to randomize subjects to.
        block_length: The length of the blocks.
        seed: (optional) The seed to provide to the RNG.

    Returns:
        list: a list of length `len(n_subjects_per_strata)` of lists of length
            `n_subjects_per_strata`.  Each sublist is the strata specific
            randomization list.

    Notes:
        The value of `block_length` should be a multiple of `n_groups`
        to ensure proper balance.

    Todo:
        Allow for multiple randomization techniques to be used.
    """

    groups = []
    for i in range(len(n_subjects_per_strata)):
        # Adding 52490, a dummy value, to the seed ensures a different list
        # per strata.  The use of a 'magic number' here allows for
        # reproducibility
        if seed is not None:
            seed = seed + 52490
        groups.append(block(n_subjects_per_strata[i], n_groups,
                            block_length, seed))
    return groups

# A Response addaptive randomization technique
def double_biased_coin_minimize(control_success, control_trials,
                                treatment_success, treatment_trials,
                                control_name=None, treatment_name=None,
                                seed=None):
    """ Returns a group assignment for adaptive trials using the Double Biased
    Coin Minimization method.

    Suppose that :math:`N_{c}` is the number of controls, of which :math:`S_{c}`
    were successes and :math:`N_{t}` is the number of treatments, of which
    :math:`S_{t}` were successes.  We can define the probability of success as:

    .. math::
        p_{c} = \\frac{S_{c}}{N_{c}}
        p_{t} = \\frac{S_{t}}{N_{t}}

    The next subject will be randomized to the control group with probability:

    .. math::
        \\frac{\sqrt{p_{c}}}{\\sqrt{p_{c}} + \\sqrt{p_{t}}}

    Args:
        control_success: The number of successfull trials in the control group.
        control_trials: The number of trials in the control group.
        treatment_success: The number of successfull trials in the treatment
            group.
        treatment_trials: The number of trials in the treatment group.
        control_name: (optional) The name of the control group.  The default
            is 'C'
        treatment_name: (optional) The name of the treatment group.  The default
            is 'T'
        seed: (optional) The seed to provide to the RNG.

    Returns:
        list: the name (either `control_name` or `treatment_name`) of the group
            the subject is assigned to.
    """
    if control_trials < control_success:
        raise ValueError('`control_trials` must be greater than or equal '
                         'to `control_success`')
    if treatment_trials < treatment_success:
        raise ValueError('`treatment_trials` must be greater than or equal '
                         'to `treatment_success`')

    if control_name is None:
        control_name = "C"
    if treatment_name is None:
        treatment_name = "T"

    if seed is not None:
        # This ensures a new seed for each selection
        seed = seed + 10 * (control_trials + treatment_trials)

    random.seed(seed)

    if control_trials > 1:
        pC = float(control_success) / control_trials
    else:
        pC = 0.5
    if treatment_trials > 1:
        pT = float(treatment_success) / treatment_trials
    else:
        pT = 0.5

    cut = math.sqrt(pC) / (math.sqrt(pC) + math.sqrt(pT))
    test = random.random()

    if test < cut:
        group = control_name
    else:
        group = treatment_name
    return group

# A Response addaptive randomization technique
def double_biased_coin_urn(control_success, control_trials,
                           treatment_success, treatment_trials,
                           control_name=None, treatment_name=None,
                           seed=None):
    """ Returns a group assignment for adaptive trials using the Double Biased
    Coin Minimization method.

    Suppose that :math:`N_{c}` is the number of controls, of which :math:`S_{c}`
    were successes and :math:`N_{t}` is the number of treatments, of which
    :math:`S_{t}` were successes.  We can define the probability of success as:

    .. math::
        p_{c} = \\frac{S_{c}}{N_{c}}
        p_{t} = \\frac{S_{t}}{N_{t}}

    The next subject will be randomized to the control group with probability:

    .. math::
        \\frac{1 - p_{t}}{(1 - p_{c}) + (1 - p_{t})}

    Args:
        control_success: The number of successfull trials in the control group.
        control_trials: The number of trials in the control group.
        treatment_success: The number of successfull trials in the treatment
            group.
        treatment_trials: The number of trials in the treatment group.
        control_name: (optional) The name of the control group.  The default
            is 'C'
        treatment_name: (optional) The name of the treatment group.  The default
            is 'T'
        seed: (optional) The seed to provide to the RNG.

    Returns:
        list: the name (either `control_name` or `treatment_name`) of the group
            the subject is assigned to.
    """
    if control_trials < control_success:
        raise ValueError('`control_trials` must be greater than or equal '
                         'to `control_success`')
    if treatment_trials < treatment_success:
        raise ValueError('`treatment_trials` must be greater than or equal '
                         'to `treatment_success`')

    if control_name is None:
        control_name = "C"
    if treatment_name is None:
        treatment_name = "T"

    if seed is not None:
        # This ensures a new seed for each selection
        seed = seed + 10 * (control_trials + treatment_trials)
    random.seed(seed)
    if control_trials > 1:
        pC = float(control_success) / control_trials
    else:
        pC = 0.5
    if treatment_trials > 1:
        pT = float(treatment_success) / treatment_trials
    else:
        pT = 0.5
    cut = (1 - pT) / ((1 - pT) + (1 - pC))
    test = random.random()
    if test < cut:
        group = control_name
    else:
        group = treatment_name
    return group

### EOF ###
