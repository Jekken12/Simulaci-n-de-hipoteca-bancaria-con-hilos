import threading
from threading import current_thread
import time
import random
import datetime

def log(msg):
    now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    tid = current_thread().name
    print(f"[{now}][{tid}] {msg}")

class Bank:
    def __init__(self, total_funds):
        self.total_funds = total_funds
        self.lock = threading.Lock()

    def request_loan(self, client_id, amount):
        with self.lock:
            if amount <= self.total_funds:
                log(f"Aprobado préstamo de ${amount} para Cliente-{client_id}. Fondos antes: ${self.total_funds}")
                self.total_funds -= amount
                log(f"Fondos restantes: ${self.total_funds}")
                return True
            else:
                log(f"Rechazado préstamo de ${amount} para Cliente-{client_id}. Fondos insuficientes (${self.total_funds}).")
                return False

    def receive_payment(self, client_id, amount):
        with self.lock:
            log(f"Cliente-{client_id} paga ${amount}. Fondos antes: ${self.total_funds}")
            self.total_funds += amount
            log(f"Fondos ahora: ${self.total_funds}")

class ClientThread(threading.Thread):
    def __init__(self, bank, client_id, loan_amount, repayment_amount, delay):
        super().__init__(name=f"Cliente-{client_id}")
        self.bank = bank
        self.client_id = client_id
        self.loan_amount = loan_amount
        self.repayment_amount = repayment_amount
        self.delay = delay

    def run(self):
        if self.bank.request_loan(self.client_id, self.loan_amount):
            time.sleep(self.delay)
            self.bank.receive_payment(self.client_id, self.repayment_amount)

def run_concurrent(initial_funds, num_clients):
    bank = Bank(initial_funds)
    clients = []
    for i in range(1, num_clients+1):
        loan = random.randint(5_000, 20_000)
        repayment = int(loan * 1.05)
        delay = random.uniform(0.5, 2.0)
        t = ClientThread(bank, i, loan, repayment, delay)
        clients.append(t)

    start = time.perf_counter()
    for t in clients:
        t.start()
    for t in clients:
        t.join()
    duration = time.perf_counter() - start

    log(f"[Concurrente] Fondo final: ${bank.total_funds} en {duration:.4f} s")
    return bank.total_funds, duration

def run_sequential(initial_funds, num_clients):
    bank = Bank(initial_funds)
    start = time.perf_counter()
    for i in range(1, num_clients+1):
        loan = random.randint(5_000, 20_000)
        repayment = int(loan * 1.05)
        # Procesar préstamo
        if bank.request_loan(i, loan):
            # Simulamos delay de forma síncrona
            time.sleep(random.uniform(0.5, 2.0))
            bank.receive_payment(i, repayment)
    duration = time.perf_counter() - start

    log(f"[Secuencial] Fondo final: ${bank.total_funds} en {duration:.4f} s")
    return bank.total_funds, duration

def main():
    initial_funds = 100_000
    num_clients = 10

    print("=== Ejecución Concurrente ===")
    conc_funds, conc_time = run_concurrent(initial_funds, num_clients)

    print("\n=== Ejecución Secuencial ===")
    seq_funds, seq_time = run_sequential(initial_funds, num_clients)

    print("\n=== Comparativa ===")
    print(f"- Concurrente: Fondo final ${conc_funds}, tiempo {conc_time:.4f} s")
    print(f"- Secuencial : Fondo final ${seq_funds}, tiempo {seq_time:.4f} s")

if __name__ == "__main__":
    main()
