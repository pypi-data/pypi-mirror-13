This package provides an RDF-based web service that describes the knowledge
assets of the Early Detection Research Network (EDRN).


Functional Tests
================

To demonstrate the code, we'll classes in a series of functional tests.  And
to do so, we'll need a test browser::

    >>> app = layer['app']
    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
    >>> portal = layer['portal']    
    >>> portalURL = portal.absolute_url()

Here we go.


RDF Source
==========

An RDF Source is a source of RDF data.  They can be added anywhere in the
portal::


    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='edrn-rdf-rdfsource')
    >>> l.url.endswith('++add++edrn.rdf.rdfsource')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'A Simple Source'
    >>> browser.getControl(name='form.widgets.description').value = u"It's just for functional tests."
    >>> browser.getControl(name='form.widgets.active:list').value = False
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'a-simple-source' in portal.keys()
    True
    >>> source = portal['a-simple-source']
    >>> source.title
    u'A Simple Source'
    >>> source.description
    u"It's just for functional tests."
    >>> source.active
    False

Now, these things are supposed to produce RDF when called with the appropriate
view.  Does it?

    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    Traceback (most recent call last):
    ...
    ValueError: The RDF Source at /plone/a-simple-source does not have an active RDF file to send

It doesn't because it hasn't yet made any RDF files to send, and it can't do
that without an RDF generator.  RDF Sources get their data from RDF
Generators.


RDF Generators
==============

