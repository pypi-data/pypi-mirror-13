Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Description: # MediaWiki API
        
        This MIT Licensed library provides a very simple convenience wrapper 
        around the [MediaWiki API](http://www.mediawiki.org/wiki/API). and 
        includes support for authenticated sessions. It requires Python 3
        and that your wiki is using MediaWiki 1.15.3 or greater.
        
        * **Installation:** ``pip install mwapi``
        * **Documentation:** https://pythonhosted.org/mwapi
        * **Repositiory:** https://github.com/mediawiki-utilities/python-mwapi
        * **License:** MIT
        
        ## Example
        
            >>> import mwapi
            >>>
            >>> session = mwapi.Session('https://en.wikipedia.org')
            >>>
            >>> print(session.get(action='query', meta='userinfo'))
            {'query': {'userinfo': {'anon': '', 'name': '75.72.203.28', 'id': 0}},
             'batchcomplete': ''}
            >>>
            >>> print(session.get(action='query', prop='revisions', revids=32423425))
            {'query': {'pages': {'1429626': {'ns': 0, 'revisions': [{'user':
             'Wknight94', 'parentid': 32276615, 'comment':
             '/* References */ Removing less-specific cat', 'revid': 32423425,
             'timestamp': '2005-12-23T00:07:17Z'}], 'title': 'Grigol Ordzhonikidze',
             'pageid': 1429626}}}, 'batchcomplete': ''}
        
        
        ## Authors
        * YuviPanda -- https://github.com/yuvipanda
        * Aaron Halfaker -- https://github.com/halfak
        
Platform: UNKNOWN
