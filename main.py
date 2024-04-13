import numpy as np
import matplotlib.pyplot as plt

class StorageProvider:
    def __init__(self, capacity_gb):
        self.capacity_gb = capacity_gb
        self.active_contracts = []
        self.base_stor_power = 0
        self.adjusted_stor_power = 0
        self.history = []

    def add_contract(self, size_gb, length_days, initial_collateral):
        contract = {
            'size_gb': size_gb,
            'length_days': length_days,
            'initial_collateral': initial_collateral,
            'completed_days': 0,
            'failed_proofs': 0,
            'slashed_collateral': 0,
            'active': True
        }
        self.active_contracts.append(contract)
        self.update_stor_power()

    def update_stor_power(self):
        self.base_stor_power = sum(
            c['size_gb'] * c['length_days'] * (c['initial_collateral'] - c['slashed_collateral'])
            for c in self.active_contracts if c['active']
        )
        proofs_required = sum(min(30, c['length_days'] - c['completed_days']) for c in self.active_contracts if c['active'])
        failed_proofs = sum(c['failed_proofs'] for c in self.active_contracts if c['active'])
        self.adjusted_stor_power = self.base_stor_power * ((proofs_required - failed_proofs) ** 1.5)

    def simulate_day(self):
        for contract in self.active_contracts:
            if contract['active']:
                contract['completed_days'] += 1
                # Simulating a failed proof randomly
                if np.random.random() < 0.05:  # 5% chance of failing a proof
                    contract['failed_proofs'] += 1
                    contract['slashed_collateral'] += contract['initial_collateral'] * 0.1  # 10% slashing
                # Check if contract is completed
                if contract['completed_days'] >= contract['length_days']:
                    contract['active'] = False
        self.update_stor_power()
        self.history.append(self.adjusted_stor_power)

# Simulation Parameters
days = 365  # Number of days to simulate
small_sp = StorageProvider(50)  # 50 GiB
medium_sp = StorageProvider(200)  # 200 GiB
large_sp = StorageProvider(1000)  # 1 TiB

# Add initial contracts
small_sp.add_contract(5, 90, 1000)
medium_sp.add_contract(20, 90, 4000)
large_sp.add_contract(100, 90, 20000)

# Simulation Loop
for day in range(days):
    small_sp.simulate_day()
    medium_sp.simulate_day()
    large_sp.simulate_day()

    # Add new contracts every 30 days
    if day % 30 == 0:
        small_sp.add_contract(5, 90, 1000)
        medium_sp.add_contract(20, 90, 4000)
        large_sp.add_contract(100, 90, 20000)

# Plotting the results
plt.figure(figsize=(10, 6))
plt.plot(small_sp.history, label='Small SP (50GiB)')
plt.plot(medium_sp.history, label='Medium SP (200GiB)')
plt.plot(large_sp.history, label='Large SP (1TiB)')
plt.xlabel('Days')
plt.ylabel('Adjusted StorPower')
plt.title('Adjusted StorPower over Time')
plt.legend()
plt.show()