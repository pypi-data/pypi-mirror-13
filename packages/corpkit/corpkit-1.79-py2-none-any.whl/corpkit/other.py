def quickview(results, n = 25):
    """view top n results as painlessly as possible.

    :param results: Interrogation data
    :type results: corpkit.interrogation.Interrogation
    :param n: Show top *n* results
    :type n: int
    :returns: None
    """

    import corpkit
    import pandas as pd
    import numpy as np
    import os

    # handle dictionaries too:
    dictpath = 'dictionaries'
    savedpath = 'saved_interrogations'

    # too lazy to code this properly for every possible data type:
    if n == 'all':
        n = 9999

    if type(results) == str:
        if os.path.isfile(os.path.join(dictpath, results)):
            import pickle
            from collections import Counter
            unpickled = pickle.load(open(os.path.join(dictpath, results), 'rb'))
            print '\nTop %d entries in %s:\n' % (n, os.path.join(dictpath, results))
            for index, (w, f) in enumerate(unpickled.most_common(n)):
                fildex = '% 3d' % index
                print '%s: %s (n=%d)' %(fildex, w, f)
            return

        elif os.path.isfile(os.path.join(savedpath, results)):
            from corpkit import load
            print '\n%s loaded temporarily from file:\n' % results
            results = load(results)
        else:
            raise ValueError('File %s not found in saved_interrogations or dictionaries')

    if not 'results' in results.__dict__.keys():
        print results.totals
        return

    datatype = results.results.iloc[0,0].dtype
    if datatype == 'int64':
        option = 't'
    else:
        option = '%'
    if 'operation' in results.query:
        if results.query['operation'].lower().startswith('k'):
            option = 'k'
        if results.query['operation'].lower().startswith('%'):
            option = '%'
        if results.query['operation'].lower().startswith('/'):
            option = '/'

    try:
        the_list = list(results.results.columns)[:n]
    except:
        the_list = list(results.results.index)[:n]

    for index, entry in enumerate(the_list):
        if option == 't':
            tot = results.results[entry].sum()
            print '%s: %s (n=%d)' %(index, entry, tot)
        elif option == '%' or option == '/':
            tot = results.totals[entry]
            totstr = "%.3f" % tot
            print '%s: %s (%s%%)' % (index, entry, totstr)  
        elif option == 'k':
            print '%s: %s' %(index, entry)

def concprinter(df, kind = 'string', n = 100, window = 60, columns = 'all', **kwargs):
    """
    Print conc lines nicely, to string, latex or csv

    :param df: concordance lines from conc()
    :type df: pd.DataFame 
    :param kind: output format
    :type kind: str ('string'/'latex'/'csv')
    :param n: Print first n lines only
    :type n: int/'all'
    :returns: None
    """
    import corpkit
    if n > len(df):
        n = len(df)
    if not kind.startswith('l') and kind.startswith('c') and kind.startswith('s'):
        raise ValueError('kind argument must start with "l" (latex), "c" (csv) or "s" (string).')
    import pandas as pd
    
    # shitty thing to hardcode
    pd.set_option('display.max_colwidth', 100)

    if type(n) == int:
        to_show = df.ix[range(n)]
    elif n is False:
        to_show = df
    elif n == 'all':
        to_show = df
    else:
        raise ValueError('n argument "%s" not recognised.' % str(n))

    def resize_by_window_size(df, window):
        cpd = df.copy()
        lengths = list(cpd['l'].str.len())
        for index, (i, lgth) in enumerate(zip(list(cpd['l']), lengths)):
            if lgth > window:
                cpd.ix[index]['l'] = i[lgth - window:]
        lengths = list(cpd['r'].str.len())
        for index, (i, lgth) in enumerate(zip(list(cpd['r']), lengths)):
            cpd.ix[index]['r'] = i[:window]
        return cpd

    if window:
        to_show = resize_by_window_size(to_show, window)

    if columns != 'all':
        to_show = to_show[columns]

    print ''
    if kind.startswith('s'):
        if 'r' in list(to_show.columns):
            print to_show.to_string(header = False, formatters={'r':'{{:<{}s}}'.format(to_show['r'].str.len().max()).format}, **kwargs)
        else:
            print to_show.to_string(header = False, **kwargs)
    if kind.startswith('l'):
        if 'r' in list(to_show.columns):
            print to_show.to_latex(header = False, formatters={'r':'{{:<{}s}}'.format(to_show['r'].str.len().max()).format}).replace('llll', 'lrrl', 1, **kwargs)
        else:
            print to_show.to_latex(header = False, **kwargs)
    if kind.startswith('c'):
        if 'r' in list(to_show.columns):
            print to_show.to_csv(sep = '\t', header = False, formatters={'r':'{{:<{}s}}'.format(to_show['r'].str.len().max()).format}, **kwargs)
        else:
            print to_show.to_csv(header = False, **kwargs)
    print ''


