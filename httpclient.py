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

PORT = 80

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.75)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        httpHeader = data[0]
        hSplit = httpHeader.split(' ')
        code = hSplit[1]
        return int(code)

    def get_headers(self,data):
        dataSplit = data.split("\r\n\r\n")
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
            try:
                part = self.socket.recv(1024)
                buffer.extend(part)
            except socket.timeout as e:
                done = True
        return buffer.decode('ISO-8859-1')

    def GET(self, url, args=None):
        code = 500
        body = ""

        # Parse url and extract host & path
        urlParse = urllib.parse.urlparse(url)
        host = urlParse.netloc
        path = urlParse.path

        # Start socket connection
        self.connect(host, PORT)

        # Send GET request with parsed info
        request = f"GET {path} / HTTP/1.1\r\nHost: {host}\r\n\r\n"
        self.sendall(request)

        # Handled received response
        response = self.recvall()

        # Extract the necessary info
        headers = self.get_headers(response)
        code = self.get_code(headers)
        body = self.get_body(response)
        # print(f"headers: {headers}\ncode: {code}\nbody: {body}")

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
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
