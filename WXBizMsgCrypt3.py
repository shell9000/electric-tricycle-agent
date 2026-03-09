#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
企業微信官方加解密庫
"""
import socket
import base64
import string
import random
import hashlib
import struct
from Crypto.Cipher import AES
import xml.etree.cElementTree as ET

class FormatException(Exception):
    pass

def throw_exception(message, exception_class=FormatException):
    raise exception_class(message)

class SHA1:
    def getSHA1(self, token, timestamp, nonce, encrypt):
        try:
            sortlist = [token, timestamp, nonce, encrypt]
            sortlist.sort()
            sha = hashlib.sha1()
            sha.update("".join(sortlist).encode())
            return 0, sha.hexdigest()
        except Exception as e:
            return -40003, None

class XMLParse:
    def extract(self, xmltext):
        try:
            xml_tree = ET.fromstring(xmltext)
            encrypt = xml_tree.find("Encrypt")
            touser_name = xml_tree.find("ToUserName")
            return 0, encrypt.text, touser_name.text
        except Exception as e:
            return -40002, None, None

    def generate(self, encrypt, signature, timestamp, nonce):
        resp_dict = {
            'Encrypt': encrypt,
            'MsgSignature': signature,
            'TimeStamp': timestamp,
            'Nonce': nonce,
        }
        resp_xml = ['<xml>']
        for k, v in resp_dict.items():
            resp_xml.append('<{0}>{1}</{0}>'.format(k, v))
        resp_xml.append('</xml>')
        return "".join(resp_xml)

class PKCS7Encoder():
    block_size = 32

    def encode(self, text):
        text_length = len(text)
        amount_to_pad = self.block_size - (text_length % self.block_size)
        if amount_to_pad == 0:
            amount_to_pad = self.block_size
        pad = chr(amount_to_pad)
        return text + (pad * amount_to_pad).encode()

    def decode(self, decrypted):
        pad = decrypted[-1]
        if isinstance(pad, int):
            pad = pad
        else:
            pad = ord(pad)
        return decrypted[:-pad]

class Prpcrypt(object):
    def __init__(self, key):
        self.key = base64.b64decode(key + "=")
        self.mode = AES.MODE_CBC

    def encrypt(self, text, receiveid):
        text = text.encode()
        text = self.get_random_str().encode() + struct.pack("I", socket.htonl(len(text))) + text + receiveid.encode()
        pkcs7 = PKCS7Encoder()
        text = pkcs7.encode(text)
        cryptor = AES.new(self.key, self.mode, self.key[:16])
        ciphertext = cryptor.encrypt(text)
        return 0, base64.b64encode(ciphertext)

    def decrypt(self, text, receiveid):
        try:
            cryptor = AES.new(self.key, self.mode, self.key[:16])
            plain_text = cryptor.decrypt(base64.b64decode(text))
        except Exception as e:
            return -40007, None
        
        try:
            pkcs7 = PKCS7Encoder()
            plain_text = pkcs7.decode(plain_text)
            content = plain_text[16:]
            xml_len = struct.unpack("!I", content[:4])[0]
            xml_content = content[4:xml_len+4]
            from_receiveid = content[xml_len+4:]
        except Exception as e:
            return -40008, None
        
        if from_receiveid.decode('utf8') != receiveid:
            return -40005, None
        return 0, xml_content

    def get_random_str(self):
        return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

class WXBizMsgCrypt(object):
    def __init__(self, sToken, sEncodingAESKey, sReceiveId):
        try:
            self.key = sEncodingAESKey
            self.token = sToken
            self.receiveid = sReceiveId
            self.crypt = Prpcrypt(sEncodingAESKey)
        except Exception as e:
            throw_exception("[error]: init Prpcrypt fail")

    def VerifyURL(self, sMsgSignature, sTimeStamp, sNonce, sEchoStr):
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, sTimeStamp, sNonce, sEchoStr)
        if ret != 0:
            return ret, None
        if signature != sMsgSignature:
            return -40001, None
        ret, sReplyEchoStr = self.crypt.decrypt(sEchoStr, self.receiveid)
        return ret, sReplyEchoStr

    def EncryptMsg(self, sReplyMsg, sNonce, timestamp=None):
        pc = Prpcrypt(self.key)
        ret, encrypt = pc.encrypt(sReplyMsg, self.receiveid)
        if ret != 0:
            return ret, None
        if timestamp is None:
            timestamp = str(int(time.time()))
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, timestamp, sNonce, encrypt.decode('utf8'))
        if ret != 0:
            return ret, None
        xmlparse = XMLParse()
        return ret, xmlparse.generate(encrypt.decode('utf8'), signature, timestamp, sNonce)

    def DecryptMsg(self, sPostData, sMsgSignature, sTimeStamp, sNonce):
        xmlparse = XMLParse()
        ret, encrypt, touser_name = xmlparse.extract(sPostData)
        if ret != 0:
            return ret, None
        sha1 = SHA1()
        ret, signature = sha1.getSHA1(self.token, sTimeStamp, sNonce, encrypt)
        if ret != 0:
            return ret, None
        if signature != sMsgSignature:
            return -40001, None
        ret, xml_content = self.crypt.decrypt(encrypt, self.receiveid)
        return ret, xml_content
