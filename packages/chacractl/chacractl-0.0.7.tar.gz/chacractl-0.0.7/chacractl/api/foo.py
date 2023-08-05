

if isinstance(res, dict):
    for field in FIELDS:
        try:
            value = res[field]
            print u'\n{0}:\n{1}'.format(field, value)
        except KeyError:
            pass



    if type(res) == type(dict()):
        for field in FIELDS:
            if field in res.keys():
                if res[field] != "" :
                    # use default encoding, check out sys.setdefaultencoding
                    print u'\n{0}:\n{1}'.format(field, res[field])
                    # or use specific encoding, e.g. utf-8
                    #print '\n{0}:\n{1}'.format(field, res[field].encode('utf-8'))
