import itertools


def vlan_range(vlan_list: list[str]) -> str:
    """Given a list that contains elements that are either ranges, return
    a string of comma-separated groups of ranges in ascending order

    Example:
        >>> vlan_range(['1', '2', '3', '5', '6', '7', '10', '11', '12'])
        '1-3,5-7,10-12'
    """
    vlan_list = sorted([int(vlan) for vlan in vlan_list])
    vlan_ranges = []
    for _, g in itertools.groupby(enumerate(vlan_list), key=lambda x: x[1] - x[0]):
        group = [x[1] for x in g]
        if len(group) > 1:
            vlan_ranges.append(f"{group[0]}-{group[-1]}")
        else:
            vlan_ranges.append(str(group[0]))
    return ",".join(vlan_ranges)
