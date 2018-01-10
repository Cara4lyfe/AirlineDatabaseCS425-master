#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys
from flask import Flask, render_template, request

con = None
app = Flask(__name__)
global currentLogin
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/booking.html')
def booking():
    try:
        con = psycopg2.connect("host='localhost' dbname='Airline' user='postgres' password='Mike8101'")

        global currentLogin
        currentLoginDic = {'key': currentLogin}
        #cardnum
        cur = con.cursor()
        cur.execute('SELECT *'
                    #'FROM flight WHERE flightid IN ( '
                    #'SELECT flightid '
                    'FROM costs NATURAL JOIN flight '
                    'WHERE bookingid IN ( '
                    'SELECT bookingid '
                    'FROM booking '
                    'WHERE cardnum IN ( '
                    'SELECT cardnum '
                    'FROM payment '
                    'WHERE emailaddress = %(key)s))', currentLoginDic)
        bookings = cur.fetchall()

        return render_template('booking.html', email=currentLogin, bookings = bookings)
    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()

        print
        'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()

@app.route('/bookingupdate', methods=['POST'])
def bookingupdate():
    try:
        con = psycopg2.connect("host='localhost' dbname='Airline' user='postgres' password='Mike8101'")
        cur = con.cursor()
        #store current login info
        global currentLogin
        currentLoginDic = {'key': currentLogin}
        bookingDic = {'key': request.form['bookingid']}
        cur.execute('DELETE FROM costs WHERE bookingid = %(key)s', bookingDic)
        cur.execute('DELETE FROM booking WHERE bookingid = %(key)s', bookingDic)

        cur1 = con.cursor()
        cur1.execute('SELECT *'
                    'FROM flight WHERE flightid IN ( '
                    'SELECT flightid '
                    'FROM costs '
                    'WHERE bookingid IN ( '
                    'SELECT bookingid '
                    'FROM booking '
                    'WHERE cardnum IN ( '
                    'SELECT cardnum '
                    'FROM payment '
                    'WHERE emailaddress = %(key)s)))', currentLoginDic)
        bookings = cur1.fetchall()

        return render_template('booking.html', email=currentLogin, bookings=bookings)

    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()
        print
        'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()

@app.route('/log', methods=['POST'])
def log():
    try:
        con = psycopg2.connect("host='localhost' dbname='Airline' user='postgres' password='Mike8101'")
        cur = con.cursor()
        #store current login info
        global currentLogin
        currentLogin= request.form['email']
        loginemail = {'key': request.form['email']}
        cur.execute('SELECT emailaddress from customer WHERE emailaddress = %(key)s', loginemail)
        #print(cur)
        if cur.fetchone() is not None:
            return render_template('main.html')
        else:
            return render_template('LoginFail.html')
    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()
        print
        'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()


@app.route('/reg.html')
def reg():
    return render_template('reg.html')

@app.route('/login', methods=['POST'])
def login():
    try:
        con = psycopg2.connect("host='localhost' dbname='Airline' user='postgres' password='Mike8101'")
        cur = con.cursor()
        email = request.form['email']
        name = request.form['name']
        cur.execute('INSERT INTO customer VALUES(%s,%s,NULL)', (email,name))
        con.commit()
    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()

        print
        'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()
    return render_template('index.html')

@app.route('/user.html')
def user():
    try:
        con = psycopg2.connect("host='localhost' dbname='Airline' user='postgres' password='Mike8101'")


        global currentLogin
        currentLoginDic = {'key': currentLogin}
        cur = con.cursor()
        cur.execute('SELECT * from payment WHERE emailaddress = %(key)s', currentLoginDic)
        tuple1 = cur.fetchall()

        cur1 = con.cursor()
        cur1.execute('SELECT * from addresses WHERE emailaddress = %(key)s', currentLoginDic)
        tuple2 = cur1.fetchall()
        print(tuple2)

        return render_template('user.html', email=currentLogin, tuple=tuple1, tuple2=tuple2)
    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()

        print
        'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()

