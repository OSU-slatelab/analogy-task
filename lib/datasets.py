Google='Google'
BATS='BATS'
BMASS='BMASS'

def aslist():
    return [BMASS, Google]

def getpath(key, config, setting):
    if key == Google:
        return config['Google']['AllModes']
    if key == BATS:
        return config['BATS']['AllModes']
    elif key == BMASS:
        return config['BMASS'][setting]
    else:
        raise KeyError('Dataset "%s" is unknown!' % key)
