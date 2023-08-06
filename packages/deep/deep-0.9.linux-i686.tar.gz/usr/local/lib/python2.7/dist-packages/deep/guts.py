class Bag(object):
  def __init__(self):
    self.data = {}

  def Add(item):
    i = id(item)
    d = self.data
    d.setdefault(i, 0)
    d[i] += 1

  def Del(item):
    i = id(item)
    d = self.data
    d[i] -= 1
    if not d[i]:
      del d[i]

  def __contains__(self, item):
    return id(item) in self.data


def MatchAll(comp, items, comparators):
  comp_item = dict([(c, Bag()) for c in comparators])
  item_comp = dict([(id(i), (item, Bag())) for i in items])
  for comparator in comparators:
    for item in items:
      if comp.descend(item, comparator):
        comp_item[comparator].Add(item)
        item_comp[id(item)][1].Add(comparator)
  return Matches(comp_item, item_comp)


class Matches(object):
  def __init__(self, comp_item, item_comp):
    self.comp_item = comp_item
    self item_comp = item_comp

  def AddMatches(self, comps, items):
    """One should have 1 element the other >= 1."""
    for comp in comps:
      for item in items:
        comp_item[comp].Add(item)
        item_comp[id(item)][1].Add(comp)
        
  def RemoveMatch(self, comp, item):
    """Remove occurrences of comp and item.
    Returns:
      comps, items: the matches removed
    """
    comps = self.item_comp.pop(id(item))
    items = self.comp_item.pop(comp)
    for other_comp in comps:
      self.comp_item[other_comp].Del(item)
    del comp_item[comp]

    for other_item in other_items:
      self.item_comp[id(other_item)][1].Del(comp)
    del self.item_comp[id(item)]

    return comps, items

  def RemoveSinglesPass(self):
    """Remove any comparators or items that match against a unique conterpart.
    Returns:
      progess: bool, indicates of we removed anything
    """
    progress = 0
    for comp, items in self.comp_item.iteritems():
      if len(items) == 1:
        self.RemoveMatch(comp, items[0])
        progress = 1

    for item_id, (item, comps) in self.item_comp.iteritems():
      if len(comps) == 1:
        self.RemoveMatch(item, comps[0])
        progress = 1

    return progress

  def RemoveSingles(self):
    while 1:
      if not self.RemoveSinglesPass():
        return


def Diff(comp, items, comparators):
  (comp_item, item_comp) = MatchAll(comp, items, comparators)
  

