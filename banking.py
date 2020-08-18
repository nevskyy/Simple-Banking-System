# import random
import rstr
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS card 
(id INTEGER PRIMARY KEY AUTOINCREMENT, 
number TEXT, 
pin TEXT, 
balance INTEGER DEFAULT  0);""")
conn.commit()


class Account:
    database = dict()

    def __init__(self):
        self.account_number = 0
        self.card_number = 0
        self.pin_number = 0

    def num_creator(self):
        while True:
            self.card_number = rstr.xeger('^4[0]{5}[0-9]{10}')
            odd = []
            for i in range(0, len(self.card_number)-1):
                if i % 2 == 0:
                    odd.append(int(self.card_number[i]) * 2)
                else:
                    odd.append(int(self.card_number[i]))
            over_nine = []
            for num in odd:
                if num > 9:
                    over_nine.append(num - 9)
                else:
                    over_nine.append(num)
            if (sum(over_nine) + int(self.card_number[-1])) % 10 == 0:
                break
            else:
                continue
        self.account_number = self.card_number[6:-3]
        self.pin_number = rstr.xeger('^[0-9]{4}')
        params = (self.card_number, self.pin_number, 0)

        cur.execute("INSERT INTO card VALUES (NULL, ?, ?, ?)", params)
        # cur.execute("INSERT INTO card (number, pin, balance) VALUES (?, ?, ?)", params)
        # print(cur.fetchall())
        conn.commit()
        return self.account_number, self.card_number, self.pin_number

    def open_account(self):
        self.num_creator()
        if self.account_number in Account.database.keys():
            self.num_creator()
        else:
            Account.database[self.account_number] = {'card': self.card_number,
                                                     'pin': self.pin_number,
                                                     'balance': 0}
            # print(Account.database)
            return Account.database

    @staticmethod
    def check_login():
        input_card = input("\nEnter your card number:\n> ")
        input_pin = input("Enter your PIN:\n> ")
        try:
            cur.execute("SELECT number FROM card")
            cards = cur.fetchall()
            # print(cards)
            cur.execute("SELECT pin FROM card")
            pins = cur.fetchall()
            # print(pins)
            if (input_card,) not in cards or (input_pin,) not in pins:
                print("\nWrong card number or PIN!\n")
                conn.commit()
            elif (input_card,) in cards or (input_pin,) in pins:
                print("\nYou have successfully logged in!\n")

                while True:
                    print('1. Balance\n2. Add Income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
                    user_choice = input('> ')
                    if user_choice == '1':
                        print()
                        cur.execute(f"SELECT balance FROM card WHERE number = {input_card}")
                        balance = cur.fetchall()
                        for item in balance:
                            print("Balance:", item[0])
                        conn.commit()
                        print()
                    elif user_choice == '2':
                        print("\nEnter income:")
                        income = int(input('> '))
                        cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number = {input_card}")
                        conn.commit()
                        print("Income was added!\n")
                    elif user_choice == '3':
                        print("\nTransfer\nEnter card Number:")
                        transfer_card_num = input('> ')
                        cur.execute("SELECT number FROM card")
                        res = cur.fetchall()
                        # print(res)
                        # print(transfer_card_num)
                        conn.commit()

                        odd = []
                        for i in range(0, len(transfer_card_num) - 1):
                            if i % 2 == 0:
                                odd.append(int(transfer_card_num[i]) * 2)
                            else:
                                odd.append(int(transfer_card_num[i]))
                        over_nine = []
                        for num in odd:
                            if num > 9:
                                over_nine.append(num - 9)
                            else:
                                over_nine.append(num)
                        if (sum(over_nine) + int(transfer_card_num[-1])) % 10 != 0:
                            print("\nProbably you made mistake in the card number. Please try again!\n")
                        elif (transfer_card_num,) not in res:
                            print("\nSuch a card does not exist.\n")
                            conn.commit()
                        elif transfer_card_num == input_card:
                            print("\nYou can't transfer money to the same account!\n")
                        else:
                            print("Enter how much money you want to transfer:")
                            transfer_amount = int(input('> '))
                            result = cur.execute(f"SELECT balance FROM card WHERE number = {input_card}").fetchone()
                            # print(result)
                            # print(type(result[0]))
                            if transfer_amount <= result[0]:
                                cur.execute(f"UPDATE card SET balance = balance + {transfer_amount} WHERE number = {transfer_card_num}")
                                conn.commit()
                                cur.execute(f"UPDATE card SET balance = balance - {transfer_amount} WHERE number = {input_card}")
                                conn.commit()
                                print("Success!\n")
                            else:
                                print("Not enough money!\n")
                                conn.commit()
                    elif user_choice == '4':
                        cur.execute(f"DELETE FROM card WHERE number = {input_card}")
                        conn.commit()
                        print("\nThe account has been closed!\n")
                    elif user_choice == '5':
                        print("\nYou have successfully logged out!\n")
                        break
                    elif user_choice == '0':
                        print('\nBye!')
                        exit()
        except KeyError:
            print("\nWrong card number or PIN!\n")


show_menu = True
while show_menu:
    print('1. Create an account\n2. Log into account\n0. Exit')
    user_choice = input('> ')
    if user_choice == '1':
        new_account = Account()
        new_account.open_account()
        print("\nYour card has been created\n")
        print(f"Your card number:\n{new_account.card_number}")
        print(f"Your card PIN:\n{new_account.pin_number}\n")
    elif user_choice == '2':
        Account.check_login()
    elif user_choice == '0':
        print('\nBye!')
        show_menu = False
        conn.commit()
        cur.close()
        conn.close()