RDF Generators have the responsibility of accessing various sources of data
(notably the DMCC's web service) and yielding an RDF graph, suitable for
serializing into XML or some other format.  There are several kinds available.


Null RDF Generator
------------------

One such generator does absolutely nothing: it's the Null RDF Generator, and
all it ever does it make zero statements about anything.  It's not very
useful, but it's nice to have for testing.  Check it out::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='edrn-rdf-nullrdfgenerator')
    >>> l.url.endswith('++add++edrn.rdf.nullrdfgenerator')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Silence'
    >>> browser.getControl(name='form.widgets.description').value = u'Just for testing.'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'silence' in portal.keys()
    True
    >>> generator = portal['silence']
    >>> generator.title
    u'Silence'
    >>> generator.description
    u'Just for testing.'

We'll set up our RDF source with this generator (and hand-craft the POST
because it's AJAX)::

    >>> from urllib import urlencode
    >>> browser.open(portalURL + '/a-simple-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': '/plone/silence',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> if source.active: postParams['form.widgets.active:list'] = 'selected'
    >>> browser.post(portalURL + '/a-simple-source/@@edit', urlencode(postParams))
    >>> source.generator.to_object.title
    u'Silence'
    >>> browser.open(portalURL + '/a-simple-source')
    >>> browser.contents
    '...Generator...href="http://nohost/plone/silence"...Silence...'

The RDF source still doesn't produce any RDF, though::

    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    Traceback (most recent call last):
    ...
    ValueError: The RDF Source at /plone/a-simple-source does not have an active RDF file to send

That's because having the generator isn't enough.  Someone has to actually
*run* the generator.


Running the Generators
----------------------

Tickled by either a cron job or a Zope clock event, a special URL finds every
RDF source and asks it to run its generator to produce a fresh update.  Each
RDF source may (in the future) run its validators against the generated graph
to ensure it has the expected information.  Assuming it passes muster, the
source then saves that output as the latest and greatest RDF to deliver when
demanded.

Tickling::

    >>> browser.open(portalURL + '/@@updateRDF')

And is there any RDF?  Let's check::

    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    Traceback (most recent call last):
    ...
    ValueError: The RDF Source at /plone/a-simple-source does not have an active RDF file to send

Still no RDF?!  Right, because RDF Sources can be active or not.  If they're
active, then when it's time to generate RDF their generator will actually get
run.  But the source "A Simple Source" is *not* active.  We didn't check the
active box when we made it.  So, let's fix that and re-tickle::

    >>> browser.open(portalURL + '/a-simple-source/edit')
    >>> browser.getControl(name='form.widgets.active:list').value = True
    >>> browser.getControl(name='form.buttons.save').click()
    >>> browser.open(portalURL + '/@@updateRDF')
    >>> browser.contents
    '...Sources updated:...<span id="numberSuccesses">1</span>...'

That looks promising: one source got updated.  I hope it was our simple source::

    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    >>> browser.isHtml
    False
    >>> browser.headers['content-type']
    'application/rdf+xml'
    >>> browser.contents
    '<?xml version="1.0" encoding="UTF-8"?>\n<rdf:RDF\n   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"\n>\n</rdf:RDF>\n'

Finally, an RDF graph that makes absolutely no statements!

    The Simple Source now contains a single File object:
    >>> len(source.keys())
    1
    >>> generatedFileID = source.keys()[0]
    >>> generatedFileID.startswith('file.')
    True
    >>> source.approvedFile.to_object.id == generatedFileID
    True

If we re-generate all active RDF, the generator will detect that new file
matches the old and won't bother changing anything in the source::

    >>> browser.open(portalURL + '/@@updateRDF')
    >>> browser.contents
    '...Sources updated:...<span id="numberSuccesses">0</span>...'
    >>> source.approvedFile.to_object.id == generatedFileID
    True

By the way, that "updateRDF" is a Zope view that's available at the site root
only::

    >>> browser.open(portalURL + '/a-simple-source/@@updateRDF')
    Traceback (most recent call last):
    ...
    NotFound:   <h2>Site Error</h2>
    ...

Now, how about some RDF that *makes a statement*?


Simple DMCC RDF Generator
-------------------------

The Simple DMCC RDF Generator uses straightforward mappings of the DMCC's
terrible web service output and into RDF statements.  They can be created
anywhere:

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='edrn-rdf-simpledmccrdfgenerator')
    >>> l.url.endswith('++add++edrn.rdf.simpledmccrdfgenerator')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Organs'
    >>> browser.getControl(name='form.widgets.description').value = u'Generates lists of organs.'
    >>> browser.getControl(name='form.widgets.webServiceURL').value = u'testscheme://localhost/ws_newcompass.asmx?WSDL'
    >>> browser.getControl(name='form.widgets.operationName').value = u'Body_System'
    >>> browser.getControl(name='form.widgets.verificationNum').value = u'0'
    >>> browser.getControl(name='form.widgets.uriPrefix').value = u'urn:testing:data:organ:'
    >>> browser.getControl(name='form.widgets.identifyingKey').value = u'Identifier'
    >>> browser.getControl(name='form.widgets.typeURI').value = u'urn:testing:types:organ'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'organs' in portal.keys()
    True
    >>> generator = portal['organs']
    >>> generator.title
    u'Organs'
    >>> generator.description
    u'Generates lists of organs.'
    >>> generator.webServiceURL
    u'testscheme://localhost/ws_newcompass.asmx?WSDL'
    >>> generator.operationName
    u'Body_System'
    >>> generator.verificationNum
    u'0'
    >>> generator.uriPrefix
    u'urn:testing:data:organ:'
    >>> generator.identifyingKey
    u'Identifier'
    >>> generator.typeURI
    u'urn:testing:types:organ'

We've got the generator, but we need to tell it how to map from the DMCC's
awful quasi-XML tags and into RDF predicates.  To do so, we add Predicate
Handlers to the Simple DMCC RDF Generator.  There are a few kinds:

• Literal Predicate Handlers that map a clumsy DMCC key to a predicate whose
  object is a literal value.
• Reference Predicate Handlers that map an inept DMCC key to a predicate whose
  object is a reference to another object, identified by its subject URI.
• Multi Literal Predicate Handlers map an awkward DMCC key that contains
  values separated by commas to multiple statements, one object per
  comma-separated value.
• Various specialized handlers for DMCC's other cumbersome cases.

Note that predicate handlers must be added to Simple DMCC RDF Generators; they
can't be added elsewhere::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='edrn-rdf-literalpredicatehandler')
    Traceback (most recent call last):
    ...
    LinkNotFoundError


Literal Predicate Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~

For organs, we need only to use the Literal Predicate Handler::

    >>> browser.open(portalURL + '/organs')
    >>> l = browser.getLink(id='edrn-rdf-literalpredicatehandler')
    >>> l.url.endswith('++add++edrn.rdf.literalpredicatehandler')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'item_Title'
    >>> browser.getControl(name='form.widgets.description').value = u'Maps the <item_Title> key to the Dublin Core title predicate URI.'
    >>> browser.getControl(name='form.widgets.predicateURI').value = u'http://purl.org/dc/terms/title'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'item_title' in generator.keys()
    True
    >>> predicateHandler = generator['item_title']
    >>> predicateHandler.title
    u'item_Title'
    >>> predicateHandler.description
    u'Maps the <item_Title> key to the Dublin Core title predicate URI.'
    >>> predicateHandler.predicateURI
    u'http://purl.org/dc/terms/title'

That takes care of mapping <Title> to http://purl.org/dc/terms/title.  Now for
the <Description> key in the blundering DMCC output::

    >>> browser.open(portalURL + '/organs')
    >>> browser.getLink(id='edrn-rdf-literalpredicatehandler').click()
    >>> browser.getControl(name='form.widgets.title').value = u'Description'
    >>> browser.getControl(name='form.widgets.description').value = u'Maps the <Description> key to the DC description term.'
    >>> browser.getControl(name='form.widgets.predicateURI').value = u'http://purl.org/dc/terms/description'
    >>> browser.getControl(name='form.buttons.save').click()

The Simple DMCC RDF Generator for organs is now ready.  We'll set it up as the
generator for our simple source::

    >>> browser.open(portalURL + '/a-simple-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': '/plone/organs',
    ...     'form.widgets.approvedFile:list': source.approvedFile.to_path if source.approvedFile else '',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> if source.active: postParams['form.widgets.active:list'] = 'selected'
    >>> browser.post(portalURL + '/a-simple-source/@@edit', urlencode(postParams))
    >>> source.generator.to_object.title
    u'Organs'
    >>> browser.open(portalURL + '/a-simple-source')
    >>> browser.contents
    '...Generator...href="http://nohost/plone/organs"...Organs...'

Tickling::

    >>> browser.open(portalURL + '/@@updateRDF')

And now::

    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    >>> browser.headers['content-type']
    'application/rdf+xml'
    >>> import rdflib
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    66
    >>> namespaceURIs = [i[1] for i in graph.namespaces()]
    >>> namespaceURIs.sort()
    >>> namespaceURIs[0]
    rdflib.term.URIRef(u'http://purl.org/dc/terms/')
    >>> subjects = frozenset([unicode(i) for i in graph.subjects() if unicode(i)])
    >>> subjects = list(subjects)
    >>> subjects.sort()
    >>> subjects[0:3]
    [u'urn:testing:data:organ:1', u'urn:testing:data:organ:10', u'urn:testing:data:organ:11']
    >>> predicates = frozenset([unicode(i) for i in graph.predicates()])
    >>> predicates = list(predicates)
    >>> predicates.sort()
    >>> predicates[0:2]
    [u'http://purl.org/dc/terms/title', u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type']
    >>> objects = [unicode(i) for i in graph.objects() if isinstance(i, rdflib.term.Literal)]
    >>> objects.sort()
    >>> objects[0:5]
    [u'Bladder', u'Blood', u'Bone', u'Brain', u'Breast']

Now that's some fine looking RDF.


Empty Values
............

The DMCC's web services are "full" of "empty" information.  In our organ test
data, we reflect this in the entry for "Bone": it has an empty "Description"
field.  When a field like this is empty, the corresponding RDF graph should
not contain an empty statement about Bone's description.

Note::

    >>> results = graph.query('''select ?description where {
    ...    <urn:testing:data:organ:3> <http://purl.org/dc/terms/description> ?description .
    ... }''')
    >>> len(results)
    0

Looks good.


Reference Predicate Handlers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Diseases are another topic covered by the DMCC.  Diseases affect specific
organs, so they give us an opportunity to demonstrate Reference Predicate
Handlers.  First, we'll make a new Simple DMCC RDF Generator::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='edrn-rdf-simpledmccrdfgenerator').click()
    >>> browser.getControl(name='form.widgets.title').value = u'Diseases'
    >>> browser.getControl(name='form.widgets.description').value = u'Generates lists of diseases.'
    >>> browser.getControl(name='form.widgets.webServiceURL').value = u'testscheme://localhost/ws_newcompass.asmx?WSDL'
    >>> browser.getControl(name='form.widgets.operationName').value = u'Disease'
    >>> browser.getControl(name='form.widgets.verificationNum').value = u'0'
    >>> browser.getControl(name='form.widgets.uriPrefix').value = u'urn:testing:data:disease:'
    >>> browser.getControl(name='form.widgets.identifyingKey').value = u'Identifier'
    >>> browser.getControl(name='form.widgets.typeURI').value = u'urn:testing:types:disease'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> generator = portal['diseases']

Now a couple Literal Predicate Handler to handle the basics like title, etc.::

    >>> browser.open(portalURL + '/diseases')
    >>> browser.getLink(id='edrn-rdf-literalpredicatehandler').click()
    >>> browser.getControl(name='form.widgets.title').value = u'item_Title'
    >>> browser.getControl(name='form.widgets.description').value = u'Maps the <item_Title> key to the Dublin Core title predicate URI.'
    >>> browser.getControl(name='form.widgets.predicateURI').value = u'http://purl.org/dc/terms/title'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> browser.open(portalURL + '/diseases')
    >>> browser.getLink(id='edrn-rdf-literalpredicatehandler').click()
    >>> browser.getControl(name='form.widgets.title').value = u'icd9'
    >>> browser.getControl(name='form.widgets.description').value = u'Maps the <icd9> key to the an EDRN-specific URI.'
    >>> browser.getControl(name='form.widgets.predicateURI').value = u'urn:testing:predicates:icd9code'
    >>> browser.getControl(name='form.buttons.save').click()

Diseases affect organs, so here's the reference::

    >>> browser.open(portalURL + '/diseases')
    >>> l = browser.getLink(id='edrn-rdf-referencepredicatehandler')
    >>> l.url.endswith('++add++edrn.rdf.referencepredicatehandler')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'body_system'
    >>> browser.getControl(name='form.widgets.description').value = u'Maps to organs that diseases affect.'
    >>> browser.getControl(name='form.widgets.predicateURI').value = u'urn:testing:predicates:affectedOrgan'
    >>> browser.getControl(name='form.widgets.uriPrefix').value = u'urn:testing:data:organs:'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'body_system' in generator.keys()
    True
    >>> predicateHandler = generator['body_system']
    >>> predicateHandler.title
    u'body_system'
    >>> predicateHandler.description
    u'Maps to organs that diseases affect.'
    >>> predicateHandler.predicateURI
    u'urn:testing:predicates:affectedOrgan'
    >>> predicateHandler.uriPrefix
    u'urn:testing:data:organs:'

The Simple DMCC RDF Generator for diseases is now ready.  We'll set it up as
the generator for our simple source::

    >>> browser.open(portalURL + '/a-simple-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': '/plone/diseases',
    ...     'form.widgets.approvedFile:list': source.approvedFile.to_path if source.approvedFile else '',
    ...     'form.widgets.active:list': 'selected',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> browser.post(portalURL + '/a-simple-source/@@edit', urlencode(postParams))
    >>> source.generator.to_object.title
    u'Diseases'

Tickling::

    >>> browser.open(portalURL + '/@@updateRDF')

And now::

    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    124
    >>> namespaceURIs = [i[1] for i in graph.namespaces()]
    >>> namespaceURIs.sort()
    >>> namespaceURIs[0]
    rdflib.term.URIRef(u'http://purl.org/dc/terms/')
    >>> namespaceURIs[-1]
    rdflib.term.URIRef(u'urn:testing:predicates:')
    >>> subjects = frozenset([unicode(i) for i in graph.subjects() if unicode(i)])
    >>> subjects = list(subjects)
    >>> subjects.sort()
    >>> subjects[0:3]
    [u'urn:testing:data:disease:1', u'urn:testing:data:disease:10', u'urn:testing:data:disease:11']
    >>> predicates = frozenset([unicode(i) for i in graph.predicates()])
    >>> predicates = list(predicates)
    >>> predicates.sort()
    >>> predicates[0]
    u'http://purl.org/dc/terms/title'
    >>> predicates[2]
    u'urn:testing:predicates:affectedOrgan'
    >>> predicates[3]
    u'urn:testing:predicates:icd9code'
    >>> objects = [unicode(i) for i in graph.objects() if isinstance(i, rdflib.term.Literal)]
    >>> objects.sort()
    >>> objects[27:32]
    [u'205', u'208.9', u'Liver cell carcinoma', u'Lymphoid leukaemia', u'Malignant melanoma of skin']
    >>> references = frozenset([unicode(i) for i in graph.objects() if isinstance(i, rdflib.term.URIRef)])
    >>> references = list(references)
    >>> references.sort()
    >>> references[0:3]
    [u'urn:testing:data:organs:1', u'urn:testing:data:organs:10', u'urn:testing:data:organs:11']

That's even better lookin' RDF.


Multiple Literal Values
~~~~~~~~~~~~~~~~~~~~~~~

Some of the information in the DMCC's web service contains literal values that
are separated by commas.  For example, the ``Publication`` operation yields a
sequence of comma-separated author names.  In RDF, we don't use such in-band
signaling, since that's moronic.  Instead, we make multiple statements about a
publication, each one describing a separate author.

We've got a class to handle just that case: the Multi-Literal Predicate
Handler.

Let's try it out.  First, let's make a brand new Simple DMCC RDF Generator for
publications:

    >>> browser.open(portalURL)
    >>> browser.getLink(id='edrn-rdf-simpledmccrdfgenerator').click()
    >>> browser.getControl(name='form.widgets.title').value = u'Publications'
    >>> browser.getControl(name='form.widgets.description').value = u'Generates lists of journal articles and stuff.'
    >>> browser.getControl(name='form.widgets.webServiceURL').value = u'testscheme://localhost/ws_newcompass.asmx?WSDL'
    >>> browser.getControl(name='form.widgets.operationName').value = u'Publication'
    >>> browser.getControl(name='form.widgets.verificationNum').value = u'0'
    >>> browser.getControl(name='form.widgets.uriPrefix').value = u'urn:testing:data:publication:'
    >>> browser.getControl(name='form.widgets.identifyingKey').value = u'Identifier'
    >>> browser.getControl(name='form.widgets.typeURI').value = u'urn:testing:types:publication'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> generator = portal['publications']

Now a Literal Predicate Handler to handle the title of each publication::

    >>> browser.open(portalURL + '/publications')
    >>> browser.getLink(id='edrn-rdf-literalpredicatehandler').click()
    >>> browser.getControl(name='form.widgets.title').value = u'item_Title'
    >>> browser.getControl(name='form.widgets.description').value = u'Maps the <item_Title> key to the Dublin Core title predicate URI.'
    >>> browser.getControl(name='form.widgets.predicateURI').value = u'http://purl.org/dc/terms/title'
    >>> browser.getControl(name='form.buttons.save').click()

And a Multi-Literal Predicate Handler for the authors::

    >>> browser.open(portalURL + '/publications')
    >>> l = browser.getLink(id='edrn-rdf-multiliteralpredicatehandler')
    >>> l.url.endswith('++add++edrn.rdf.multiliteralpredicatehandler')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Author'
    >>> browser.getControl(name='form.widgets.description').value = u'Maps to authors of publications.'
    >>> browser.getControl(name='form.widgets.predicateURI').value = u'http://purl.org/dc/terms/creator'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'author' in generator.keys()
    True
    >>> predicateHandler = generator['author']
    >>> predicateHandler.title
    u'Author'
    >>> predicateHandler.description
    u'Maps to authors of publications.'
    >>> predicateHandler.predicateURI
    u'http://purl.org/dc/terms/creator'

Does it work?  Let's make the simple source use it to find out::

    >>> browser.open(portalURL + '/a-simple-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': '/plone/publications',
    ...     'form.widgets.approvedFile:list': source.approvedFile.to_path if source.approvedFile else '',
    ...     'form.widgets.active:list': 'selected',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> browser.post(portalURL + '/a-simple-source/@@edit', urlencode(postParams))
    >>> source.generator.to_object.title
    u'Publications'

Tickling::

    >>> browser.open(portalURL + '/@@updateRDF')

And now for the RDF::

    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    1908
    >>> subjects = frozenset([unicode(i) for i in graph.subjects() if unicode(i)])
    >>> subjects = list(subjects)
    >>> subjects.sort()
    >>> subjects[0:3]
    [u'urn:testing:data:publication:128', u'urn:testing:data:publication:129', u'urn:testing:data:publication:130']
    >>> predicates = frozenset([unicode(i) for i in graph.predicates()])
    >>> predicates = list(predicates)
    >>> predicates.sort()
    >>> predicates[0]
    u'http://purl.org/dc/terms/creator'
    >>> objects = [unicode(i) for i in graph.objects() if isinstance(i, rdflib.term.Literal)]
    >>> objects.sort()
    >>> objects[20:23]
    [u'Aberrant promoter methylation and silencing of the RASSF1A gene in pediatric tumors and cell lines', u'Aberrant promoter methylation profile of bladder cancer and its relationship to clinicopathologic features', u'Aberrant promoter methylation profile of bladder cancer and its relationship to clinicopathological features']

Yes, fine—and I mean *fiiiiiine*—RDF.


Approved RDF Files in RDF Sources
=================================

While we're here, notice this: our "Simple Source" first produced an empty
graph, thanks to the Null RDF Generator, then it produced non-empty graphs,
thanks to the Simple DMCC RDF Generator.  However, the previous, empty RDF is
still there, as are each of the other files for organs, diseases, and our
latest one, publications.  We can change the approved RDF at any time from the
latest generated file to any other generated file.

The RDF Source is a container object that holds all of the RDF files generated
for it::

    >>> files = list(source.keys())
    >>> len(files)
    4
    >>> latest = source.approvedFile.to_object.id
    >>> files.remove(latest)
    >>> earliest = files[0]

You can point the source to an older file::

    >>> browser.open(portalURL + '/a-simple-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': source.generator.to_path if source.generator else '',
    ...     'form.widgets.approvedFile:list': '/plone/a-simple-source/' + earliest,
    ...     'form.widgets.active:list': 'selected',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> browser.post(portalURL + '/a-simple-source/@@edit', urlencode(postParams))
    >>> source.approvedFile.to_object.id == earliest
    True
    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    0

Using this, you can go back to an earlier RDF file in case a later one
contains bad data.  Note, though, that the next time the source's generator
gets run, it'll make an active file again::

    >>> browser.open(portalURL + '/@@updateRDF')
    >>> browser.open(portalURL + '/a-simple-source/@@rdf')
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    1908

To prevent that from happening, uncheck the source's "Active" checkbox.


Advanced RDF Generators
=======================

The Simple DMCC RDF Generator handles simple statements with literal objects
as well as referential statements with reference objects.  With this, we can
provide RDF for a number of the DMCC's sources of EDRN information, including:

• Body systems
• Diseases
• Sites
• Publications
• Registered Persons

More tricky are EDRN's committees and protocols.  They're so tricky, in fact,
that they have dedicated RDF generators:

• DMCC Committee RDF Generator
• DMCC Protocols RDF Generator

Let's dive right in.


Generating RDF for Committees
-----------------------------

Committees require input from multiple SOAP API calls into the DMCC's ungainly
web service.  They may be created anywhere::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='edrn-rdf-dmcccommitteerdfgenerator')
    >>> l.url.endswith('++add++edrn.rdf.dmcccommitteerdfgenerator')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Committees'
    >>> browser.getControl(name='form.widgets.description').value = u'Generates info about EDRN committees.'
    >>> browser.getControl(name='form.widgets.webServiceURL').value = u'testscheme://localhost/ws_newcompass.asmx?WSDL'
    >>> browser.getControl(name='form.widgets.committeeOperation').value = u'Committees'
    >>> browser.getControl(name='form.widgets.membershipOperation').value = u'Committee_Membership'
    >>> browser.getControl(name='form.widgets.verificationNum').value = u'0'
    >>> browser.getControl(name='form.widgets.typeURI').value = u'urn:testing:types:committee'
    >>> browser.getControl(name='form.widgets.uriPrefix').value = u'urn:testing:data:committee:'
    >>> browser.getControl(name='form.widgets.personPrefix').value = u'urn:testing:data:person:'
    >>> browser.getControl(name='form.widgets.titlePredicateURI').value = u'http://purl.org/dc/terms/title'
    >>> browser.getControl(name='form.widgets.abbrevNamePredicateURI').value = u'urn:testing:predicates:abbrevName'
    >>> browser.getControl(name='form.widgets.committeeTypePredicateURI').value = u'urn:testing:predicates:committeeType'
    >>> browser.getControl(name='form.widgets.chairPredicateURI').value = u'urn:testing:predicates:chair'
    >>> browser.getControl(name='form.widgets.coChairPredicateURI').value = u'urn:testing:predicates:coChair'
    >>> browser.getControl(name='form.widgets.consultantPredicateURI').value = u'urn:testing:predicates:consultant'
    >>> browser.getControl(name='form.widgets.memberPredicateURI').value = u'urn:testing:predicates:member'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'committees' in portal.keys()
    True
    >>> generator = portal['committees']
    >>> generator.title
    u'Committees'
    >>> generator.description
    u'Generates info about EDRN committees.'
    >>> generator.webServiceURL
    u'testscheme://localhost/ws_newcompass.asmx?WSDL'
    >>> generator.committeeOperation
    u'Committees'
    >>> generator.membershipOperation
    u'Committee_Membership'
    >>> generator.verificationNum
    u'0'
    >>> generator.typeURI
    u'urn:testing:types:committee'
    >>> generator.uriPrefix
    u'urn:testing:data:committee:'
    >>> generator.personPrefix
    u'urn:testing:data:person:'
    >>> generator.titlePredicateURI
    u'http://purl.org/dc/terms/title'
    >>> generator.abbrevNamePredicateURI
    u'urn:testing:predicates:abbrevName'
    >>> generator.committeeTypePredicateURI
    u'urn:testing:predicates:committeeType'
    >>> generator.chairPredicateURI
    u'urn:testing:predicates:chair'
    >>> generator.coChairPredicateURI
    u'urn:testing:predicates:coChair'
    >>> generator.consultantPredicateURI
    u'urn:testing:predicates:consultant'
    >>> generator.memberPredicateURI
    u'urn:testing:predicates:member'

Looks good.  Now, we could make this generator be the source for our simple
source that we've been using so far, but frankly, we've been riding the simple
source pretty hard for a while now.  Let's give it a rest and come up with a
fresh source, just for the committees generator::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='edrn-rdf-rdfsource').click()
    >>> browser.getControl(name='form.widgets.title').value = u'A Committee Source'
    >>> browser.getControl(name='form.widgets.description').value = u"It's just for functional tests."
    >>> browser.getControl(name='form.widgets.active:list').value = True
    >>> browser.getControl(name='form.buttons.save').click()
    >>> source = portal['a-committee-source']
    >>> browser.open(portalURL + '/a-committee-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': '/plone/committees',
    ...     'form.widgets.active:list': 'selected',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> browser.post(portalURL + '/a-committee-source/@@edit', urlencode(postParams))

Now for the tickle::

    >>> browser.open(portalURL + '/@@updateRDF')

And now for the RDF::

    >>> browser.open(portalURL + '/a-committee-source/@@rdf')
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    247
    >>> subjects = frozenset([unicode(i) for i in graph.subjects() if unicode(i)])
    >>> subjects = list(subjects)
    >>> subjects.sort()
    >>> subjects[0:3]
    [u'urn:testing:data:committee:1', u'urn:testing:data:committee:10', u'urn:testing:data:committee:14']
    >>> predicates = frozenset([unicode(i) for i in graph.predicates()])
    >>> predicates = list(predicates)
    >>> predicates.sort()
    >>> predicates[0]
    u'http://purl.org/dc/terms/title'
    >>> predicates[2]
    u'urn:testing:predicates:abbrevName'
    >>> predicates[3]
    u'urn:testing:predicates:chair'
    >>> predicates[4]
    u'urn:testing:predicates:coChair'
    >>> predicates[5]
    u'urn:testing:predicates:committeeType'
    >>> predicates[6]
    u'urn:testing:predicates:consultant'
    >>> predicates[7]
    u'urn:testing:predicates:member'
    >>> objects = [unicode(i) for i in graph.objects() if isinstance(i, rdflib.term.Literal)]
    >>> objects.sort()
    >>> objects[0:6]
    [u'Assoc. Member', u'Associate Member', u'BDL', u'BRL', u'Biomarker Developmental  Laboratories', u'Biomarker Reference Laboratories']

Major wootness.


Generating RDF for Protocols
----------------------------

Protocols are quite a bit tricky.  Generators for them may be created
anywhere::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='edrn-rdf-dmccprotocolrdfgenerator')
    >>> l.url.endswith('++add++edrn.rdf.dmccprotocolrdfgenerator')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Protocols'
    >>> browser.getControl(name='form.widgets.description').value = u'Generates info about EDRN protocols.'
    >>> browser.getControl(name='form.widgets.webServiceURL').value = u'testscheme://localhost/ws_newcompass.asmx?WSDL'
    >>> browser.getControl(name='form.widgets.protocolOrStudyOperation').value = u'Protocol_or_Study'
    >>> browser.getControl(name='form.widgets.edrnProtocolOperation').value = u'EDRN_Protocol'
    >>> browser.getControl(name='form.widgets.protoSiteSpecificsOperation').value = u'Protocol_Site_Specifics'
    >>> browser.getControl(name='form.widgets.protoProtoRelationshipOperation').value = u'Protocol_Protocol_Relationship'
    >>> browser.getControl(name='form.widgets.verificationNum').value = u'0'
    >>> browser.getControl(name='form.widgets.typeURI').value = u'urn:testing:types:protocol'
    >>> browser.getControl(name='form.widgets.siteSpecificTypeURI').value = u'urn:testing:types:protocol:sitespecific'
    >>> browser.getControl(name='form.widgets.uriPrefix').value = u'urn:testing:data:protocol:'
    >>> browser.getControl(name='form.widgets.siteSpecURIPrefix').value = u'urn:testing:data:protocol:site-spec:'
    >>> browser.getControl(name='form.widgets.publicationURIPrefix').value = u'urn:testing:data:publication:'
    >>> browser.getControl(name='form.widgets.siteURIPrefix').value = u'urn:testing:data:sites:'
    >>> browser.getControl(name='form.widgets.titleURI').value = u'urn:testing:predicates:titleURI'
    >>> browser.getControl(name='form.widgets.abstractURI').value = u'urn:testing:predicates:abstractURI'
    >>> browser.getControl(name='form.widgets.involvedInvestigatorSiteURI').value = u'urn:testing:predicates:involvedInvestigatorSiteURI'
    >>> browser.getControl(name='form.widgets.bmNameURI').value = u'urn:testing:predicates:bmNameURI'
    >>> browser.getControl(name='form.widgets.coordinateInvestigatorSiteURI').value = u'urn:testing:predicates:coordinateInvestigatorSiteURI'
    >>> browser.getControl(name='form.widgets.leadInvestigatorSiteURI').value = u'urn:testing:predicates:leadInvestigatorSiteURI'
    >>> browser.getControl(name='form.widgets.collaborativeGroupTextURI').value = u'urn:testing:predicates:collaborativeGroupTextURI'
    >>> browser.getControl(name='form.widgets.phasedStatusURI').value = u'urn:testing:predicates:phasedStatusURI'
    >>> browser.getControl(name='form.widgets.aimsURI').value = u'urn:testing:predicates:aimsURI'
    >>> browser.getControl(name='form.widgets.analyticMethodURI').value = u'urn:testing:predicates:analyticMethodURI'
    >>> browser.getControl(name='form.widgets.blindingURI').value = u'urn:testing:predicates:blindingURI'
    >>> browser.getControl(name='form.widgets.cancerTypeURI').value = u'urn:testing:predicates:cancerTypeURI'
    >>> browser.getControl(name='form.widgets.commentsURI').value = u'urn:testing:predicates:commentsURI'
    >>> browser.getControl(name='form.widgets.dataSharingPlanURI').value = u'urn:testing:predicates:dataSharingPlanURI'
    >>> browser.getControl(name='form.widgets.inSituDataSharingPlanURI').value = u'urn:testing:predicates:inSituDataSharingPlanURI'
    >>> browser.getControl(name='form.widgets.finishDateURI').value = u'urn:testing:predicates:finishDateURI'
    >>> browser.getControl(name='form.widgets.estimatedFinishDateURI').value = u'urn:testing:predicates:estimatedFinishDateURI'
    >>> browser.getControl(name='form.widgets.startDateURI').value = u'urn:testing:predicates:startDateURI'
    >>> browser.getControl(name='form.widgets.designURI').value = u'urn:testing:predicates:designURI'
    >>> browser.getControl(name='form.widgets.fieldOfResearchURI').value = u'urn:testing:predicates:fieldOfResearchURI'
    >>> browser.getControl(name='form.widgets.abbreviatedNameURI').value = u'urn:testing:predicates:abbreviatedNameURI'
    >>> browser.getControl(name='form.widgets.objectiveURI').value = u'urn:testing:predicates:objectiveURI'
    >>> browser.getControl(name='form.widgets.projectFlagURI').value = u'urn:testing:predicates:projectFlagURI'
    >>> browser.getControl(name='form.widgets.protocolTypeURI').value = u'urn:testing:predicates:protocolTypeURI'
    >>> browser.getControl(name='form.widgets.publicationsURI').value = u'urn:testing:predicates:publicationsURI'
    >>> browser.getControl(name='form.widgets.outcomeURI').value = u'urn:testing:predicates:outcomeURI'
    >>> browser.getControl(name='form.widgets.secureOutcomeURI').value = u'urn:testing:predicates:secureOutcomeURI'
    >>> browser.getControl(name='form.widgets.finalSampleSizeURI').value = u'urn:testing:predicates:finalSampleSizeURI'
    >>> browser.getControl(name='form.widgets.plannedSampleSizeURI').value = u'urn:testing:predicates:plannedSampleSizeURI'
    >>> browser.getControl(name='form.widgets.isAPilotForURI').value = u'urn:testing:predicates:isAPilotForURI'
    >>> browser.getControl(name='form.widgets.obtainsDataFromURI').value = u'urn:testing:predicates:obtainsDataFromURI'
    >>> browser.getControl(name='form.widgets.providesDataToURI').value = u'urn:testing:predicates:providesDataToURI'
    >>> browser.getControl(name='form.widgets.contributesSpecimensURI').value = u'urn:testing:predicates:contributesSpecimensURI'
    >>> browser.getControl(name='form.widgets.obtainsSpecimensFromURI').value = u'urn:testing:predicates:obtainsSpecimensFromURI'
    >>> browser.getControl(name='form.widgets.hasOtherRelationshipURI').value = u'urn:testing:predicates:hasOtherRelationshipURI'
    >>> browser.getControl(name='form.widgets.animalSubjectTrainingReceivedURI').value = u'urn:testing:predicates:animalSubjectTrainingReceivedURI'
    >>> browser.getControl(name='form.widgets.humanSubjectTrainingReceivedURI').value = u'urn:testing:predicates:humanSubjectTrainingReceivedURI'
    >>> browser.getControl(name='form.widgets.irbApprovalNeededURI').value = u'urn:testing:predicates:irbApprovalNeededURI'
    >>> browser.getControl(name='form.widgets.currentIRBApprovalDateURI').value = u'urn:testing:predicates:currentIRBApprovalDateURI'
    >>> browser.getControl(name='form.widgets.originalIRBApprovalDateURI').value = u'urn:testing:predicates:originalIRBApprovalDateURI'
    >>> browser.getControl(name='form.widgets.irbExpirationDateURI').value = u'urn:testing:predicates:irbExpirationDateURI'
    >>> browser.getControl(name='form.widgets.generalIRBNotesURI').value = u'urn:testing:predicates:generalIRBNotesURI'
    >>> browser.getControl(name='form.widgets.irbNumberURI').value = u'urn:testing:predicates:irbNumberURI'
    >>> browser.getControl(name='form.widgets.siteRoleURI').value = u'urn:testing:predicates:siteRoleURI'
    >>> browser.getControl(name='form.widgets.reportingStageURI').value = u'urn:testing:predicates:reportingStageURI'
    >>> browser.getControl(name='form.widgets.eligibilityCriteriaURI').value = u'urn:testing:predicates:eligibilityCriteriaURI'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'protocols' in portal.keys()
    True
    >>> generator = portal['protocols']

We won't bother confirming that every field got its correct value;
plone.app.dexterity had better damn well take care of that for us.  Instead,
let's make a source to hold graphs generated by this protocol generator::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='edrn-rdf-rdfsource').click()
    >>> browser.getControl(name='form.widgets.title').value = u'A Protocol Source'
    >>> browser.getControl(name='form.widgets.description').value = u"It's just for functional tests."
    >>> browser.getControl(name='form.widgets.active:list').value = True
    >>> browser.getControl(name='form.buttons.save').click()
    >>> source = portal['a-protocol-source']
    >>> browser.open(portalURL + '/a-protocol-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': '/plone/protocols',
    ...     'form.widgets.active:list': 'selected',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> browser.post(portalURL + '/a-protocol-source/@@edit', urlencode(postParams))

Once again, tickling::

    >>> browser.open(portalURL + '/@@updateRDF')

And now for the RDF::

    >>> browser.open(portalURL + '/a-protocol-source/@@rdf')
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    2518
    >>> subjects = frozenset([unicode(i) for i in graph.subjects() if unicode(i)])
    >>> subjects = list(subjects)
    >>> subjects.sort()
    >>> subjects[0]
    u'urn:testing:data:protocol:100'
    >>> predicates = frozenset([unicode(i) for i in graph.predicates()])
    >>> predicates = list(predicates)
    >>> predicates.sort()
    >>> predicates[1]
    u'urn:testing:predicates:abbreviatedNameURI'
    >>> objects = [unicode(i) for i in graph.objects() if isinstance(i, rdflib.term.Literal)]
    >>> objects.sort()
    >>> objects[-1]
    u'xyz'

CA-1031 complains that the rdf:resource links for a protocol to its sites and
its publications are bad, consisting of a URI prefix but with no final numeric
identifier.  Really?  Let's check::

    >>> with open('/tmp/log.html', 'w') as xxx: xxx.write(browser.contents)
    >>> results = graph.query('''select ?publicationsURI where {
    ...    <urn:testing:data:protocol:155> <urn:testing:predicates:publicationsURI> ?publicationsURI .
    ... }''')
    >>> len(results)
    3
    >>> ids = [unicode(i[0]) for i in results.result]
    >>> ids.sort()
    >>> ids
    [u'urn:testing:data:publication:184', u'urn:testing:data:publication:265', u'urn:testing:data:publication:332'] 
    
That looks good for publications.  And sites::

    >>> results = graph.query('''select ?leadInvestigatorSiteURI where {
    ...    <urn:testing:data:protocol:342> <urn:testing:predicates:leadInvestigatorSiteURI> ?leadInvestigatorSiteURI .
    ... }''')
    >>> len(results)
    1
    >>> results.result[0][0]
    rdflib.term.URIRef(u'urn:testing:data:sites:244')

OK, great!  But let's make sure the publications don't appear at all when an
protocol doesn't have any::

    >>> results = graph.query('''select ?publicationsURI where {
    ...    <urn:testing:data:protocol:342> <urn:testing:predicates:publicationsURI> ?publicationsURI .
    ... }''')
    >>> len(results)
    0

Fan-freakin'-tastic.


RDF Generators added by David
=============================

Generating RDF for Biomuta
-----------------------------

Biomuta generator grabs csv file from George Washington University's 
High-performance Integrated Virtual Environment (HIVE).  They may be created anywhere::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='edrn-rdf-biomutardfgenerator')
    >>> l.url.endswith('++add++edrn.rdf.biomutardfgenerator')
    True
    >>> l.click()
    >>> browser.getControl(name='form.widgets.title').value = u'Biomuta'
    >>> browser.getControl(name='form.widgets.description').value = u'Generates mutation info about EDRN biomarkers.'
    >>> browser.getControl(name='form.widgets.webServiceURL').value = u'testscheme://localhost/biomuta.tsv'
    >>> browser.getControl(name='form.widgets.typeURI').value = u'urn:testing:types:biomuta'
    >>> browser.getControl(name='form.widgets.uriPrefix').value = u'urn:testing:data:biomuta:'
    >>> browser.getControl(name='form.widgets.geneNamePredicateURI').value = u'urn:testing:predicates:geneName'
    >>> browser.getControl(name='form.widgets.uniProtACPredicateURI').value = u'urn:testing:predicates:uniprotAccession'
    >>> browser.getControl(name='form.widgets.mutCountPredicateURI').value = u'urn:testing:predicates:mutationCount'
    >>> browser.getControl(name='form.widgets.pmidCountPredicateURI').value = u'urn:testing:predicates:pubmedIDCount'
    >>> browser.getControl(name='form.widgets.cancerDOCountPredicateURI').value = u'urn:testing:predicates:cancerDOCount'
    >>> browser.getControl(name='form.widgets.affProtFuncSiteCountPredicateURI').value = u'urn:testing:predicates:affectedProtFuncSiteCount'
    >>> browser.getControl(name='form.buttons.save').click()
    >>> 'biomuta' in portal.keys()
    True
    >>> generator = portal['biomuta']
    >>> generator.title
    u'Biomuta'
    >>> generator.description
    u'Generates mutation info about EDRN biomarkers.'
    >>> generator.webServiceURL
    u'testscheme://localhost/biomuta.tsv'
    >>> generator.typeURI
    u'urn:testing:types:biomuta'
    >>> generator.uriPrefix
    u'urn:testing:data:biomuta:'
    >>> generator.geneNamePredicateURI
    u'urn:testing:predicates:geneName'
    >>> generator.uniProtACPredicateURI
    u'urn:testing:predicates:uniprotAccession'
    >>> generator.mutCountPredicateURI
    u'urn:testing:predicates:mutationCount'
    >>> generator.pmidCountPredicateURI
    u'urn:testing:predicates:pubmedIDCount'
    >>> generator.cancerDOCountPredicateURI
    u'urn:testing:predicates:cancerDOCount'
    >>> generator.affProtFuncSiteCountPredicateURI
    u'urn:testing:predicates:affectedProtFuncSiteCount'

Looks good.  Fresh source for the biomuta generator::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='edrn-rdf-rdfsource').click()
    >>> browser.getControl(name='form.widgets.title').value = u'A Biomuta Source'
    >>> browser.getControl(name='form.widgets.description').value = u"It's just for functional tests."
    >>> browser.getControl(name='form.widgets.active:list').value = True
    >>> browser.getControl(name='form.buttons.save').click()
    >>> source = portal['a-biomuta-source']
    >>> browser.open(portalURL + '/a-biomuta-source/edit')
    >>> postParams = {
    ...     'form.widgets.title': source.title,
    ...     'form.widgets.description': source.description,
    ...     'form.widgets.generator:list': '/plone/biomuta',
    ...     'form.widgets.active:list': 'selected',
    ...     'form.buttons.save': 'Save',
    ... }
    >>> browser.post(portalURL + '/a-biomuta-source/@@edit', urlencode(postParams))

Now for the tickle::

    >>> browser.open(portalURL + '/@@updateRDF')

And now for the RDF::

    >>> browser.open(portalURL + '/a-biomuta-source/@@rdf')
    >>> graph = rdflib.Graph()
    >>> graph.parse(data=browser.contents)
    <Graph identifier=...(<class 'rdflib.graph.Graph'>)>
    >>> len(graph)
    266
    >>> subjects = frozenset([unicode(i) for i in graph.subjects() if unicode(i)])
    >>> subjects = list(subjects)
    >>> subjects.sort()
    >>> subjects[0:3]
    [u'urn:testing:data:biomuta:ANO9', u'urn:testing:data:biomuta:ARHGAP10', u'urn:testing:data:biomuta:ARHGEF37']
    >>> predicates = frozenset([unicode(i) for i in graph.predicates()])
    >>> predicates = list(predicates)
    >>> predicates.sort()
    >>> predicates[1]
    u'urn:testing:predicates:affectedProtFuncSiteCount'
    >>> predicates[2]
    u'urn:testing:predicates:cancerDOCount'
    >>> predicates[3]
    u'urn:testing:predicates:geneName'
    >>> predicates[4]
    u'urn:testing:predicates:mutationCount'
    >>> predicates[5]
    u'urn:testing:predicates:pubmedIDCount'
    >>> predicates[6]
    u'urn:testing:predicates:uniprotAccession'
    >>> objects = [unicode(i) for i in graph.objects() if isinstance(i, rdflib.term.Literal)]
    >>> objects.sort()
    >>> objects[0:6]
    [u'0', u'0', u'0', u'0', u'0', u'0']

Woot Woot.
