from typing import List, Optional, Union, Dict
from datetime import datetime

class Client:
    def __init__(self, cin: Union[int, str], firstName: str, lastName: str, tel: Union[int, str] = ""):
        if not isinstance(cin, (int, str)) or not isinstance(firstName, str) or not isinstance(lastName, str):
            raise TypeError("Invalid type for client attributes")
        self.__CIN, self.__firstName, self.__lastName = str(cin), firstName.strip(), lastName.strip()
        self.__tel, self.__accounts = str(tel) if tel else "", []

    def get_CIN(self) -> str: return self.__CIN
    def get_name(self) -> str: return f"{self.__firstName} {self.__lastName}"
    def get_tel(self) -> str: return self.__tel
    def add_account(self, account: 'Account') -> None: self.__accounts.append(account)
    def get_accounts(self) -> List['Account']: return self.__accounts

class Account:
    __nbAccounts = 0

    def __init__(self, owner: Client):
        if not isinstance(owner, Client): raise TypeError("Owner must be Client")
        Account.__nbAccounts += 1
        self.__code, self.__balance, self.__owner = Account.__nbAccounts, 0.0, owner
        self.__transactions = []
        owner.add_account(self)

    def get_code(self) -> int: return self.__code
    def get_balance(self) -> float: return self.__balance
    def get_owner(self) -> Client: return self.__owner
    def get_transactions(self) -> List[dict]: return self.__transactions

    def __log(self, trans_type: str, amount: float, desc: str) -> None:
        self.__transactions.append({'type': trans_type, 'amount': amount, 'desc': desc, 
                                   'time': datetime.now().strftime("%Y-%m-%d %H:%M"), 'bal': self.__balance})

    def credit(self, amount: Union[int, float]) -> bool:
        if not isinstance(amount, (int, float)) or amount <= 0: return False
        self.__balance += float(amount)
        self.__log("Credit", amount, f"+{amount} DA")
        return True

    def debit(self, amount: Union[int, float]) -> bool:
        if not isinstance(amount, (int, float)) or amount <= 0 or self.__balance < amount: return False
        self.__balance -= float(amount)
        self.__log("Debit", -amount, f"-{amount} DA")
        return True

    def transfer(self, to_acc: 'Account', amount: Union[int, float]) -> bool:
        if not isinstance(to_acc, Account) or not self.debit(amount): return False
        to_acc.credit(amount)
        self.__transactions[-1]['desc'] = f"Transfer to #{to_acc.get_code()}: -{amount} DA"
        to_acc.__transactions[-1]['desc'] = f"Transfer from #{self.__code}: +{amount} DA"
        return True

    @staticmethod
    def get_total() -> int: return Account.__nbAccounts

def clear(): 
    import os; os.system('cls' if os.name == 'nt' else 'clear')

def find_client(clients: Dict, cin: str) -> Optional[Client]: 
    return clients.get(str(cin))

def find_account(clients: Dict, code: int) -> Optional[Account]:
    for client in clients.values():
        for acc in client.get_accounts():
            if acc.get_code() == code: return acc
    return None

def show_clients_accounts(clients: Dict) -> None:
    print("\n" + "="*60 + "\n  ALL CLIENTS & ACCOUNTS\n" + "="*60)
    if not clients: print("No clients."); return
    for client in clients.values():
        print(f"\n{client.get_name()} (CIN: {client.get_CIN()}, Tel: {client.get_tel() or 'N/A'})")
        accs = client.get_accounts()
        if not accs: print("  └─ No accounts")
        else:
            for acc in accs:
                print(f"  └─ Acc #{acc.get_code()}: {acc.get_balance():.2f} DA ({len(acc.get_transactions())} trans)")

def show_all_transactions(clients: Dict) -> None:
    print("\n" + "="*60 + "\n  ALL TRANSACTIONS\n" + "="*60)
    all_trans = []
    for client in clients.values():
        for acc in client.get_accounts():
            for t in acc.get_transactions():
                all_trans.append({**t, 'acc': acc.get_code(), 'owner': client.get_name()})
    if not all_trans: print("No transactions."); return
    all_trans.sort(key=lambda x: x['time'], reverse=True)
    print(f"\n{'Time':<17} {'Acc':<5} {'Owner':<15} {'Type':<10} {'Amount':>12} {'Balance':>12}")
    print("-"*75)
    for t in all_trans:
        print(f"{t['time']:<17} #{t['acc']:<4} {t['owner']:<15} {t['type']:<10} {t['amount']:>+11.2f} {t['bal']:>12.2f}")

