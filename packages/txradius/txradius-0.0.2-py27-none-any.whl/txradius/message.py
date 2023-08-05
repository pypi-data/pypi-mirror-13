#!/usr/bin/env python
#coding=utf-8
from txradius.radius.packet import tools
from txradius.radius.packet import AuthPacket
from txradius.radius.packet import AcctPacket
from txradius.radius.packet import CoAPacket
from txradius.radius.packet import AccessRequest
from txradius.radius.packet import AccessAccept
from txradius.radius.packet import AccountingRequest
from txradius.radius.packet import AccountingResponse
from txradius.radius.packet import CoARequest
from txradius.mschap import mschap,mppe
import time
import binascii
import datetime
import hashlib
import six


md5_constructor = hashlib.md5

PacketStatusTypeMap = {
    1 : 'AccessRequest',
    2 : 'AccessAccept',
    3 : 'AccessReject',
    4 : 'AccountingRequest',
    5 : 'AccountingResponse',
    40 : 'DisconnectRequest',
    41 : 'DisconnectACK',
    42 : 'DisconnectNAK',
    43 : 'CoARequest',
    44 : 'CoAACK',
    45 : 'CoANAK',
}

def format_packet_str(pkt):
    attr_keys = pkt.keys()
    _str = "\nRadius Packet:%s"%PacketStatusTypeMap.get(pkt.code)
    _str += "\nid:%s" % pkt.id
    _str += "\ncode:%s" % pkt.code
    _str += "\nAttributes: "     
    for attr in attr_keys:
        try:
            _type = pkt.dict[attr].type
            if _type == 'octets':
                _str += "\n\t%s: %s " % (attr, ",".join([ binascii.hexlify(_a) for _a in pkt[attr] ]))   
            else:
                _str += "\n\t%s: %s " % (attr, ",".join(pkt[attr]))   
        except:
            try:_str += "\n\t%s: %s" % (attr, pkt[attr])
            except:pass
    return _str


def format_packet_log(pkt):
    attr_keys = pkt.keys()
    _str = "RadiusPacket:%s;" % PacketStatusTypeMap[pkt.code]
    _str += "host:(%s,%s);" % pkt.source
    _str += "id:%s;" % pkt.id
    _str += "code:%s;" % pkt.code
    for attr in attr_keys:
        try:
            _type = pkt.dict[attr].type
            if _type == 'octets':
                _str += "%s:%s;" % (attr, ",".join([binascii.hexlify(_a) for _a in pkt[attr]]))
            else:
                _str += "%s:%s;" % (attr, ",".join(pkt[attr]))
        except:
            try:
                _str += "%s:%s;" % (attr, pkt[attr])
            except:
                pass
    return _str



class CoAMessage(CoAPacket):
    def __init__(self, code=CoARequest, id=None, secret=six.b(''),
            authenticator=None, **attributes):
        CoAPacket.__init__(self, code, id, secret, authenticator, **attributes)
        
    def format_str(self):
        return format_packet_str(self)    

    def format_log(self):
        return format_packet_log(self)


