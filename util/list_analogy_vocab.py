import configparser
import codecs
from lib import datasets, eval_mode, data_mode
import parsers
import configlogger
from drgriffis.common import log

if __name__ == '__main__':
    def _cli():
        import optparse
        parser = optparse.OptionParser(usage='Usage: %prog VOCABF')
        parser.add_option('--config', dest='config',
                default='config.ini',
                help='configuration file for experiments (default %default)')
        parser.add_option('--dataset', dest='dataset',
                help='analogy dataset to run on',
                type='choice', choices=datasets.aslist(), default=None)
        parser.add_option('--to-lower', dest='to_lower',
                action='store_true', default=False,
                help='lowercase all analogies')
        parser.add_option('-l', '--logfile', dest='logfile',
                help='name of file to write log contents to (empty for stdout)',
                default=None)
        (options, args) = parser.parse_args()
        if len(args) != 1 or not options.dataset:
            parser.print_help()
            exit()
        return args, options
    (vocabf,), options = _cli()
    log.start(logfile=options.logfile)

    config = configparser.ConfigParser()
    config.read(options.config)

    analogy_file = datasets.getpath(options.dataset, config, eval_mode.ALL_INFO)

    configlogger.writeConfig(log, settings=[
        ('Config file', options.config),
        ('Dataset', options.dataset),
        ('Path to dataset', analogy_file),
        ('Lowercasing analogies', options.to_lower),
        ('Output vocab file', vocabf),
    ], title='Vocabulary extraction from analogy dataset')

    log.writeln('Reading %s analogies from %s...' % (options.dataset, analogy_file))
    analogies = parsers.parse(
        analogy_file,
        options.dataset,
        eval_mode.ALL_INFO,
        data_mode.String,
        to_lower=options.to_lower
    )
    log.writeln('Read {0:,} analogies in {1:,} relations.\n'.format(
        sum([len(anlg_set) for anlg_set in analogies.values()]),
        len(analogies)
    ))

    log.writeln('Extracting vocabulary...')
    vocab = set()
    for (_, anlg_set) in analogies.items():
        for (a,b,c,d) in anlg_set:
            vocab.add(a)
            vocab.add(c)
            if options.dataset != datasets.Google:
                for _b in b:
                    vocab.add(_b)
                for _d in d:
                    vocab.add(_d)
            else:
                vocab.add(b)
                vocab.add(d)
    log.writeln('Found {0:,} unique word types.\n'.format(len(vocab)))

    log.writeln('Writing vocab to %s...' % vocabf)
    vocab = list(vocab)
    vocab.sort()

    with codecs.open(vocabf, 'w', 'utf-8') as stream:
        for v in vocab:
            stream.write('%s\n' % v)
    log.writeln('Done.')

    log.stop()