def save(interrogation, savename, savedir = 'saved_interrogations', print_info = True):
    """
    Save an interrogation as pickle to *savedir*.

       >>> interro_interrogator(corpus, 'words', 'any')
       >>> save(interro, 'savename')

    will create saved_interrogations/savename.p

    :param interrogation: Corpus interrogation to save
    :type interrogation: corpkit interogation/edited result
    
    :param savename: A name for the saved file
    :type savename: str
    
    :param savedir: Relative path to directory in which to save file
    :type savedir: str
    
    :param print_info: Show/hide stdout
    :type print_info: bool
    
    :returns: None
    """

    import pickle
    import os
    from time import localtime, strftime

    def urlify(s):
        "Turn savename into filename"
        import re
        #s = s.lower()
        s = re.sub(r"[^\w\s-]", '', s)
        s = re.sub(r"\s+", '-', s)
        s = re.sub(r"-(textbf|emph|textsc|textit)", '-', s)
        return s

    savename = urlify(savename)

    savename = savename.replace('.p', '')
    
    if not savename.endswith('.p'):
        savename = savename + '.p'

    if savedir:
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        fullpath = os.path.join(savedir, savename)
    else:
        fullpath = savename

    while os.path.isfile(fullpath):
        selection = raw_input("\nSave error: %s already exists in %s.\n\nType 'o' to overwrite, or enter a new name: " % (savename, savedir))
        if selection == 'o' or selection == 'O':
            import os
            os.remove(fullpath)
        else:
            selection = selection.replace('.p', '')
            if not selection.endswith('.p'):
                selection = selection + '.p'
                fullpath = os.path.join(savedir, selection)

    with open(fullpath, 'wb') as fo:
        pickle.dump(interrogation, fo)
    
    time = strftime("%H:%M:%S", localtime())
    if print_info:
        print '\n%s: Data saved: %s\n' % (time, fullpath)

def load(savename, loaddir = 'saved_interrogations'):
    """
    Load saved data into memory:

        >>> loaded = load('interro')

    will load saved_interrogations/interro.p as loaded

    :param savename: Filename with or without extension
    :type savename: str
    
    :param loaddir: Relative path to the directory containg *savename*
    :type loaddir: str
    
    :param only_concs: Set to True if loading concordance lines
    :type only_concs: bool

    :returns: loaded data
    """    
    import pickle
    import os
    if not savename.endswith('.p'):
        savename = savename + '.p'

    if loaddir:
        fullpath = os.path.join(loaddir, savename)
    else:
        fullpath = savename

    with open(fullpath, 'rb') as fo:
        data = pickle.load(fo)
    return data

