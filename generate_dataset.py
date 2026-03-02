import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Number of samples
n_samples = 4465

# Selected features (23 attributes)
features = [
    'access_all_downloads', 'access_cache_filesystem', 'access_fine_location',
    'access_network_state', 'access_service', 'access_shared_data',
    'access_superuser', 'access_wifi_state', 'camera', 'change_configuration',
    'delete_cache_files', 'read_attachment', 'read_contacts', 'read_data',
    'read_external_storage', 'read_gmail', 'read_history_bookmarks',
    'read_messages', 'read_phone_state', 'read_settings', 'read_sms',
    'receive_boot_completed', 'receive_sms'
]

# Create dataset
data = {}

# Generate binary features (0 or 1)
for feature in features:
    # Different probabilities for different features to make it realistic
    if 'read' in feature or 'access' in feature:
        # More common permissions
        prob = np.random.uniform(0.3, 0.7)
    elif 'receive' in feature:
        # Less common
        prob = np.random.uniform(0.2, 0.5)
    else:
        # Moderate
        prob = np.random.uniform(0.25, 0.6)
    
    data[feature] = np.random.binomial(1, prob, n_samples)

# Create DataFrame
df = pd.DataFrame(data)

# Generate target variable (class)
# 70% malware, 30% benign
n_malware = int(n_samples * 0.7)
n_benign = n_samples - n_malware

# Create class labels
class_labels = ['malware'] * n_malware + ['benign'] * n_benign
np.random.shuffle(class_labels)
df['class'] = class_labels

# Add some correlation patterns for malware
# Malware often has multiple suspicious permissions
malware_indices = df[df['class'] == 'malware'].index

# Increase certain permission combinations for malware
for idx in malware_indices:
    if np.random.random() > 0.5:
        # Malware often reads SMS and contacts
        df.loc[idx, 'read_sms'] = 1
        df.loc[idx, 'read_contacts'] = 1
    
    if np.random.random() > 0.6:
        # Malware often accesses network and location
        df.loc[idx, 'access_network_state'] = 1
        df.loc[idx, 'access_fine_location'] = 1
    
    if np.random.random() > 0.7:
        # Some malware tries to access superuser
        df.loc[idx, 'access_superuser'] = 1
    
    if np.random.random() > 0.5:
        # Malware often receives boot completed to start automatically
        df.loc[idx, 'receive_boot_completed'] = 1

# Save to CSV
df.to_csv('upload.csv', index=False)

print(f"Dataset created successfully!")
print(f"Total samples: {n_samples}")
print(f"Features: {len(features)}")
print(f"Malware samples: {(df['class'] == 'malware').sum()}")
print(f"Benign samples: {(df['class'] == 'benign').sum()}")
print(f"\nDataset saved as 'upload.csv'")
print(f"\nFirst few rows:")
print(df.head())
print(f"\nClass distribution:")
print(df['class'].value_counts())
