Card Me
=======

Card Me simplifies the process of parsing and creating iCalendar and vCard objects.
It is a fork of the venerable vobject library, improved, updated, substantially rewritten for Python3 support,
and with some proper unit tests.

[![Build Status](https://travis-ci.org/tBaxter/python-card-me.svg?branch=master)](https://travis-ci.org/tBaxter/python-card-me)

--------------
 Installation
--------------

Requires dateutil 2.4.0: `pip install dateutil`
six should also be installed, if it isn't already: `pip install six`

---------------
 Running tests
---------------

To run unit tests, use `python tests.py` from within the card_me directory.


-------
 Usage
-------

### Creating iCalendar objects


Card Me has a basic datastructure for working with iCalendar-like syntaxes.
Additionally, it defines specialized behaviors for many of
the commonly used iCalendar objects.

To create an object that already has a behavior defined, run:
```
>>> import card_me
>>> cal = card_me.newFromBehavior('vcalendar')
>>> cal.behavior
<class 'card_me.icalendar.VCalendar2_0'>
```

Convenience functions exist to create iCalendar and vCard objects:
```
>>> cal = card_me.iCalendar()
>>> cal.behavior
<class 'card_me.icalendar.VCalendar2_0'>
>>> card = card_me.vCard()
>>> card.behavior
<class 'card_me.vcard.VCard3_0'>
```
Once you have an object, you can use the add method to create children:
```
>>> cal.add('vevent')
<VEVENT| []>
>>> cal.vevent.add('summary').value = "This is a note"
>>> cal.prettyPrint()
 VCALENDAR
    VEVENT
       SUMMARY: This is a note
```
Note that summary is a little different from vevent, it's a ContentLine, not a Component.  
It can't have children, and it has a special value attribute.

ContentLines can also have parameters.  They can be accessed with
regular attribute names with \_param appended:
```
>>> cal.vevent.summary.x_random_param = 'Random parameter'
>>> cal.prettyPrint()
 VCALENDAR
    VEVENT
       SUMMARY: This is a note
       params for  SUMMARY:
          X-RANDOM ['Random parameter']
```
There are a few things to note about this example

  * The underscore in x_random is converted to a dash (dashes are
    legal in iCalendar, underscores legal in Python)
  * X-RANDOM's value is a list.

If you want to access the full list of parameters, not just the first,
use <paramname>\_paramlist:
```
>>> cal.vevent.summary.x_random_paramlist
['Random parameter']
>>> cal.vevent.summary.x_random_paramlist.append('Other param')
>>> cal.vevent.summary
<SUMMARY{'X-RANDOM': ['Random parameter', 'Other param']}This is a note>
```
Similar to parameters, If you want to access more than just the first
child of a Component, you can access the full list of children of a
given name by appending \_list to the attribute name:
```
>>> cal.add('vevent').add('summary').value = "Second VEVENT"
>>> for ev in cal.vevent_list:
...     print(ev.summary.value)
This is a note
Second VEVENT
```
The interaction between the del operator and the hiding of the
underlying list is a little tricky, del cal.vevent and del
cal.vevent_list both delete all vevent children:
```
>>> first_ev = cal.vevent
>>> del cal.vevent
>>> cal
<VCALENDAR| []>
>>> cal.vevent = first_ev
```
card_me understands Python's datetime module and tzinfo classes.
```
>>> import datetime
>>> utc = card_me.icalendar.utc
>>> start = cal.vevent.add('dtstart')
>>> start.value = datetime.datetime(2006, 2, 16, tzinfo = utc)
>>> first_ev.prettyPrint()
     VEVENT
        DTSTART: 2006-02-16 00:00:00+00:00
        SUMMARY: This is a note
        params for  SUMMARY:
           X-RANDOM ['Random parameter', 'Other param']
```
Components and ContentLines have serialize methods:
```
>>> cal.vevent.add('uid').value = 'Sample UID'
>>> icalstream = cal.serialize()
>>> print(icalstream)
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PYVOBJECT//NONSGML Version 1//EN
BEGIN:VEVENT
UID:Sample UID
DTSTART:20060216T000000Z
SUMMARY;X-RANDOM=Random parameter,Other param:This is a note
END:VEVENT
END:VCALENDAR
```
Observe that serializing adds missing required lines like version and
prodid.  A random UID would be generated, too, if one didn't exist.

If dtstart's tzinfo had been something other than UTC, an appropriate
vtimezone would be created for it.

### Parsing iCalendar objects


To parse one top level component from an existing iCalendar stream or
string, use the readOne function:
```
>>> parsedCal = card_me.readOne(icalstream)
>>> parsedCal.vevent.dtstart.value
datetime.datetime(2006, 2, 16, 0, 0, tzinfo=tzutc())
```
Similarly, readComponents is a generator yielding one top level
component at a time from a stream or string.
```
>>> card_me.readComponents(icalstream).next().vevent.dtstart.value
datetime.datetime(2006, 2, 16, 0, 0, tzinfo=tzutc())
```
More examples can be found in source code doctests.

### vCards


Making vCards proceeds in much the same way.
Note that the 'N' and 'FN' attributes are required.
```
>>> j = card_me.vCard()
>>> j.add('n')
 <N{}    >
>>> j.n.value = card_me.vcard.Name( family='Smith', given='Tom' )
>>> j.add('fn')
 <FN{}>
>>> j.fn.value ='Tom Smith'
>>> j.add('email')
 <EMAIL{}>
>>> j.email.value = 'tom.smith@example.com'
>>> j.email.type_param = 'INTERNET'
>>> j.prettyPrint()
 VCARD
    EMAIL: tom.smith@example.com
    params for  EMAIL:
       TYPE ['INTERNET']
    FN: Tom Smith
    N:  Tom Smith
```
serializing will add any required computable attributes (like 'VERSION')
```
>>> j.serialize()
'BEGIN:VCARD\r\nVERSION:3.0\r\nEMAIL;TYPE=INTERNET:tom.smith@example.com\r\nFN:Tom Smith\r\nN:Smith;Tom;;;\r\nEND:VCARD\r\n'
>>> j.prettyPrint()
 VCARD
    VERSION: 3.0
    EMAIL: tom.smith@example.com
    params for  EMAIL:
       TYPE ['INTERNET']
    FN: Tom Smith
    N:  Tom Smith
```
### Parsing vCards
```
>>> s = """
... BEGIN:VCARD
... VERSION:3.0
... EMAIL;TYPE=INTERNET:tom.smith@example.com
... FN:Tom Smith
... N:Smith;Tom;;;
... END:VCARD
... """
>>> v = card_me.readOne( s )
>>> v.prettyPrint()
 VCARD
    VERSION: 3.0
    EMAIL: tom.smith@example.com
    params for  EMAIL:
       TYPE [u'INTERNET']
    FN: Tom Smith
    N:  Tom Smith
>>> v.n.value.family
u'Smith'
```
