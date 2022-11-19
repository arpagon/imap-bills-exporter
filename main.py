#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
#       imap-bills-exporter/main.py
#       Copyright 2022 sebastian.rojo <arpagon@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#

__author__ = "Sebastian Rojo"
__copyright__ = "Copyright 2022, Sebastian Rojo"
__credits__ = []
__license__ = "Apache 2.0"
__version__ = "0.1.1"
__maintainer__ = "Sebastian Rojo"
__email__ = ["arpagon at gmail.com"]
__status__ = "beta"

import os
import re

import imaplib, email
from dotenv import load_dotenv

load_dotenv()

IMAP_USER_EMAIL_ADDRESS = os.getenv('IMAP_USER_EMAIL_ADDRESS')
IMAP_USER_PASSWORD = os.getenv('IMAP_USER_PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER')
IMAP_BANK_SENDER_ACCOUNT=os.getenv('IMAP_BANK_SENDER_ACCOUNT')
IMAP_BANK_MSG_START=os.getenv('IMAP_BANK_MSG_START')
IMAP_BANK_MSG_END=os.getenv('IMAP_BANK_MSG_END')
IMAP_BANK_TRANSACTION_TC_REGEX=os.getenv('IMAP_BANK_TRANSACTION_TC_REGEX')

transaction_regex={
        "tc": IMAP_BANK_TRANSACTION_TC_REGEX
    }

# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

# Function to search for a key value pair
def search(key, value, con):
    result, data = con.search(None, key, '"{}"'.format(value))
    return data

# Function to get the list of emails under this label
def get_emails(result_bytes):
    msgs = [] # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = con.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs

def export_transactions_text(
        transaction_regex=transaction_regex,
        format=csv,
        outputfile=out/transactions.csv
        ):
    """Export transactions

    Receive an array of transactions notification Text and export to file (CSV)

    Args:
        transaction_regex: Regular expression for convert transactions notification 
            Text to Variables.
        format: Format of output file
        outputfile: Path where the export file is saved
        
    Returns:
        A bool for the state of creation process:

        And create a file like this

        Type,Value,Ref,Datetime,AcountType,Account

    Raises:
        IOError: An error occurred creating outputfile.
    """
    pass


# this is done to make SSL connection with GMAIL
con = imaplib.IMAP4_SSL(IMAP_SERVER)

# logging the user in
con.login(IMAP_USER_EMAIL_ADDRESS, IMAP_USER_PASSWORD)

# calling function to check for email under this label
con.select('Inbox')

# fetching emails from bank sender account
msgs = get_emails(search('FROM', IMAP_BANK_SENDER_ACCOUNT, con))

# Array of Transaction text
transactions_text=[]

# Array of Email whit problems
email_whit_problems=[]

for msg in msgs[::-1]:
    for response_part in msg:
        if type(response_part) is tuple:
            my_msg=email.message_from_bytes((response_part[1]))
            content = str(response_part[1], 'utf-8')
            data = str(content)

            # Handling errors related to unicodenecode
            try:
                # Clean data
                data=data.replace('\n','')
                data=data.replace('\r','')
                data=data.replace('=','')

                # Select Important part in email
                indexstart = data.find(IMAP_BANK_MSG_START)
                data2 = data[indexstart: len(data)]
                indexend = data2.find(IMAP_BANK_MSG_END)
                
                transactions=data2[0: indexend]

                if indexstart > 1:    
                    transactions_text.append(transactions)
                    if len(transactions) == 0 or len(transactions) >= 300:
                        email_whit_problems.append(data)
            except (UnicodeEncodeError) as e:
                pass

