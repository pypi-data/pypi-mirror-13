from time import sleep
from api import Api
from contact_manager import ContactManager
from attribute_manager import AttributeManager
from list_manager import ListManager
token = '1Y/lGJluBC16wdnvCI4tIdGERpFi5AKCJGNPuW0DcX3PuQ2L+lJeKw07u8+kmqBF23kSZcpeG4oz/0TWEisAS+gHCLxTgy79ZeiJ7KlQE/7gIGF5MhCm41aWuBBYxBzLf+bd/ZoNhMeH0Ux00dcKvu6l9WBZKtQkH403Y1dH14NKdcwsx2obaumww4U3Ph7uHM1b1F3DVhLtGcLnc+WpHW1c3HE17o9QRLGJyD2vWuJXSb7lppO9eoESmVFM7v6'

gan_api = Api(token)
gan_api.batch_size = 4
am = ContactManager(gan_api)
list_manager = ListManager(gan_api)
"""'page': 1"""

#all_attr = am.all(start=4, stop=5)#query(filters={})
ras = am.get('rasmus.lager@chas.se')

#lst = list_manager.get('HzuNi2HYB1')

#lst.description = 'Fint skare va'
#lst.save()
import pdb; pdb.set_trace()
#lst.cancelled
#ras.subscribe_to(lst)
#ras.save()
#ras.lists = []
#ras.email = 'rasmuslager@chas.se'
#new_ras = ras.save()

#import pdb; pdb.set_trace()

#new_ras.unsubscribe_from(lst)

#newer = new_ras.save()


#import pdb; pdb.set_trace()

#newer.remove_from(lst)

#newer.save()


#gen = Indexable(all_attr)
#print len([gen for gen in gen])
#import pdb; pdb.set_trace()
#lst = [page for page in gen]
#all_attr.next()

#all_attr.next()

#all_attr.next()

#all_attr.next()
#all_attr.next()
#all_attr.next()
#all_attr.next()

#for l in all_attr:
#    print l.email
    #sleep(0.5)
    #print str(l)
    #print '----------'

#import pdb; pdb.set_trace()