@app.route('/userupdate', methods=['POST'])
def userupdate():
    try:
        global currentLogin
        currentLoginDic = {'key': currentLogin}
        con = psycopg2.connect("host='localhost' dbname='Airline' user='postgres' password='Mike8101'")

        cur2 = con.cursor()
        # update
        if request.form['submit'] == 'submit':
            d = {'cardNum': request.form['cardnum'],
                 'zipcode': request.form['zipcode'],
                 'address': request.form['address'],
                 'country': request.form['country'],
                 'state': request.form['state'],
                 'city': request.form['city']}

            cur2.execute(""" UPDATE payment 
                SET address = '%(address)s',
                zipcode = %(zipcode)s,
                country = '%(country)s',
                state = '%(state)s',
                city = '%(city)s'
                WHERE cardnum = %(cardNum)s""" % d)
        elif request.form['submit'] == 'delete':
            d = {'cardNum': request.form['cardnum']}
            cur2.execute("""DELETE FROM payment WHERE cardnum = '%(cardNum)s'""" % (d))
        elif request.form['submit'] == 'add':
            d = {'cardNum': request.form['cardnum'],
                 'expdate': request.form['expdate'],
                 'cardtype': request.form['cardtype'],
                 'zipcode': request.form['zipcode'],
                 'address': request.form['address'],
                 'country': request.form['country'],
                 'state': request.form['state'],
                 'city': request.form['city'],
                 'cL': currentLogin}
            cur2.execute("""INSERT INTO payment VALUES('%(cardNum)s',
                                                        '%(expdate)s',
                                                        '%(cardtype)s',
                                                        '%(address)s',
                                                        '%(zipcode)s',
                                                        '%(country)s',
                                                        '%(state)s',
                                                        '%(city)s',
                                                        '%(cL)s'
                                                        )""" % (d))
        #addupdate
        elif request.form['submit'] == 'addsubmit':
            d = {'ozipcode': request.form['oaddzipcode'],
                 'oaddress': request.form['oaddaddress'],
                 'ocountry': request.form['oaddcountry'],
                 'ostate': request.form['oaddstate'],
                 'ocity': request.form['oaddcity'],
                 'zipcode': request.form['oaddzipcode'],
                 'address': request.form['oaddaddress'],
                 'country': request.form['oaddcountry'],
                 'state': request.form['oaddstate'],
                 'city': request.form['oaddcity'],
                 'key': currentLogin}

            cur2.execute(""" UPDATE addresses 
                SET address = '%(address)s',
                zipcode = '%(zipcode)s',
                country = '%(country)s',
                state = '%(state)s',
                city = '%(city)s'
                WHERE 
                address = '%(oaddress)s' AND 
                zipcode = '%(ozipcode)s' AND 
                country = '%(ocountry)s' AND 
                state = '%(ostate)s' AND 
                city = '%(ocity)s' AND 
                emailaddress = '%(key)s'""" % d)
        elif request.form['submit'] == 'adddelete':
            d = {'ozipcode': request.form['oaddzipcode'],
                 'oaddress': request.form['oaddaddress'],
                 'ocountry': request.form['oaddcountry'],
                 'ostate': request.form['oaddstate'],
                 'ocity': request.form['oaddcity'],
                 'zipcode': request.form['oaddzipcode'],
                 'address': request.form['oaddaddress'],
                 'country': request.form['oaddcountry'],
                 'state': request.form['oaddstate'],
                 'city': request.form['oaddcity'],
                 'key': currentLogin}

            cur2.execute("""DELETE FROM addresses 
                            WHERE 
                            emailaddress = '%(key)s' AND 
                            address = '%(address)s' AND 
                            zipcode = '%(zipcode)s' AND 
                            country = '%(country)s' AND 
                            state = '%(state)s' AND 
                            city = '%(city)s'
                            """ % d)
        elif request.form['submit'] == 'addadd':
            d = {'zipcode': request.form['addzipcode'],
                 'address': request.form['addaddress'],
                 'country': request.form['addcountry'],
                 'state': request.form['addstate'],
                 'city': request.form['addcity'],
                 'cL': currentLogin}
            cur2.execute("""INSERT INTO addresses VALUES('%(cL)s',
                                                        '%(address)s',
                                                        '%(zipcode)s',
                                                        '%(country)s',
                                                        '%(state)s',
                                                        '%(city)s'
                                                        )""" % (d))
        con.commit()

        cur = con.cursor()
        cur.execute('SELECT * from payment WHERE emailaddress = %(key)s', currentLoginDic)
        tuple1 = cur.fetchall()
        cur1 = con.cursor()
        cur1.execute('SELECT * from addresses WHERE emailaddress = %(key)s', currentLoginDic)
        tuple2 = cur1.fetchall()

        return render_template('user.html', email=currentLogin, tuple=tuple1, tuple2=tuple2)
    except psycopg2.DatabaseError as e:
        if con:
            con.rollback()

        print
        'Error %s' % e
        sys.exit(1)
    finally:
        if con:
            con.close()


if __name__ == "__main__":
    app.run(debug=True)