class AuthMessage(AuthPacket):

    def __init__(self, code=AccessRequest, id=None, secret=six.b(''), authenticator=None, **attributes):
        AuthPacket.__init__(self, code, id, secret, authenticator, **attributes)

    def format_str(self):
        return format_packet_str(self)

    def format_log(self):
        return format_packet_log(self)

    def __str__(self):
        _str = PacketStatusTypeMap[self.code]
        _str += ",id=%s"%self.id
        if self.code == 1:
            _str += ",username=%s,mac_addr=%s" % (self.get_user_name(),self.get_mac_addr())
        if 'Reply-Message' in self:
            _str += ',Reply-Message="%s"' % self['Reply-Message'][0]
        return _str   

    def CreateReply(self, **attributes):
        return AuthMessage(AccessAccept, self.id,
            self.secret, self.authenticator, dict=self.dict,
            **attributes)
        
    def ChapEcrypt(self,password):
        if not self.authenticator:
            self.authenticator = self.CreateAuthenticator()
        if not self.id:
            self.id = self.CreateID()
        if isinstance(password, six.text_type):
            password = password.strip().encode('utf-8')

        chapid = self.authenticator[0]
        self['CHAP-Challenge'] = self.authenticator
        return '%s%s' % (chapid, md5_constructor("%s%s%s" % (chapid, password, self.authenticator)).digest())


    def set_reply_msg(self,msg):
        if msg:self.AddAttribute(18,msg)

    def set_framed_ip_addr(self,ipaddr):
        if ipaddr:self.AddAttribute(8,tools.EncodeAddress(ipaddr))

    def set_session_timeout(self,timeout):
        if timeout:self.AddAttribute(27,tools.EncodeInteger(timeout))
   
    def get_nas_addr(self):
        _nas_addr = None
        try:
            return tools.DecodeAddress(self.get(4)[0])
        except:pass
        
    def get_mac_addr(self):
        if self.client_macaddr:return self.client_macaddr
        try:return tools.DecodeString(self.get(31)[0]).replace("-",":")
        except:return None

    def get_user_name(self):
        try:
            user_name = tools.DecodeString(self.get(1)[0])
            if "@" in user_name:
                user_name = user_name[:user_name.index("@")]
            return user_name
        except:
            return None

    def get_domain(self):
        try:
            user_name = tools.DecodeString(self.get(1)[0])
            if "@" in user_name:
                return user_name[user_name.index("@")+1:]
        except:
            return None            
        
    def get_vlanids(self):
        return self.vlanid,self.vlanid2

    def get_passwd(self):
        try:return self.PwDecrypt(self.get(2)[0])
        except:return None        

    def get_chappwd(self):
        try:return tools.DecodeOctets(self.get(3)[0])
        except:return None  
        
    def verifyChapEcrypt(self,userpwd):
        if isinstance(userpwd, six.text_type):
            userpwd = userpwd.strip().encode('utf-8')   

        _password = self.get_chappwd()
        if len(_password) != 17:
            return False

        chapid = _password[0]
        password = _password[1:]

        if not self.authenticator:
            self.authenticator = self.CreateAuthenticator()

        challenge = self.authenticator
        if 'CHAP-Challenge' in self:
            challenge = self['CHAP-Challenge'][0] 

        _pwd =  md5_constructor("%s%s%s"%(chapid,userpwd,challenge)).digest()
        return password == _pwd
        

    def verifyMsChapV2(self,userpwd):
        ms_chap_response = self['MS-CHAP2-Response'][0]
        authenticator_challenge = self['MS-CHAP-Challenge'][0]
        if len(ms_chap_response)!=50:
            raise Exception("Invalid MSCHAPV2-Response attribute length")
        # if isinstance(userpwd, six.text_type):
        #     userpwd = userpwd.strip().encode('utf-8')
        
        nt_response = ms_chap_response[26:50]
        peer_challenge = ms_chap_response[2:18]
        _user_name = self.get(1)[0]
        nt_resp = mschap.generate_nt_response_mschap2(
            authenticator_challenge,
            peer_challenge,
            _user_name,
            userpwd,
        )
        if nt_resp == nt_response:
            auth_resp = mschap.generate_authenticator_response(
                userpwd,
                nt_response,
                peer_challenge,
                authenticator_challenge,
                _user_name
            )
            self.ext_attrs['MS-CHAP2-Success'] = auth_resp
            self.ext_attrs['MS-MPPE-Encryption-Policy'] = '\x00\x00\x00\x01'
            self.ext_attrs['MS-MPPE-Encryption-Type'] = '\x00\x00\x00\x06'
            mppeSendKey, mppeRecvKey = mppe.mppe_chap2_gen_keys(userpwd, nt_response)
            send_key, recv_key = mppe.gen_radius_encrypt_keys(
                mppeSendKey,
                mppeRecvKey,
                self.secret,
                self.authenticator)
            self.ext_attrs['MS-MPPE-Send-Key'] = send_key
            self.ext_attrs['MS-MPPE-Recv-Key'] = recv_key
            return True
        else:
            self.ext_attrs['Reply-Message'] = "E=691 R=1 C=%s V=3 M=<password error>" % ('\0' * 32)
            return False
        
        
    def get_pwd_type(self):
        if 'MS-CHAP-Challenge' in self:
            if 'MS-CHAP-Response' in self:
                return 'mschapv1'
            elif 'MS-CHAP2-Response' in self:
                return 'mschapv2'
        elif 'CHAP-Password' in self:
            return 'chap'
        else:
            return 'pap'
            

    def is_valid_pwd(self,userpwd):
        pwd_type = self.get_pwd_type()
        try:
            if pwd_type == 'pap':
                return userpwd == self.get_passwd()
            elif pwd_type == 'chap':
                return self.verifyChapEcrypt(userpwd)
            elif pwd_type == 'mschapv1':
                return False
            elif pwd_type == 'mschapv2':
                return self.verifyMsChapV2(userpwd)
            else:
                return False
        except Exception as err:
            import traceback
            traceback.print_exc()
            return False


