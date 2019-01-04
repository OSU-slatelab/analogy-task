from . import Google, BATS, BMASS
from lib import data_mode, datasets

def parse(analogy_file, dataset, setting, analogy_type, to_lower=False):
    if dataset == datasets.Google:
        analogies = Google.read(analogy_file, to_lower=to_lower)
    elif dataset == datasets.BATS:
        analogies = BATS.read(analogy_file, setting, to_lower=to_lower)
    elif dataset == datasets.BMASS:
        if analogy_type == data_mode.String:
            analogies = BMASS.read(analogy_file, setting, strings_only=True, to_lower=to_lower)
        else:
            analogies = BMASS.read(analogy_file, setting, cuis_only=True, to_lower=to_lower)
    else:
        raise KeyError('Dataset "%s" is unknown' % dataset)
    return analogies
