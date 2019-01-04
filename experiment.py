import os
import sys
import numpy as np
import configparser
from lib import compute_mode, eval_mode, data_mode, datasets
from task import analogyTask
import pyemblib
import configlogger
from drgriffis.common import log

if __name__ == '__main__':

    def _cli():
        import optparse
        parser = optparse.OptionParser(usage='Usage: %prog',
                description='Run the analogy task')
        parser.add_option('--config', dest='config',
                default='config.ini',
                help='configuration file for experiments (default %default)')
        parser.add_option('--embeddings', dest='embeddings',
                help='word/entity embedding file to use (if not provided, defaults to Embeddings field in --config)')
        parser.add_option('--embeddings-mode', dest='embeddings_mode',
                type='choice', choices=list(pyemblib.CLI_Formats.options()), default=pyemblib.CLI_Formats.default(),
                help='format of --embeddings file (default %default); if --embeddings not used,'
                     ' defaults to value of EmbeddingsFormat field in --config')
        parser.add_option('--dataset', dest='dataset',
                help='analogy dataset to run on',
                type='choice', choices=datasets.aslist(), default=None)
        parser.add_option('-l', '--logfile', dest='logfile',
                help='logfile')
        parser.add_option('--predictions-file', dest='predictions_file',
                help='file to write predictions for individual analogies to')
        parser.add_option('--predictions-top-k', dest='report_top_k',
                help='number of predictions to log in the predictions file (default: %default)',
                type='int', default=5)
        parser.add_option('--analogy-type', dest='anlg_type',
                help='type of analogy data to use'
                     ' (options: {0}; default: %default)'.format(', '.join(data_mode.aslist())),
                type='choice', choices=data_mode.aslist(), default=data_mode.default())
        parser.add_option('--analogy-method', dest='analogy_method',
                help='method to use for analogy completion'
                     ' (options: {0}; default: %default)'.format(', '.join(compute_mode.aslist())),
                type='choice', choices=compute_mode.aslist(), default=compute_mode.default())
        parser.add_option('--setting', dest='setting',
                help='analogy evaluation variant'
                     ' (options: {0}; default: %default)'.format(', '.join(eval_mode.aslist())),
                type='choice', choices=eval_mode.aslist(), default=eval_mode.default())
        parser.add_option('--tab-separated', dest='tab_sep',
                action='store_true', default=False,
                help='use if embeddings file uses \\t to separate key from value')
        parser.add_option('--to-lower', dest='to_lower',
                action='store_true', default=False,
                help='lowercase all analogies')
        (options, args) = parser.parse_args()
        if not options.dataset:
            parser.print_help()
            exit()

        return options
    
    options = _cli()
    log.start(logfile=options.logfile)

    t_main = log.startTimer()

    config = configparser.ConfigParser()
    config.read(options.config)

    analogy_file = datasets.getpath(options.dataset, config, options.setting)

    if not options.embeddings:
        options.embeddings = config['Default']['Embeddings']
        options.embeddings_mode = config['Default']['EmbeddingsMode']

    configlogger.writeConfig(log, settings=[
        ('Config file', options.config),
        ('Dataset', options.dataset),
        ('Path to dataset', analogy_file),
        ('Embeddings file', options.embeddings),
        ('Embeddings file mode', options.embeddings_mode),
        ('Analogy type', options.anlg_type),
        ('Computation method', options.analogy_method),
        ('Evaluation setting', options.setting),
        ('Predictions file', options.predictions_file),
        ('Number of predictions to report', options.report_top_k),
        ('Lowercasing analogies/embeddings', options.to_lower),
    ], title='Analogy completion task')

    # only one valid data mode for Google and BATS datasets
    if options.dataset in [datasets.Google, datasets.BATS] and options.anlg_type != data_mode.String:
        log.writeln('[WARNING] Invalid --analogy-type setting for %s dataset; Overriding to "%s"' % (options.dataset, data_mode.String))
        options.anlg_type = data_mode.String

    t_sub = log.startTimer('Reading %s embeddings from %s...' % (options.embeddings_mode, options.embeddings))
    separator = '\t' if options.tab_sep else ' '
    (fmt, mode) = pyemblib.CLI_Formats.parse(options.embeddings_mode)
    embeddings = pyemblib.read(
        options.embeddings,
        format=fmt,
        mode=mode,
        separator=separator,
        lower_keys=options.to_lower
    )
    log.stopTimer(t_sub, 'Read {0:,} embeddings in {1}s.\n'.format(len(embeddings), '{0:.2f}'))

    t_sub = log.startTimer('Running analogy task on %s dataset...' % options.dataset)
    results = analogyTask(
        analogy_file,
        options.dataset,
        options.setting,
        options.anlg_type,
        embeddings,
        log=log,
        predictions_file=options.predictions_file,
        predictions_file_mode='w',
        report_top_k=options.report_top_k,
        to_lower=options.to_lower
    )
    log.stopTimer(t_sub, 'Done in {0:.2f}s.')

    relations = list(results.keys())
    relations.sort()

    check_rels = relations.copy()
    check_rels.append('MACRO RESULTS')
    max_rel_len = max([len(r) for r in check_rels])
    macro_acc, macro_cor, macro_ttl, macro_map, macro_mrr, macro_skipped = [], [], [], [], [], []

    log.writeln('\n--- Results ---')
    log.writeln(('%{0}s |  %5s (%5s/%5s)  %5s  %5s  | %5s'.format(max_rel_len)) % (
        'Relation', 'Acc', 'Cor', 'Ttl', 'MAP', 'MRR', 'Skips'
    ))
    def _writeTableRow(rel, acc, MAP, MRR, correct, total, skipped):
        log.writeln(('%{0}s |  %.3f (%5d/%5d)  %.3f  %.3f  | %5d'.format(max_rel_len)) % (
            rel, acc, correct, total, MAP, MRR, skipped
        ))
    for relation in relations:
        (correct, MAP, MRR, total, skipped, _) = results[relation]
        if total > 0: acc = float(correct)/total
        else: acc = 0
        macro_acc.append(acc)
        macro_cor.append(correct)
        macro_ttl.append(total)
        macro_map.append(MAP)
        macro_mrr.append(MRR)
        macro_skipped.append(skipped)
        _writeTableRow(relation, acc, MAP, MRR, correct, total, skipped)

    _writeTableRow(
        'MACRO RESULTS',
        np.mean(macro_acc),
        np.mean(macro_map),
        np.mean(macro_mrr),
        np.sum(macro_cor),
        np.sum(macro_ttl),
        np.sum(macro_skipped)
    )
        

    log.stopTimer(t_main, message='\nProgram complete in {0:.2f}s.')

    log.stop()
