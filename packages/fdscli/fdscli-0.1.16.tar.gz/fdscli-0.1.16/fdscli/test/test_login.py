'''
Created on Jan 21, 2016

@author: nate
'''
from unittest.case import TestCase
from services.fds_auth import FdsAuth
from mock import patch
from FDSShell import FDSShell

def failedLogin():
    raise Exception( "AAAAAHHHH!" )

class testLogin( TestCase ):
    '''
    Test the login functionality
    '''
    
    @patch( "services.fds_auth.FdsAuth.login", side_effect=failedLogin )
    def test_fail_odd_exception( self, mockLogin ):
        '''
        Test that login works and accepts a command
        '''
        auth = FdsAuth()
        
        cli = FDSShell( auth )
        
        args = ["volume", "list"]
        
        rtn = cli.run( args )
        
        assert rtn == 1, "Expected a non-zero return like 1 but got {}".format( rtn )