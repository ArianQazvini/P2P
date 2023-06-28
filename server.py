import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import  urlparse, parse_qs

import redis
r= redis.Redis(host='localhost', port=6379)
r.flushdb()
class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if (self.path == '/register'):
            length = int(self.headers.get('content-length'))
            data = json.loads(self.rfile.read(length).decode())
            print("------------------------------------")
            print(data)
            print("*************************************")
            username  = data['username']
            address = data["address"]
            r.set(username,address)

            keys = r.keys("*")
            values = r.mget(keys)
            for key, value in zip(keys, values):
                print(f"{key.decode('utf-8')}: {value.decode('utf-8')}")
            print("----------------------------------")

            response = {'message': 'Saved'}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self.send_response(403)
        self.end_headers()

    def do_GET(self):
        pass
        if (self.path=='/getAll'):
            print(self.path)
            redis_keys = r.keys('*')
            redis_data = r.mget(redis_keys)
            names = {}
            index =1
            for key, value in zip(redis_keys, redis_data):
                decoded_key = key.decode('utf-8')
                names[str(index)]=decoded_key
                index+=1

            print(names)
            print("----------------------")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(names).encode('utf-8'))
        else:
            splited = self.path.split('?')
            # print(splited)
            if(splited[0]=='/get'):
                # print(splited[1])
                decoded_value = r.get(splited[1]).decode('utf-8')
                dict= {'address':decoded_value}
                print(dict)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(dict).encode('utf-8'))

        # if self.path=='/get':
        #     print(self.path)
        #     record_id = self.path.split('/')[-1]
        #     if record_id in LocalData.records:
        #         self.send_response(200)
        #         self.send_header('Content-Type', 'application/json')
        #         self.end_headers()
        #
        #         # Return json, even though it came in as POST URL params
        #         data = json.dumps(LocalData.records[record_id]).encode('utf-8')
        #         logging.info("get record %s: %s", record_id, data)
        #         self.wfile.write(data)
        #
        #     else:
        #         self.send_response(404, 'Not Found: record does not exist')
        # else:
        #     self.send_response(403)
        # self.end_headers()


server = HTTPServer(('127.0.0.1', 8000), HTTPRequestHandler)
print("Server is listening on port 8000...")
server.serve_forever()
