#!/usr/bin/env python
"""
    iotfridge.py - An IoT fridge API

    This software acts as the API between an SQLite database
    and the interfaces to the fridge.

"""

# Libraries that we need
import sys
import sqlite3 as sql
import json
import time
import datetime
import re


class IoTFridge:
    """
        Implements the IoT Fridge API
    """

    def __init__(self, dbpath, infile, outfile):
        self.db = sql.connect(dbpath)
        self.cur = self.db.cursor()
        self.infile = infile
        self.outfile = outfile

################################################################################
############################## Begin API requests###############################

################################################################################
############################# Product API requests #############################

    # reqjson refers to json document
    def req_listProducts(self, reqjson):
        resp = { 'response': [], 'success': True }
        for row in self.cur.execute("SELECT name, brand, id FROM products"):
            # Each row only contains one thing right now, name...
            resp['response'].append({'name': row[0], 'brand': row[1], 'product_id': row[2] })
        print >> self.outfile, json.dumps(resp, indent = 1)

    # insert new item into products table. Name and brand combination must be unique
    # id is automatically generated from row_id 
    def req_addProduct(self, reqjson):
        data = (reqjson['name'], reqjson['brand'], reqjson['data']['measurement_type'], reqjson['data']['use_within'])
        self.cur.execute("INSERT INTO products(name, brand, measurement_type, use_within) VALUES(?, ?, ?, ?)", data)
        self.db.commit()
        resp = {'response': 'OK', 'success': True},
        print >> self.outfile, json.dumps(resp, indent = 1)

    # get product id from unique name and brand candidate key
    def req_removeProduct(self, reqjson):
        product_name = reqjson['name']
        product_brand = reqjson['brand']
        self.cur.execute("SELECT id FROM products WHERE name=? AND brand=?", (product_name, product_brand,))
        product_id = json.dumps(self.cur.fetchone()).strip('[]')
        resp = {'response': 'OK', 'success': True},
        print >> self.outfile, json.dumps(resp, indent = 1)


################################################################################
########################## fridge contents API requests ########################

    # list fridge contents
    def req_listContents(self, reqjson):
        resp = { 'response': [], 'success': True }
        for row in self.cur.execute("SELECT name, item_id, expiration_date, quantity, volume, weight, measurement_type FROM fridge_contents INNER JOIN products ON product_id = products.id"):
            amount = []
            for column in range(3, len(row)):
                column_value = str(row[column])
                if column_value != 'None':
                    amount.append(column_value)
            resp['response'].append({'name': row[0], 'item_id': row[1], 'expiration_date': row[2], 'amount': amount})
        print >> self.outfile, json.dumps(resp, indent = 1)

    # insert item into fridge contents table
    def req_insertItem(self, reqjson):

        product_name = reqjson['name']
        # get product id from name/brand candidate key
        product_name = reqjson['name']
        product_brand = reqjson['brand']
        self.cur.execute("SELECT id FROM products WHERE name=? AND brand=?", (product_name, product_brand,))
        product_id = json.dumps(self.cur.fetchone()).strip('[]')

        # get product measurement type from products table by name (quantity, volume or weight)
        self.cur.execute("SELECT measurement_type FROM products WHERE name=?", (product_name,))
        measurement_type = json.dumps(self.cur.fetchone()).strip('"[]')

        # enter measurement quantity into relevant measurement field in table, irrelevant values are set to NULL by default
        data = (product_id, reqjson['data'][measurement_type], reqjson['data']['use_by'])
        self.cur.execute("INSERT INTO fridge_contents(product_id, " + measurement_type + ", expiration_date) VALUES(?, ?, ?)", data)

        self.db.commit()
        resp = {'response': 'OK', 'success': True}
        print >> self.outfile, json.dumps(resp, indent = 1)

    # remove item from fridge contents table
    def req_removeItem(self, reqjson):

        item_id = str(reqjson['item_id'])
        self.cur.execute("DELETE FROM fridge_contents WHERE item_id = " + item_id)
        resp = {'response': 'OK', 'success': True}
        print >> self.outfile, json.dumps(resp, indent = 1)

    # open item and update use by date
    def req_openItem(self, reqjson):

        resp = { 'response': [], 'success': True }

        item_id = reqjson['item_id']

        self.cur.execute("SELECT product_id FROM fridge_contents INNER JOIN products ON product_id = products.id WHERE item_id = ?", (item_id,))
        product_id = json.dumps(self.cur.fetchone()).strip('[]')

        self.cur.execute("SELECT use_within FROM products WHERE id = ?", (product_id,))
        use_within = str(json.dumps(self.cur.fetchone()).strip('[]'))
        # if use_within date is not specified, don't change the expiry date
        if(use_within != 'null'):
            use_within = int(use_within)
        else:
            use_within = 0
        self.cur.execute("SELECT expiration_date FROM fridge_contents WHERE item_id = ?", (item_id,))
        expiration_date = str(json.dumps(self.cur.fetchone()).strip('"[]'))
        expiration_date = re.sub('-', '', expiration_date)
        expiration_date = int(expiration_date)

        # add use within date to expiry date and replace expiry date with new value
        current_date = datetime.date.today()
        updated_expiration_date = str(current_date + datetime.timedelta(days=use_within))
        self.cur.execute("UPDATE fridge_contents SET expiration_date = ? WHERE item_id = ?", (updated_expiration_date, item_id,))

        resp['response'].append({'expiration_date': updated_expiration_date})
        print >> self.outfile, json.dumps(resp, indent = 1)


################################################################################
########################### Favourites API requests ############################

    # add item to favourites
    def req_addFavourite(self, reqjson):

        product_id = str(reqjson['product_id'])

        # enter product id into table
        data = (product_id)
        self.cur.execute("INSERT INTO favourites(product_id) VALUES(?)", data)
        self.db.commit()
        resp = {'response': 'OK', 'success': True}
        print >> self.outfile, json.dumps(resp, indent = 1)

    def req_removeFavourite(self, reqjson):
        
        product_id = reqjson['product_id']

        self.cur.execute("DELETE FROM favourites WHERE product_id = ?", (product_id,))

        resp = {'response': 'OK', 'success': True}
        print >> self.outfile, json.dumps(resp, indent = 1)



    # return ids of favourites products
    def req_listFavourites(self, reqjson):
        resp = { 'response': [], 'success': True }     
        for row in self.cur.execute("SELECT product_id FROM favourites"):
            resp['response'].append({"product_id": row[0]})
        print >> self.outfile, json.dumps(resp, indent = 1)


################################################################################
######################### Expiry date API requests #############################

    # check items in fridge for expiry date and return items that are out of date in response
    def req_checkDates(self, reqjson):
        resp = { 'response': [], 'success': True }     
        current_date = int(time.strftime("%Y%m%d"))
        # expiry_reminder_warning would be added to a preferences table in later iterations
        expiry_reminder_warning = 2
        for row in self.cur.execute("SELECT name, item_id, expiration_date FROM fridge_contents INNER JOIN products ON product_id = products.id"):
            # format date from database for use in integer comparison
            item_expiry_date = int(re.sub('-', '', (str(row[2]))))
            if item_expiry_date - current_date <= expiry_reminder_warning:
                resp['response'].append({'name': row[0], 'item_id': row[1]})
        print >> self.outfile, json.dumps(resp, indent = 1)


################################################################################
############################# End API requests #################################

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
