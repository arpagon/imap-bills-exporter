#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
#
# imap-bills-exporter/main.py
# Copyright 2022 Sebastian Rojo <arpagon@gmail.com>
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
from datetime import datetime

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
# TODO def get_body(msg: MIMEMultipart) -> str:
def get_body(msg):
    """
    This function takes in a MIMEMultipart email object and returns 
    its body as a string. If the email is not multipart, 
    it simply returns the payload.

    Args:
        msg (MIMEMultipart): The MIMEMultipart email object.

    Returns:
        str: The body of the email as a string.
    """
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
# TODO def get_emails(result_bytes: list, imap_con: IMAP4_SSL) -> list:
def get_emails(result_bytes, imap_con):
    """
    This function takes in a list of email IDs and an IMAP4_SSL 
    connection object. It retrieves the email data for each ID 
    and returns the email data as a list of strings.

    Args:
        result_bytes (list): The list of email IDs.
        imap_con (IMAP4_SSL): The IMAP4_SSL connection object.

    Returns:
        list: A list of strings containing the email data.
    """
    msgs = [] # all the email data are pushed inside an array
    for num in result_bytes[0].split():
        typ, data = imap_con.fetch(num, '(RFC822)')
        msgs.append(data)
    return msgs


def clean_value(currency_string: str) -> float:
    '''
    This function takes in a string representing a currency 
    value and cleans it by removing dollar signs and replacing
    commas and periods with nothing. It then splits the string
    into its integral and decimal parts, converts them to floats,
    and combines them into a single float value. Finally, 
    the function returns the cleaned float value.

    Args:
        currency_string (str): The string representing the currency value to be cleaned.

    Returns:
        float: The cleaned float value.
    '''
    # Clean match['value']
    if currency_string[-3] in [",","."]:
        # Value has .00
        value_integral = currency_string[:-3]
        value_integral = value_integral.replace("$","")
        value_integral = value_integral.replace(".","")
        value_integral = value_integral.replace(",","")
        value_decimal = currency_string[-2:]
        print(value_decimal)
        value = float(value_integral + "." + value_decimal)
    else:
        # Value dont has .00
        value_integral = currency_string
        value_integral = value_integral.replace("$","")
        value_integral = value_integral.replace(".","")
        value_integral = value_integral.replace(",","")
        value = float(value_integral + ".00")
    print(currency_string,value,value_integral)
    return value

def clean_date(date_string: str, time_string: str) -> datetime:
    """
    This function takes in a date and time string in the 
    format of "DD/MM/YYYY" and "HH:MM", respectively. 
    It splits the date and time strings into their respective 
    components, converts them into integers, and then combines
    them into a single datetime object. Finally, the function 
    returns the cleaned datetime object.

    Args:
        date_string (str): The date string to be cleaned.
        time_string (str): The time string to be cleaned.

    Returns:
        datetime: The cleaned datetime object.
    """
    date_list=date_string.split("/")
    time_list=time_string.split(":")
    date = datetime(
            day=int(date_list[0]),
            month=int(date_list[1]),
            year=int(date_list[2]),
            hour=int(time_list[0]),
            minute=int(time_list[1])
    )
    return date

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
        
        header = ['Type', 'ValueString', 'ValueFloat', 'dest', 'Date','time', 'DateTime', 'Account']
        
        with open(outputfile, 'w', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for transaction in transactions_text:
                print(transaction)
                for regex in notification_regex:                    
                    match = re.match(regex, transaction)
                    if match:
                        match_dict=match.groupdict()
                        print(match_dict)

                        if not "time" in match_dict.keys():
                            match_dict['time'] = "00:00"

                        # Write CSV
                        writer.writerow(
                            [
                                match_dict['type'],
                                match_dict['value'],
                                clean_value(match_dict['value']),
                                match_dict['dest'],
                                match_dict['date'],
                                match_dict['time'],
                                clean_date(match_dict['date'],match_dict['time']),
                                match_dict['account'],
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

def load_transactions_from_file(
        inputfile="target/transactions.text"
        ):
    ''' Load transactions from file
    
    Load Notification transactions text from a text file
    Args:
        inputfile: Path where the export file was saved
     
     Returns:
        transactions_text: Array of transactions notification text
    '''
    transactions_text = []
    with open(inputfile, 'r', encoding='UTF8') as transactions_text_file:
        for line in transactions_text_file:
            transactions_text.append(line.strip('\n'))
    
    return transactions_text

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
    """
    This function establishes an SSL connection with a Gmail IMAP server, 
    logs in with the specified credentials, retrieves email data from the 
    user's inbox, extracts transactions from the email data, saves the 
    transactions to a file, and exports the transactions as text.
    """
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