"""Graph functions for tips.py"""

### API ###

def auto(data):
    """
    Return automatically selected graph based on term window size.
    """
    data = [int(round(i)) for i in data] # Graph only deals with int, not float.
    result = _get_term_size()

    if not result:
        print "Failed to get terminal size."
        return vertical_side_nums(data)
    else:
        if result[1] - 1 < max(data) or result[0] - 3 < len(data):
            return horizontal(data)
        else:
            return vertical_side_nums(data)

def horizontal(data, bar_char="#"):
    """
    Return horizontal bar graph as line by line list to be iterated on.
    Optionally use args as characters.
    """
    graph = []
    max_length = _get_term_size()[0] - (3 + len(str(max(data))))

    if max(data) > max_length:
        for_bars = [(i / 2) if (i / 2) > 0 else 1 for i in data]

        for real, build in zip(data, for_bars):
            bar = bar_char * (build - 1) + '\033[34m' + '*' + '\033[0m'

            if build > max_length:
                graph.append("%s... - %s (Too big)" % ((max_length-13) * bar_char, real))
            else:
                graph.append("%s - %s" % (bar, real))

    else:
        for item in data:
            bar = bar_char * (item - 1) + '\033[34m' + '*' + '\033[0m'
            graph.append("%s - %s" % (bar, item))

    return graph

def vertical_side_nums(data, bar_char="#", top_char="*", resize=True):
    """
    Return vertical bar graph with values along left side as a list to be printed.
    """
    graph = []
    print_graph = []
    original = None

    if not _get_term_size():
        resize = False

    if resize:
        join_char = _resize_width(data)
    else:
        join_char = " "

    ## The top of the graph is the height of the tallest bar.
    graph_size = max(data)

    bars = _generate_bars(data, bar_char, top_char)

    ## Give us remaining whitespace from the smaller bars to the top.
    for item in bars:
        item.extend([" "] * (graph_size - len(item)))

    ## Add the highest current element in each bar to the current line.
    for i in xrange(graph_size):
        current_line = []

        for item in bars:
            current_line.append(item.pop())

        graph.append(current_line)

    graph = _side_nums(data, graph, join_char)

    for row in graph:
        print_graph.append(join_char.join(row))

    return print_graph

def vertical_bar_nums(data, bar_char="#", top_char="*", resize=True):
    """
    Return vertical bar graph with values on top of bars as a list to be printed.
    """
    graph = []
    print_graph = []

    if resize:
        term_width, term_height = _get_term_size()

        if term_width != None and term_width < (len(data) * 2) - 1:
            join_char = ""
        else:
            join_char = " "
    else:
        join_char = " "

    ## The top of the graph is the height of the tallest bar.
    graph_size = max(data) + 3

    bars = _generate_bars(data, bar_char, top_char)
    bars = _bar_nums(data, bars)

    ## Gives us remaining whitespace from the smaller bars to the top.
    for item in bars:
        item.extend([" "] * (graph_size - len(item)))

    ## Add the highest current element in each bar to the current line.
    for i in xrange(graph_size):
        current_line = []

        for item in bars:
            current_line.append(item.pop())

        graph.append(current_line)

    for row in graph:
        print_graph.append(join_char.join(row))

    return print_graph



### Graph Building Functions ###

def _generate_bars(data, bar_char, top_char):
    """Generate bar per item in data, and return as list."""
    bars = []

    for item in data:
        bar = []
        bar.extend([bar_char] * (item - 1))
        bar.append("\033[34m{0}\033[0m".format(top_char))
        bars.append(bar)

    return bars

def _side_nums(data, graph, join_char):
    """
    For item (int) in data, add to side of graph at correct position.

    If graph resized by height, pass in original data set for accurate side nums.
    """
    used_nums = []
    zero_pad = len(str(max(data))) # Padding for zfill
    padding = " " * zero_pad # Padding for rows with no amounts.

    if join_char == "":
        num_spacing = " "
    else:
        num_spacing = ""

    ## Add amounts to left of graph.
    for i in data:
        if i not in used_nums:
            graph[i*-1] = [str(i).zfill(zero_pad)] + [num_spacing] + graph[i*-1]
        used_nums.append(i)

    ## Add whitespace to rows with no amounts to the left.
    for index, row in enumerate(graph):
        try:
            int(row[0])
        except ValueError:
            graph[index] = [padding] + [num_spacing] + row

    return graph

def _bar_nums(data, bars):
    """For item (int) in data, add on top of each bar of the graph."""
    for item, bar in zip(data, bars):
        reversed_item = list(reversed(str(item)))
        bar.extend(reversed_item)

    return bars

def _get_term_size():
    """
    Return width, height of current terminal.
    Uses backports or falls back to tput command on unix systems.
    """
    try:
        from backports import shutil_get_terminal_size
        size = shutil_get_terminal_size.get_terminal_size()

        return size.columns, size.lines
    except ImportError:
        import subprocess

        try:
            return int(subprocess.check_output(('tput', 'cols'))), \
                    int(subprocess.check_output(('tput', 'lines')))
        except OSError:
            return False

def _resize_width(data):
    """
    Resize graph based on window width and data set. Return join_char.
    """
    term_width = _get_term_size()[0]

    if (len(data) * 2) + 3 > term_width:
        return ""
    else:
        return " "
