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
IMAP_FILTER=os.getenv('IMAP_FILTER')
IMAP_BANK_MSG_START=os.getenv('IMAP_BANK_MSG_START')
IMAP_BANK_MSG_END=os.getenv('IMAP_BANK_MSG_END')
REGEX_BANK_FILE=os.getenv('REGEX_BANK_FILE')


notification_regex = []
with open(REGEX_BANK_FILE) as regex_bank_file:
    for line in regex_bank_file:
        notification_regex.append(line.strip('\n'))

# Function to get email content part i.e its body part
def get_body(msg):
    if msg.is_multipart():
        return get_body(msg.get_payload(0))
    else:
        return msg.get_payload(None, True)

# Function to search for a key value pair
def search(imap_filter, imap_con):
    '''Search email 
    
    using: https://www.rfc-editor.org/rfc/rfc3501#section-6.4.4
    To build better filter you can use https://github.com/ikvk/imap_tools
    
    Args:
        imap_filter
    '''
    result, data = imap_con.search(None, imap_filter)
    return data

# Function to get the list of emails under this label
def get_emails(result_bytes, imap_con):
    msgs = [] # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = imap_con.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs

def export_transactions_text(
        transactions_text,
        transaction_regex=notification_regex,
        format="csv",
        outputfile="target/transactions.csv"
        ):
    """Export transactions

    Receive an array of transactions notification Text and export to file (CSV)

    Args:
        transactions_text: Array of transactions notification text
        transaction_regex: Regular expression for convert transactions notification 
            Text to Variables.
        format: Format of output file
        outputfile: Path where the export file is saved
        
    Returns:
        A bool for the state of creation process:

        And create a file like this

        Type,Value,dest,Date,time,Account

    Raises:
        IOError: An error occurred creating outputfile.
    """
    if format=="csv":
        import csv
        
        header = ['Type', 'Value', 'dest', 'Date','time', 'Account']
        
        with open(outputfile, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for transaction in transactions_text:
                print(transaction)
                for regex in notification_regex:                    
                    match = re.match(regex, transaction)
                    if match:
                        print(match.groupdict())
                        writer.writerow(
                            [
                                match['type'],
                                match['value'],
                                match['dest'],
                                match['date'],
                                match['time'],
                                match['account']
                            ]
                        )
        return True

def save_transactions_to_file(
        transactions_text,
        outputfile="target/transactions.text"
        ):
    ''' Save transactions to file
    
    Save Notification transactions text to a text file
    Args:
        transactions_text: Array of transactions notification text
        outputfile: Path where the export file is saved
     
     Returns:
        A bool for the state of creation process:
    '''
    with open(outputfile, 'w', encoding='UTF8') as f:
        for transactions in transactions_text:
            f.write('%s\n' % transactions)

def get_transactions_from_imap(imap_con):
    """get_transactions_from_imap

    Get Notification transactions text from imap
        
    Returns:
        Array of transaction
    """

    # fetching emails from bank sender account
    msgs = get_emails(search(IMAP_FILTER, imap_con), imap_con)

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
    
    return transactions_text

def main():
    # this is done to make SSL connection with GMAIL
    imap_con = imaplib.IMAP4_SSL(IMAP_SERVER)

    # logging the user in
    imap_con.login(IMAP_USER_EMAIL_ADDRESS, IMAP_USER_PASSWORD)

    # calling function to check for email under this label
    imap_con.select('Inbox')

    transactions_text=get_transactions_from_imap(imap_con)

    save_transactions_to_file(transactions_text)

    export_transactions_text(transactions_text, notification_regex)

if __name__ == "__main__":
    main()