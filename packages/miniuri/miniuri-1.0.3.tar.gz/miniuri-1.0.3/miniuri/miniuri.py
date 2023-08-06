class Uri( object ):
    """
    miniuri is a universal URI parser class.
    The parser grants access to the following attributes:

    foo://username:password@test.com:808/go/to/index.php?pet=cat&name=bam#eye
    \_/   \_______________/ \______/ \_/       \___/ \_/ \_______________/\_/
     |           |             |      |          |    |       |            | 
     |       userinfo       hostname  |          |    |      query   fragment
     |    \___________________________|/\________|____|_/
     |                  |             |      |   |    |
    scheme          authority         |    path  |  extension
                                      |          |
                                     port     filename
    """
    def __init__( self, uri = None ):
        if uri: self.uri = uri # invoke uri.setter

    def __str__(self): return self.uri

    @property
    def uri( self ):
        """build and return uri from attributes"""
        scheme = self.scheme + '://' if self.scheme else ''
        return ''.join([scheme, self.authority, self.not_authority])

    @uri.setter
    def uri( self, uri ):
        """parse and set all uri attributes"""
        self.scheme = self.username = self.password = None
        self.hostname = self.port = self.path = None
        self.filename = self.query = self.fragment = None 

        if '://' in uri:
            self.scheme, uri = uri.split( '://' )

        if '#' in uri:
            uri, self.fragment = uri.split('#')

        if '?' in uri:
            uri, self.query = uri.split('?')

        # invoke authority setter.
        self.authority = uri.split( '/' )[0]

        # invoke path setter.
        self.path = uri[ len( self.authority ): ]
        
    @property
    def authority( self ):
        """return a authority string from attributes"""
        a = ''
        if self.username:
            a += self.username
            if self.password: a += ':' + self.password
            a += '@'
        a += self.hostname
        if self.port: a += ':' + self.port
        return a

    @authority.setter
    def authority( self, a ):
        """set all the attribute that makeup a authority"""
        self.username = self.password = self.port = None
        self.hostname = a
        if '@' in self.hostname:
            self.userinfo, self.hostname = a.split( '@' ) # userinfo setter
        if ':' in self.hostname:
            self.hostname, self.port = self.hostname.split( ':' )

    @property
    def not_authority(self):
        """return everything that isn't part of the authority."""
        path = query = fragment = ''
        if self.path: path = self.path
        if self.query: query = '?' + self.query
        if self.fragment: fragment = '#' + self.fragment
        return ''.join([path, query, fragment])

    @property
    def userinfo( self ):
        """return username:password, username, or None"""
        if self.username:
            if self.password: 
                return self.username + ':' + self.password
            return self.username

    @userinfo.setter
    def userinfo( self, info ):
        """set username and password"""
        self.username, self.password = info, None 
        if ':' in info:
            self.username, self.password = info.split( ':' )

    @property
    def path(self):
        """return path"""
        p = self._path if self._path is not None else ''
        f = self.filename if self.filename is not None else ''
        return p + f

    @path.setter
    def path(self, new_path):
        if new_path:
            self.filename = new_path.split('/')[-1]
            self._path = new_path.rstrip(self.filename)
        else:
            self.filename = None
            self._path = None

    @property
    def filename(self):
        """return filename"""
        if self._filename: 
            if self.extension:
                return '{}.{}'.format(self._filename, self.extension)
            return self._filename
        return ''

    @filename.setter
    def filename(self, new_filename):
        self.extension = ''
        if new_filename:
            self._filename = new_filename.split('.')[0]
            if '.' in new_filename:
                self.extension = new_filename.split('.')[-1]
        else:
            self._filename = None
