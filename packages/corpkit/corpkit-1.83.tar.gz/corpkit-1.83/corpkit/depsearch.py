def dep_searcher(sents,
                 search,
                 show = 'w',
                 dep_type = 'collapsed-ccprocessed-dependencies',
                 regex_nonword_filter = r'[A-Za-z0-9:_]',
                 concordancing = False,
                 exclude = False,
                 excludemode = 'any',
                 searchmode = 'all',
                 lemmatise = False,
                 case_sensitive = False,
                 progbar = False):
    import re
    from corenlp_xml.document import Document
    from collections import Counter
    from corpkit.build import flatten_treestring
    from corpkit.process import filtermaker, animator, get_deps
    """
    search corenlp dependency parse
    1. search for 'search' keyword arg
       governor
       dependent
       function
       pos
       lemma
       word
       index
       etc

    2. exclude entries if need be, using same method as search

    3. return '/'-sep list of 'show' keyword arg, or conc lines:
       governor
       dependent
       function
       pos
       lemma
       word
       index
       distance
       etc
       
       ... or just return int count.
       """

    def distancer(lks, lk):
        "determine number of jumps to root"      
        c = 0
        # get the gov index, stop when it's zero
        root_found = False
        while not root_found:
            if c == 0:
                try:
                    link_to_check = next(i for i in lks if i.dependent.idx == lk.id)
                except StopIteration:
                    root_found = True
                    break
                #link_to_check = lk
            gov_index = link_to_check.governor.idx
            if gov_index == 0:
                root_found = True
            else:
                if c > 29:
                    root_found = True
                    break
                link_to_check = [l for l in lks if l.dependent.idx == gov_index]
                if len(link_to_check) > 0:
                    link_to_check = link_to_check[0]
                else:
                    break
                c += 1
        if c < 30:
            return c

    def get_matches_from_sent(s, search, deps = False, tokens = False, 
        dep_type = 'basic-dependencies', mode = 'all'):
        """process a sentence object, returning matching tok ids"""
        from corpkit.process import get_deps
        lks = []
        if not deps:
            deps = get_deps(s, dep_type)
        if not tokens:
            tokens = s.tokens

        for opt, pat in search.items():
            if type(pat) == list:
                #from corpkit.other import as_regex
                #pat = as_regex(pat, boundaries = '')
                pat = filtermaker(pat, case_sensitive = case_sensitive)
            elif opt == 'g':
                got = []
                for l in deps.links:
                    if re.search(pat, l.governor.text):
                        got.append(s.get_token_by_id(l.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'gf':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        gov_index = l.dependent.idx
                        for l2 in deps.links:
                            if l2.governor.idx == gov_index:
                                got.append(s.get_token_by_id(l2.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'df':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        got.append(s.get_token_by_id(l.governor.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'gl':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.lemma):
                        for i in deps.links:
                            if i.governor.idx == tok.id:
                                got.append(s.get_token_by_id(i.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'gp':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        for i in deps.links:
                            if i.governor.idx == tok.id:
                                got.append(s.get_token_by_id(i.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'dl':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.lemma):
                        for i in deps.links:
                            if i.dependent.idx == tok.id:
                                got.append(s.get_token_by_id(i.governor.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'dp':
                got = []
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        for i in deps.links:
                            if i.dependent.idx == tok.id:
                                got.append(s.get_token_by_id(i.governor.idx))
                got = set(got)
                for i in got:
                    lks.append(i)

            elif opt == 'd':
                got = []
                for l in deps.links:
                    if re.search(pat, l.dependent.text):
                        got.append(s.get_token_by_id(l.governor.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'f':
                got = []
                for l in deps.links:
                    if re.search(pat, l.type):
                        got.append(s.get_token_by_id(l.dependent.idx))
                got = set(got)
                for i in got:
                    lks.append(i)
            elif opt == 'p':
                for tok in tokens:
                    if re.search(pat, tok.pos):
                        lks.append(tok)
            elif opt == 'pl':
                for tok in tokens:
                    from dictionaries.word_transforms import taglemma
                    postag = tok.pos
                    if postag.lower() in taglemma.keys():
                        stemmedtag = taglemma[postag.lower()]
                    else:
                        stemmedtag = postag.lower()
                    if re.search(pat, stemmedtag):
                        lks.append(tok)
            elif opt == 'l':
                for tok in tokens:
                    if re.search(pat, tok.lemma):
                        lks.append(tok)
            elif opt == 'w':
                for tok in tokens:
                    if re.search(pat, tok.word):
                        lks.append(tok)
            elif opt == 'i':
                for tok in tokens:
                    if re.search(pat, str(tok.id)):
                        lks.append(tok)

        if mode == 'all':
            from collections import Counter
            counted = Counter(lks)
            lks = [k for k, v in counted.items() if v >= len(search.keys())]
        
        return lks


    result = []
    numdone = 0

    for s in sents:
        numdone += 1
        deps = get_deps(s, dep_type)
        tokens = s.tokens
        lks = get_matches_from_sent(s, search, deps, tokens, dep_type, mode = searchmode)

        if not concordancing:
            lks = list(set([x for x in lks if x and re.search(regex_nonword_filter, x.word)]))

        if exclude is not False:
            to_remove = get_matches_from_sent(s, exclude, deps, tokens, dep_type, mode = excludemode)

            for i in to_remove:
                try:
                    lks.remove(i)
                except ValueError:
                    pass

        if progbar:
            tstr = '%d/%d' % (numdone, len(sents))
            animator(progbar, numdone, tstr)

        if 'c' in show:
            result.append(len(lks))
            continue

        if concordancing:
            for lk in lks: # for each concordance match
                one_result = []
                if not lk:
                    continue
                windex = int(lk.id) - 1
                speakr = s.speakername
                if not speakr:
                    speakr = ''
                conc_line = [speakr]
                # format a single word correctly
                for tok in s.tokens:

                    single_wd = {}
                    intermediate_result = []
                    if 'w' in show:
                        single_wd['w'] = tok.word
                    if 'l' in show:
                        from dictionaries.word_transforms import wordlist
                        if tok.lemma in wordlist.keys():
                            lem = wordlist[tok.lemma]
                        else:
                            lem = tok.lemma
                        single_wd['l'] = lem
                    if 'p' in show:
                        single_wd['p'] = tok.pos

                    if 'pl' in show:
                        single_wd['pl'] = lk.pos
                        from dictionaries.word_transforms import taglemma
                        if postag.lower() in taglemma.keys():
                            single_wd['pl'] = taglemma[postag.lower()]
                        else:
                            single_wd['pl'] = postag.lower()
                        if not single_wd['pl']:
                            single_wd['pl'] == 'none'

                    if 'r' in show:
                        all_lks = [l for l in deps.links]
                        distance = distancer(all_lks, tok)
                        if distance:
                            single_wd['r'] = str(distance)
                        else:
                            single_wd['r'] = '0'
                    if 'f' in show:
                        for lin in deps.links:
                            single_wd['f'] = '.'
                            if tok.id == lin.dependent.idx:
                                single_wd['f'] = lin.type
                                break
                    if 'i' in show:
                        single_wd['i'] = str(tok.id)

                    for i in show:
                        intermediate_result.append(single_wd[i])
                    one_result.append('/'.join(intermediate_result))
                # now we have formatted tokens as a list. we need to split
                # it into start, middle and end
                start = ' '.join([w for index, w in enumerate(one_result) if index < windex])
                middle = one_result[windex]
                end = ' '.join([w for index, w in enumerate(one_result) if index > windex])
                for bit in start, middle, end:
                    conc_line.append(bit)
                result.append(conc_line)
        else:
            # figure out what to show
            for lk in lks:
                single_result = {}
                if not lk:
                    continue
                if 'w' in show:
                    single_result['w'] = 'none'
                    if lemmatise:
                        single_result['w'] = lk.lemma
                    else:
                        single_result['w'] = lk.word
                if 'l' in show:
                    from dictionaries.word_transforms import wordlist
                    if lk.lemma in wordlist.keys():
                        lem = wordlist[lk.lemma]
                    else:
                        lem = lk.lemma
                    single_result['l'] = lem
                if 'p' in show:
                    single_result['p'] = 'none'
                    postag = lk.pos
                    if lemmatise:
                        from dictionaries.word_transforms import taglemma
                        if postag.lower() in taglemma.keys():
                            single_result['p'] = taglemma[postag.lower()]
                        else:
                            single_result['p'] = postag.lower()
                    else:
                        single_result['p'] = postag
                    if not single_result['p']:
                        single_result['p'] == 'none'

                if 'pl' in show:
                    single_result['pl'] = 'none'
                    postag = lk.pos
                    from dictionaries.word_transforms import taglemma
                    if postag.lower() in taglemma.keys():
                        single_result['pl'] = taglemma[postag.lower()]
                    else:
                        single_result['pl'] = postag.lower()
                    if not single_result['pl']:
                        single_result['pl'] == 'none'

                if 'f' in show:
                    single_result['f'] = 'none'
                    for i in deps.links:
                        if i.dependent.idx == lk.id:
                            single_result['f'] = i.type.rstrip(',')
                            break
                    if single_result['f'] == '':
                        single_result['f'] = 'root'

                if 'g' in show:
                    single_result['g'] = 'none'
                    for i in deps.links:
                        if i.dependent.idx == lk.id:
                            if s.get_token_by_id(i.governor.idx):
                                if lemmatise:                          
                                        single_result['g'] = s.get_token_by_id(i.governor.idx).lemma
                                else:
                                    single_result['g'] = i.governor.text
                            else:
                                single_result['g'] = 'root'
                            break

                if 'd' in show:
                    single_result['d'] = 'none'
                    for i in deps.links:
                        if i.governor.idx == lk.id:
                            if s.get_token_by_id(i.dependent.idx):       
                                if lemmatise:
                                    single_result['d'] = s.get_token_by_id(i.dependent.idx).lemma
                                else:
                                    single_result['d'] = i.dependent.text
                            break

                if 'gl' in show:
                    single_result['gl'] = 'none'
                    for i in deps.links:
                        if i.dependent.idx == lk.id:
                            if s.get_token_by_id(i.governor.idx):
                                single_result['gl'] = s.get_token_by_id(i.governor.idx).lemma
                            else:
                                single_result['gl'] = 'root'
                            break

                if 'dl' in show:
                    single_result['dl'] = 'none'
                    for i in deps.links:
                        if i.governor.idx == lk.id:
                            if s.get_token_by_id(i.dependent.idx):       
                                single_result['dl'] = s.get_token_by_id(i.dependent.idx).lemma
                            break

                if 'r' in show:
                    all_lks = [l for l in deps.links]
                    distance = distancer(all_lks, lk)
                    if distance:
                        single_result['r'] = str(distance)
                    else:
                        single_result['r'] = '0'

                if 'i' in show:
                    single_result['i'] = str(lk.id)

                if 'c' not in show:
                    
                    # add them in order
                    out = []
                    for i in show:
                        out.append(single_result[i])

                    result.append('/'.join(out))
    
    if 'c' in show:
        result = sum(result)

    return result