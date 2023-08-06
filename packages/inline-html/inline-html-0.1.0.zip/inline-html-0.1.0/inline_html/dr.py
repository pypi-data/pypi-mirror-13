import docraptor

docraptor.configuration.username = "YOUR_API_KEY_HERE" # this key works for test documents
docraptor.configuration.debug = True

doc_api = docraptor.DocApi()

html = open('out.html', 'rb').read()

response = doc_api.create_doc({
  "test": True,                                                   # test documents are free but watermarked
  "document_content": html,
  # "document_url": "http://docraptor.com/examples/invoice.html", # or use a url
  "name": "docraptor-python.pdf",                                 # help you find a document later
  "document_type": "pdf",                                         # pdf or xls or xlsx
  # "javascript": True,                                           # enable JavaScript processing
  # "prince_options": {
  #   "media": "screen",                                          # use screen styles instead of print styles
  #   "baseurl": "http://hello.com",                              # pretend URL when using document_content
  # },
})

open('out.pdf', 'wb').write(response)
