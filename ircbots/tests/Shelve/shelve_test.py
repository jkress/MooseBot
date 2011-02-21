import ConfigParser
import shelve 

def test_a_shelf():
    config = ConfigParser.SafeConfigParser('../../config/ircbots.cfg')
    data = config.get('AutoOp', 'users')
    key = "users"

    d = shelve.open('autoop.db')
    d[key] = data 

    data = d[key]


    flag = d.has_key(key)
    klist = d.keys()

    print klist

    #d['xx'] = range(4)
    #d['xx'].append(5)

    #temp = d('xx')
    #temp.append(5)
    #d['xx'] = temp

    d.close() 
