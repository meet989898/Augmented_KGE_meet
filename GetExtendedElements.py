def get_elements(relation, elem_type, domains_dict, ranges_dict):
    """
    Retrieves the set of elements (domain or range) for a given relation.

    :param relation: Relation ID or name
    :param elem_type: Either 'domain' or 'range'
    :param domains_dict: {relation: set of domain entities}
    :param ranges_dict: {relation: set of range entities}
    :return: Set of entities
    """
    if elem_type == "domain":
        return domains_dict.get(relation, set())
    elif elem_type == "range":
        return ranges_dict.get(relation, set())
    else:
        raise ValueError("elem_type must be 'domain' or 'range'")

def get_extended_elements(relation, elem_type, compatible_relations, domains_dict, ranges_dict):
    """
    Computes the union of compatible elements for one-hop extended corruption.

    :param relation: Relation ID or name
    :param elem_type: 'domain' or 'range'
    :param compatible_relations: Dict with format {(r, elem_type): [(r', elem_type'), ...]}
    :param domains_dict: Dictionary of relation → domain entity set
    :param ranges_dict: Dictionary of relation → range entity set
    :return: Union of compatible elements (set)
    """
    extended = set()
    for (rel_prime, type_prime) in compatible_relations.get((relation, elem_type), []):
        elements = get_elements(rel_prime, type_prime, domains_dict, ranges_dict)
        extended.update(elements)
    return extended

# Is this the correct format????:
# domains = { 'r': {1, 2, 3}, 'r1': {4, 5}, 'r2': {6} }
# ranges =  { 'r': {10, 11}, 'r2': {12, 13} }
# compat = { ('r', 'domain'): [('r1', 'domain'), ('r2', 'range')] }
# get_extended_elements('r', 'domain', compat, domains, ranges) -> {4, 5, 12, 13}

def build_compatible_relations(dom_dom, dom_ran, ran_dom, ran_ran):
    """
    Constructs a unified compatible_relations dictionary based on type of compatibility.

    :param dom_dom: {r: [r']} domain-domain compatible
    :param dom_ran: {r: [r'']} domain-range compatible
    :param ran_dom: {r: [r'']} range-domain compatible
    :param ran_ran: {r: [r']} range-range compatible
    :return: Dictionary {(r, elem_type): [(r', elem_type'), ...]}
    """
    compatible_relations = {}
    all_relations = set(dom_dom.keys()) | set(dom_ran.keys()) | set(ran_dom.keys()) | set(ran_ran.keys())

    for r in all_relations:
        domain_compat = []
        range_compat = []

        if r in dom_dom:
            domain_compat.extend([(r_prime, "domain") for r_prime in dom_dom[r]])
        if r in dom_ran:
            domain_compat.extend([(r_prime, "range") for r_prime in dom_ran[r]])
        if r in ran_dom:
            range_compat.extend([(r_prime, "domain") for r_prime in ran_dom[r]])
        if r in ran_ran:
            range_compat.extend([(r_prime, "range") for r_prime in ran_ran[r]])

        compatible_relations[(r, "domain")] = domain_compat
        compatible_relations[(r, "range")] = range_compat

    return compatible_relations
