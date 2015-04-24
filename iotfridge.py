#!/usr/bin/env python
"""
    iotfridge.py - An IoT fridge API

    This software acts as the API between an SQLite database
    and the interfaces to the fridge.

    Remember to initialise a database first!
"""

# Libraries that we need
import sys
import sqlite3 as sql
import json

class IoTFridge:
    """
        Implements the IoT Fridge API
    """

    def __init__(self, dbpath, infile, outfile):
        self.db = sql.connect(dbpath)
        self.cur = self.db.cursor()
        self.infile = infile
        self.outfile = outfile

    # Begin API requests

    # reqjson refers to json document
    def req_list(self, reqjson):
        resp = { 'response': [], 'success': True }
        for row in self.cur.execute("SELECT name FROM products"):
            # Each row only contains one thing right now, name...
            resp['response'].append({'name': row[0] })
        print >> self.outfile, json.dumps(resp, indent = 1)

    # insert new item into products table. Name must be unique(for practical purposes for consumers)
    # id is automatically generated from row_id 
    def req_addProduct(self, reqjson):

        data = (reqjson['data']['name'], reqjson['data']['manufacturer'], reqjson['data']['measurement_type'])

        self.cur.execute("INSERT INTO products(name, manufacturer, measurement_type) VALUES(?, ?, ?)", data)
        self.db.commit()
        resp = {'response': 'OK', 'success': True}
        print >> self.outfile, json.dumps(resp)

   # insert item into fridge contents table
    def req_insertProduct(self, reqjson):

        product_name = reqjson['name']
        
        # get product id from products table by looking up unique product name
        self.cur.execute("SELECT id FROM products WHERE name=?", (product_name,))
        product_id = json.dumps(self.cur.fetchone())

        # get product measurement type from products table by name (quantity, volume or weight)
        self.cur.execute("SELECT measurement_type FROM products WHERE name=?", (product_name,))
        measurement_type = json.dumps(self.cur.fetchone()).strip('"[]')
        print(measurement_type)

        # enter measurement quantity into relevant measurement field in table, irrelevant values are set to NULL by default
        data = (product_id, reqjson['data'][measurement_type], reqjson['data']['useBy'])
        self.cur.execute("INSERT INTO fridge_contents(product_id, " + measurement_type + ", expiration_date) VALUES(?, ?, ?)", data)

        self.db.commit()
        resp = {'response': 'OK', 'success': True}
        print >> self.outfile, json.dumps(resp)


    # End API requests

    def processRequest(self, req):
        """
            Takes a JSON request, does some simple checking, and tries to call
            the appropriate method to handle the request. The called method is
            responsible for any output.
        """
        jsonData = json.loads(req)
        if "request" in jsonData:
            reqstr = 'req_{0}'.format(jsonData['request'])
            # Echo the request for easier output debugging
            print req
            if reqstr in dir(self):
                getattr(self,reqstr)(jsonData)
            else:
                print >> sys.stderr, "ERROR: {0} not implemented".format(
                    jsonData['request'])
                errorResp = {
                        'response': "{0} not implemented".format(
                            jsonData['request']),
                        'success': False}
                print >> self.outfile, json.dumps(errorResp)
        else:
                print >> sys.stderr, "ERROR: No request attribute in JSON"

    def run(self):
        """
            Read data input, assume a blank line signifies that the buffered
            data should now be parsed as JSON and acted upon
        """
        lines = []
        while True:
            line = self.infile.readline()
            #if first line blank
            if line == '': break
            #remove whitespace
            lines.append(line.strip())
            #if more than one line and last line in lines list blank
            if len(lines) > 1 and lines[-1] == '':
                #process json lines
                print(''.join(lines))
                self.processRequest( ''.join(lines) )
                lines = []


if __name__ == '__main__':
    """
        Connect stdin and stdout to accept and emit JSON data

        Non-API content is printed to stderr, so it can be redirected
        independently.
    """
    if len(sys.argv) != 2:
        print >> sys.stderr, "Usage: python iotfridge.py dbfilename"
        sys.exit(1)
    print >> sys.stderr, "Starting IoTFridge..."
    IOTF = IoTFridge(sys.argv[1], sys.stdin, sys.stdout)
    print >> sys.stderr, "Ready."
    try:
        IOTF.run()
    except KeyboardInterrupt:
        print >> sys.stderr, "Received interrupt, quitting..."
    print >> sys.stderr, "Done"