def main():
    clear()
    clients: Dict[str, Client] = {}
    print("="*60 + "\n  BANK MANAGEMENT SYSTEM\n" + "="*60)
    
    while True:
        print("\n" + "-"*60)
        print("MENU: 1)NewClient 2)NewAcc 3)Credit 4)Debit 5)Transfer")
        print("      6)ViewClients 7)ViewTrans 8)AccInfo 9)Stats 0)Exit")
        print("-"*60)
        
        try:
            choice = input("→ ").strip()
            clear()
            
            if choice == "1":
                print("CREATE CLIENT")
                cin, fname, lname, tel = input("CIN: "), input("First: "), input("Last: "), input("Tel(opt): ")
                if find_client(clients, cin): print("❌ CIN exists!"); continue
                clients[cin] = Client(cin, fname, lname, tel)
                print(f"✓ Client {fname} {lname} created!")
            
            elif choice == "2":
                print("CREATE ACCOUNT")
                if not clients: print("❌ No clients!"); continue
                cin = input("Client CIN: ")
                client = find_client(clients, cin)
                if not client: print("❌ Client not found!"); continue
                acc = Account(client)
                print(f"✓ Account #{acc.get_code()} created for {client.get_name()}!")
            
            elif choice == "3":
                print("CREDIT")
                code, amt = int(input("Account: ")), float(input("Amount: "))
                acc = find_account(clients, code)
                if not acc: print("❌ Account not found!"); continue
                print("✓ Success!" if acc.credit(amt) else "❌ Failed!")
            
            elif choice == "4":
                print("DEBIT")
                code, amt = int(input("Account: ")), float(input("Amount: "))
                acc = find_account(clients, code)
                if not acc: print("❌ Account not found!"); continue
                print("✓ Success!" if acc.debit(amt) else "❌ Failed/Insufficient!")
            
            elif choice == "5":
                print("TRANSFER")
                from_code, to_code = int(input("From Acc: ")), int(input("To Acc: "))
                amt = float(input("Amount: "))
                from_acc, to_acc = find_account(clients, from_code), find_account(clients, to_code)
                if not from_acc or not to_acc: print("❌ Account not found!"); continue
                print("✓ Transfer success!" if from_acc.transfer(to_acc, amt) else "❌ Failed!")
            
            elif choice == "6":
                show_clients_accounts(clients)
            
            elif choice == "7":
                show_all_transactions(clients)
            
            elif choice == "8":
                print("ACCOUNT INFO")
                code = int(input("Account: "))
                acc = find_account(clients, code)
                if not acc: print("❌ Not found!"); continue
                print(f"\nAcc #{acc.get_code()} - {acc.get_owner().get_name()}")
                print(f"Balance: {acc.get_balance():.2f} DA | Trans: {len(acc.get_transactions())}")
                if acc.get_transactions():
                    print(f"\n{'Time':<17} {'Type':<10} {'Amount':>12} {'Balance':>12}")
                    print("-"*55)
                    for t in acc.get_transactions():
                        print(f"{t['time']:<17} {t['type']:<10} {t['amount']:>+11.2f} {t['bal']:>12.2f}")
            
            elif choice == "9":
                print("STATISTICS")
                print(f"Total Clients: {len(clients)}")
                print(f"Total Accounts: {Account.get_total()}")
                total_bal = sum(acc.get_balance() for c in clients.values() for acc in c.get_accounts())
                print(f"Total Balance: {total_bal:.2f} DA")
            
            elif choice == "0":
                print("Goodbye!"); break
            
            else:
                print("❌ Invalid choice!")
        
        except (ValueError, TypeError) as e:
            print(f"❌ Error: {e}")
        
        input("\n[Press Enter]")
        clear()

if __name__ == "__main__":
    main()


