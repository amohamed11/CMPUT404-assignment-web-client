#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
import json

HTTP_PORT = 80
HTTPS_PORT = 443

NOT_FOUND = 404
BAD_GATEWAY = 504


# get host information
def get_remote_ip(host):
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        return NOT_FOUND

    return remote_ip

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self, url):
        port = HTTP_PORT
        urlSplit = url.split(":")
        if len(urlSplit) > 1:
            port = int(urlSplit[1])
        return port

    def connect(self, host, port):
        remote_ip = get_remote_ip(host)
        if remote_ip == NOT_FOUND:
            return NOT_FOUND
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((remote_ip, port))
        return None

    def get_code(self, data):
        httpHeader = data[0]
        hSplit = httpHeader.split(' ')
        if len(hSplit) < 2:
            print("Data: ", data)
        code = hSplit[1]
        return int(code)

    def get_headers(self,data):
        dataSplit = data.split("\r\n")
        headers = dataSplit[0].split('\n')
        return headers

    def get_body(self, data):
        dataSplit = data.split("\r\n\r\n")
        body = dataSplit[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        # Parse url and extract host & path
        urlParse = urllib.parse.urlparse(url)
        host = urlParse.netloc
        domain = host
        path = urlParse.path+"?"+urlParse.query
        if len(path) == 1:
            path = "/"

        # Extract port
        port = HTTP_PORT
        if urlParse.scheme == "https":
            port = HTTPS_PORT
        else:
            port = self.get_host_port(host)
            domain = host.split(":")[0]

        # Attempt to start socket connection
        if self.connect(domain, port) == NOT_FOUND:
            return HTTPResponse(NOT_FOUND, body)

        # Send GET request with parsed info
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)

        # Handled received response
        response = self.recvall()

        self.close()

        # Extract the necessary info
        headers = self.get_headers(response)
        code = self.get_code(headers)
        body = self.get_body(response)


        # Wasted 6 hrs on the below, so I'm leaving it here out of sheer spite.
        # if code == 301 or code == 302:
        #     matches = re.findall(r"(?<=[Ll]ocation: )\S+", response)
        #     if len(matches) > 0:
        #         newUrl = matches[0]
        #         print(urllib.parse.urlparse(newUrl))
        #         return self.GET(newUrl, args)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        if args != None:
            args = urllib.parse.urlencode(args)
        else:
            args = ""
        argsLength = len(args)

        # Parse url and extract host & path
        urlParse = urllib.parse.urlparse(url)
        host = urlParse.netloc
        domain = host
        path = urlParse.path+"?"+urlParse.query


        # Extract port
        port = HTTP_PORT
        if urlParse.scheme == "https":
            port = HTTPS_PORT
        else:
            port = self.get_host_port(host)
            domain = host.split(":")[0]

        # Attempt to start socket connection
        if self.connect(domain, port) == NOT_FOUND:
            return HTTPResponse(NOT_FOUND, body)

        # Send POST request with parsed info & arguments
        httpHeader = f"POST {path} HTTP/1.1\r\nHost: {host}\r\n"
        contentHeader = f"Content-type: application/x-www-form-urlencoded\r\nContent-length: {argsLength}\r\n\r\n"
        request = httpHeader + contentHeader + args

        self.sendall(request)
        self.socket.shutdown(socket.SHUT_WR)

        # Handled received response
        response = self.recvall()

        self.close()

        # Extract the necessary info
        headers = self.get_headers(response)
        code = self.get_code(headers)
        body = self.get_body(response)
        # print(request)
        # print(response)


        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