def new_project(name, loc = '.', root = False):
    """Make a new project in ./*loc*

    :param name: A name for the project
    :type name: str
    :param loc: Relative path to directory in which project will be made
    :type loc: str
    """
    import corpkit
    import os
    import shutil
    import stat
    import platform
    from time import strftime, localtime

    path_to_corpkit = os.path.dirname(corpkit.__file__)
    thepath, corpkitname = os.path.split(path_to_corpkit)
    
    # make project directory
    fullpath = os.path.join(loc, name)
    try:
        os.makedirs(fullpath)
    except:
        if root:
            thetime = strftime("%H:%M:%S", localtime())
            print '%s: Directory already exists: "%s"' %( thetime, fullpath)
            return
        else:
            raise
    # make other directories
    dirs_to_make = ['data', 'images', 'saved_interrogations', \
      'saved_concordances', 'dictionaries', 'exported', 'logs']
    #subdirs_to_make = ['dictionaries', 'saved_interrogations']
    for directory in dirs_to_make:
        os.makedirs(os.path.join(fullpath, directory))
    #for subdir in subdirs_to_make:
        #os.makedirs(os.path.join(fullpath, 'data', subdir))
    # copy the bnc dictionary to dictionaries
    if root:

        # clean this up
        import corpkit
        def resource_path(relative):
            import os
            return os.path.join(
                os.environ.get(
                    "_MEIPASS2",
                    os.path.abspath(".")
                ),
                relative
            )
        corpath = os.path.dirname(corpkit.__file__)
        corpath = corpath.replace('/lib/python2.7/site-packages.zip/corpkit', '')
        baspat = os.path.dirname(corpath)
        dicpath = os.path.join(baspat, 'dictionaries')
        try:
            shutil.copy(os.path.join(dicpath, 'bnc.p'), os.path.join(fullpath, 'dictionaries'))
        except:
            shutil.copy(resource_path('bnc.p'), os.path.join(fullpath, 'dictionaries'))

    # if not GUI
    if not root:
        time = strftime("%H:%M:%S", localtime())
        print '%s: New project created: "%s"' % (time, name)

def interroplot(path, query):
    """Demo function for interrogator/plotter.

        1. Interrogates path with Tregex query, 
        2. Gets relative frequencies
        3. Plots the top seven results

    :param path: path to corpus
    :type path: str
    
    :param query: Tregex query
    :type query: str

    """
    import corpkit
    from corpkit import interrogator
    quickstart = interrogator(path, 'w', query, show = ['w'])
    edited = quickstart.edit('%', 'self', print_info = False)
    edited.plot(str(path))

def load_all_results(data_dir = 'saved_interrogations', **kwargs):
    """
    Load every saved interrogation in data_dir into a dict:

        >>> r = load_all_results()

    :param data_dir: path to saved data
    :type data_dir: str

    :returns: dict with filenames as keys
    """
    import os
    from time import localtime, strftime
    from corpkit.other import load

    def get_root_note(kwargs):
        if 'root' in kwargs.keys():
            root = kwargs['root']
        else:
            root = False
        if 'note' in kwargs.keys():
            note = kwargs['note']
        else:
            note = False       
        return root, note

    root, note = get_root_note(kwargs)
    
    datafiles = [f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) \
                 and f.endswith('.p')]
    output = {}

    l = 0
    for f in datafiles:    
        try:
            loadname = f.replace('.p', '')
            output[loadname] = load(f, loaddir = data_dir)
            time = strftime("%H:%M:%S", localtime())
            print '%s: %s loaded as %s.' % (time, f, loadname)
            l += 1
        except:
            time = strftime("%H:%M:%S", localtime())
            print '%s: %s failed to load. Try using load to find out the matter.' % (time, f)
        if note and len(datafiles) > 3:
            note.progvar.set((index + 1) * 100.0 / len(fs))
        if root:
            root.update()
    time = strftime("%H:%M:%S", localtime())
    print '%s: %d interrogations loaded from %s.' % (time, l, os.path.basename(data_dir))
    return output

def texify(series, n = 20, colname = 'Keyness', toptail = False, sort_by = False):
    """turn a series into a latex table"""
    import corpkit
    import pandas as pd
    if sort_by:
        df = pd.DataFrame(series.order(ascending = False))
    else:
        df = pd.DataFrame(series)
    df.columns = [colname]
    if not toptail:
        return df.head(n).to_latex()
    else:
        comb = pd.concat([df.head(n), df.tail(n)])
        longest_word = max([len(w) for w in list(comb.index)])
        tex = ''.join(comb.to_latex()).split('\n')
        linelin = len(tex[0])
        try:
            newline = (' ' * (linelin / 2)) + ' &'
            newline_len = len(newline)
            newline = newline + (' ' * (newline_len - 1)) + r'\\'
            newline = newline.replace(r'    \\', r'... \\')
            newline = newline.replace(r'   ', r'... ', 1)
        except:
            newline = r'...    &     ... \\'
        tex = tex[:n+4] + [newline] + tex[n+4:]
        tex = '\n'.join(tex)
        return tex


