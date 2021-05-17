from datetime import datetime
from pa.api.oanda_api import API
from pa.settings import api_token, live


def backtest(self, data_path):
    line_count = 0
    if color:
        color_formatters = [
            formatters.Text('Info', style='class:cyan'),
            formatters.Text(': Preparing backtest: '),
            formatters.Bar(sym_a='=', sym_b='=', sym_c=' ', unknown='='),
            formatters.Text(' '),
            formatters.IterationsPerSecond(),
            formatters.Text(' data-points/second'),
            formatters.Text('  ')
        ]
        with ProgressBar(style=style, formatters=color_formatters, color_depth=TRUE_COLOR) as pb:
            for _ in pb(file_size(data_path)):
                line_count += 1
        backtest_message = FormattedText([
            ('class:cyan', 'Info'),
            ('', ': Done, beginning backtest'),
        ])
        print(backtest_message, style=style, color_depth=TRUE_COLOR)
        color_formatters = [
            formatters.Text('Backtest', style='class:cyan'),
            formatters.Text(': ['),
            formatters.Label(),
            formatters.Text(']: '),
            formatters.Bar(sym_a='=', sym_b='=', sym_c=' ', unknown='='),
            formatters.Text(' '),
            formatters.Progress(),
            formatters.Text(' '),
            formatters.TimeLeft(),
            formatters.Text('  ')
        ]
        with ProgressBar(style=style, formatters=color_formatters, color_depth=TRUE_COLOR) as pb:
            # Base Backtest Thread
            def backtest_thread(pb_control, pb_strat_pair, pb_line_count):
                if color:
                    label = FormattedText([
                        ('class:yellow', str(type(pb_strat_pair[0])).split('.')[-1][:-2]),
                        ('', ', '),
                        ('class:yellow', str(type(pb_strat_pair[1])).split('.')[-1][:-2]),
                    ])
                else:
                    label = str(type(pb_strat_pair[0])).split('.')[-1][:-2] + ', ' + \
                            str(type(pb_strat_pair[1])).split('.')[-1][:-2]
                for _ in pb(get_backtest_stream()(pb_control.events, data_path, control.run_flag).gen(),
                            total=pb_line_count, label=label):
                    pass

            control_threads = []
            for strat_pair in backtest_strategies:
                control = Control(strat_pair[0], strat_pair[1], data_path)
                control_threads.append((
                    Thread(
                        target=control.run,
                        daemon=True
                    ),
                    Thread(
                        target=backtest_thread,
                        args=(control, strat_pair, line_count),
                        daemon=True
                    ),
                    control
                ))
            for thread in control_threads:
                thread[2].run_flag.set()
                thread[0].start()
                thread[1].start()

            for thread in control_threads:
                if thread[0].is_alive():
                    thread[0].join()
                if thread[1].is_alive():
                    thread[1].join()
        backtest_message = FormattedText([
            ('class:cyan', 'Info'),
            ('', ': Done, finished backtest'),
        ])
        print(backtest_message, style=style, color_depth=TRUE_COLOR)
    else:
        base_formatters = [
            formatters.Text('Info: Preparing backtest: '),
            formatters.Bar(sym_a='=', sym_b='=', sym_c=' ', unknown='='),
            formatters.Text(' '),
            formatters.IterationsPerSecond(),
            formatters.Text(' data-points/second'),
            formatters.Text('  ')
        ]
        with ProgressBar(formatters=base_formatters) as pb:
            for _ in pb(file_size(data_path)):
                line_count += 1
        print('Info: Done, beginning backtest')
        base_formatters = [
            formatters.Text('Backtest: ['),
            formatters.Label(),
            formatters.Text(']: '),
            formatters.Bar(sym_a='=', sym_b='=', sym_c=' ', unknown='='),
            formatters.Text(' '),
            formatters.IterationsPerSecond(),
            formatters.Text(' data-points/second'),
            formatters.Text(' '),
            formatters.TimeLeft(),
            formatters.Text('  ')
        ]
        with ProgressBar(formatters=base_formatters) as pb:
            # Base Backtest Thread
            def backtest_thread(control, strat_pair, line_count):
                if color:
                    label = FormattedText([
                        ('class:yellow', str(type(strat_pair[0])).split('.')[-1][:-2]),
                        ('', ', '),
                        ('class:yellow', str(type(strat_pair[1])).split('.')[-1][:-2]),
                    ])
                else:
                    label = str(type(strat_pair[0])).split('.')[-1][:-2] + ', ' + \
                            str(type(strat_pair[1])).split('.')[-1][:-2]
                for _ in pb(control.run(), total=line_count, label=label):
                    pass

            control_threads = []
            for strat_pair in backtest_strategies:
                control = Control(strat_pair[0], strat_pair[1], data_path)
                control_threads.append((
                    Thread(
                        target=backtest_thread,
                        args=(control, strat_pair, line_count),
                        daemon=True
                    ),
                    control
                ))
            for thread in control_threads:
                thread[0].start()
                thread[1].events.put(StartEvent())

            for thread in control_threads:
                thread[0].join()
        print('Info: Done, finished backtest')