class AcctMessage(AcctPacket):
    def __init__(self, code=AccountingRequest, id=None, secret=six.b(''),
            authenticator=None, **attributes):
        AcctPacket.__init__(self, code, id, secret, authenticator, **attributes)

    def format_str(self):
        return format_packet_str(self)

    def format_log(self):
        return format_packet_log(self)

    def __str__(self):
        _str = PacketStatusTypeMap.get(self.code)
        _str += " host=%s:%s" % self.source
        _str += ",id=%s"%self.id
        if self.code == 4:
            _str += ",username=%s,mac_addr=%s" % (self.get_user_name(),self.get_mac_addr())
        return _str   

    def CreateReply(self,**attributes):
        return AcctMessage(AccountingResponse, self.id,
            self.secret, self.authenticator, dict=self.dict,
            **attributes)    

    def get_user_name(self):
        try:
            user_name = tools.DecodeString(self.get(1)[0])
            if "@" in user_name:
                return user_name[:user_name.index("@")]
            else:
                return user_name
        except:
            return None
 

    def get_mac_addr(self):
        if self.client_macaddr:return self.client_macaddr
        try:return tools.DecodeString(self.get(31)[0]).replace("-",":")
        except:return None

    def get_nas_addr(self):
        _nas_addr = None
        try:
            return tools.DecodeAddress(self.get(4)[0])
        except:pass


    def get_nas_port(self):
        try:return tools.DecodeInteger(self.get(5)[0]) or 0
        except:return 0

    def get_service_type(self):
        try:return tools.DecodeInteger(self.get(0)[0]) or 0
        except:return 0
        
    def get_framed_ipaddr(self):
        try:return tools.DecodeAddress(self.get(8)[0])
        except:return None

    def get_framed_netmask(self):
        try:return tools.DecodeAddress(self.get(9)[0])
        except:return None

    def get_nas_class(self):
        try:return tools.DecodeString(self.get(25)[0])
        except:return None   

    def get_session_timeout(self):
        try:return tools.DecodeInteger(self.get(27)[0]) or 0
        except:return 0

    def get_calling_stationid(self):
        try:return tools.DecodeString(self.get(31)[0])
        except:return None   

    def get_acct_status_type(self):
        try:return tools.DecodeInteger(self.get(40)[0])
        except:return None

    def get_acct_input_octets(self):
        try:return tools.DecodeInteger(self.get(42)[0]) or 0
        except:return 0

    def get_acct_output_octets(self):
        try:return tools.DecodeInteger(self.get(43)[0]) or 0
        except:return 0

    def get_acct_sessionid(self):
        try:return tools.DecodeString(self.get(44)[0])
        except:return None                                                         

    def get_acct_sessiontime(self):
        try:return tools.DecodeInteger(self.get(46)[0]) or 0
        except:return 0                                                             

    def get_acct_input_packets(self):
        try:return tools.DecodeInteger(self.get(47)[0]) or 0
        except:return 0                                                       

    def get_acct_output_packets(self):
        try:return tools.DecodeInteger(self.get(48)[0]) or 0
        except:return 0           

    def get_acct_terminate_cause(self):
        try:return tools.DecodeInteger(self.get(49)[0]) or 0
        except:return 0           

    def get_acct_input_gigawords(self):
        try:return tools.DecodeInteger(self.get(52)[0]) or 0
        except:return 0       

    def get_acct_output_gigawords(self):
        try:return tools.DecodeInteger(self.get(53)[0]) or 0
        except:return 0                                                         

    def get_event_timestamp(self,timetype=0):
        try:
            return tools.DecodeDate(self.get(55)[0])
        except:
            return None

    def get_nas_port_type(self):
        try:return tools.DecodeInteger(self.get(61)[0]) or 0
        except:return 0   

    def get_nas_portid(self):
        try:return tools.DecodeString(self.get(87)[0])
        except:return None    
        
 