def as_regex(lst, boundaries = 'w', case_sensitive = False, inverse = False):
    """Turns a wordlist into an uncompiled regular expression

    :param lst: A wordlist to convert
    :type lst: list

    :param boundaries:
    :type boundaries: str -- 'word'/'line'/'space'; tuple -- (leftboundary, rightboundary)
    
    :param case_sensitive: Make regular expression case sensitive
    :type case_sensitive: bool
    
    :param inverse: Make regular expression inverse matching
    :type inverse: bool

    :returns: regular expression as string
    """
    import corpkit

    import re
    if case_sensitive:
        case = r''
    else:
        case = r'(?i)'
    if not boundaries:
        boundary1 = r''
        boundary2 = r''
    elif type(boundaries) == tuple or type(boundaries) == list:
        boundary1 = boundaries[0]
        boundary2 = boundaries[1]
    else:
        if boundaries.startswith('w') or boundaries.startswith('W'):
            boundary1 = r'\b'
            boundary2 = r'\b'
        elif boundaries.startswith('l') or boundaries.startswith('L'):
            boundary1 = r'^'
            boundary2 = r'$'
        elif boundaries.startswith('s') or boundaries.startswith('S'):
            boundary1 = r'\s'
            boundary2 = r'\s'
        else:
            raise ValueError('Boundaries not recognised. Use a tuple for custom start and end boundaries.')
    if inverse:
        inverser1 = r'(?!'
        inverser2 = r')'
    else:
        inverser1 = r''
        inverser2 = r''

    if inverse:
        joinbit = r'%s|%s' % (boundary2, boundary1)
        return case + inverser1 + r'(' + boundary1 + joinbit.join(sorted(list(set([re.escape(w) for w in lst])))) + boundary2 + r')' + inverser2
    else:
        return case + boundary1 + inverser1 + r'(' + r'|'.join(sorted(list(set([re.escape(w) for w in lst])))) + r')' + inverser2 + boundary2

def make_multi(interrogation, indexnames = None):    
    """
    make pd.multiindex version of an interrogation (for pandas geeks)

    :param interrogation: a corpkit interrogation
    :type interrogation: a corpkit interrogation, pd.DataFrame or pd.Series

    :param indexnames: pass in a list of names for the multiindex;
                       leave as None to get them if possible from interrogation
                       use False to explicitly not get them
    :type indexnames: list of strings/None/False
    :returns: pd.DataFrame with multiindex"""

    # get proper names for index if possible
    translator = {'f': 'Function',
                  'l': 'Lemma',
                  'a': 'Distance',
                  'w': 'Word',
                  't': 'Trees',
                  'i': 'Index',
                  'n': 'N-grams',
                  'p': 'POS',
                  'g': 'Governor',
                  'd': 'Dependent'}
    import numpy as np
    import pandas as pd
    # determine datatype, get df and cols
    if type(interrogation) == pd.core.frame.DataFrame:
        df = interrogation
        cols = list(interrogation.columns)
    elif type(interrogation) == pd.core.series.Series:
        cols = list(interrogation.index)
        df = pd.DataFrame(interrogation).T
    else:
        cols = list(interrogation.results.columns)
        df = interrogation.results
        # set indexnames if we have them
        if indexnames is not False:
            indexnames = [translator[i] for i in interrogation.query['show']]

    # split column names on slash
    for index, i in enumerate(cols):
        cols[index] = i.split('/')

    # make numpy arrays
    arrays = []
    for i in range(len(cols[0])):
        arrays.append(np.array([x[i] for x in cols]))
    
    # make output df, add names if we have them
    newdf = pd.DataFrame(df.T.as_matrix(), index=arrays).T
    if indexnames:
        newdf.columns.names = indexnames
    pd.set_option('display.multi_sparse', False)
    return newdf
