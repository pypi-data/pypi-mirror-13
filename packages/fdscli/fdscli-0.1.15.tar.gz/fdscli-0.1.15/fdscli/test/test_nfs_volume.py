from test.base_cli_test import BaseCliTest
from utils.converters.volume.settings_converter import SettingsConverter
import mock_functions
from mock import patch
from model.volume.settings.nfs_settings import NfsSettings
from utils.fds_cli_configuration_manager import FdsCliConfigurationManager

class TestNfsVolume( BaseCliTest ):
    '''
    Created on Nov 9, 2015
    
    @author: nate
    '''

    def test_marshalling(self):
        
        settings = NfsSettings()
        
        settings.use_acls = True
        settings.use_root_squash = False
        settings.synchronous = True
        
        settings.clients ="localhost*::[0-3]"
        
        j_str = SettingsConverter.to_json(settings)
        
        print( j_str )
        
        m_settings = SettingsConverter.build_settings_from_json( j_str )
        
        assert m_settings.type == "NFS"
        assert m_settings.clients == "localhost*::[0-3]"
        assert settings.use_acls is True
        assert settings.use_root_squash is False
        assert settings.synchronous is True
        
        
    @patch( "services.volume_service.VolumeService.list_volumes", side_effect=mock_functions.listVolumes )
    @patch( "services.volume_service.VolumeService.create_volume", side_effect=mock_functions.createVolume )        
    def test_iscsi_creation(self, volumeCreate, listVolumes ):
        '''
        This test will make sure the settings look right after a volume create call
        '''
        config = FdsCliConfigurationManager()
        
        self.cli.loadmodules()
        
        args = ['volume', 'create', '-name', 'nfs', '-type', 'nfs', '-acls', 'true', '-root_squash', 'false', 
                '-clients', '128.*2*.[6-9]::ab']
         
        self.callMessageFormatter(args)
        self.cli.run(args)
         
        volume = volumeCreate.call_args[0][0]
        settings = volume.settings
     
        assert settings.type == 'NFS'
        assert settings.clients == "128.*2*.[6-9]::ab"
        assert settings.use_acls is True
        assert settings.use_root_squash is False
        assert settings.synchronous is False
        
        