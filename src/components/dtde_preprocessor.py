import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

class DTDEPreprocessor(BaseEstimator, TransformerMixin):
    """
    This class handles all feature engineering for the DTDE model.
    It ensures that the data for prediction is identical in structure
    to the data used for training.
    """
    def __init__(self):
        self.columns = []

    def fit(self, df, y=None):
        # 1. Engineer time-based features
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['hour'] = df_copy['timestamp'].dt.hour
        df_copy['day_of_week'] = df_copy['timestamp'].dt.dayofweek

        # 2. One-hot encode categorical features
        features_to_encode = ['user_id', 'action', 'status', 'source_ip']
        df_encoded = pd.get_dummies(df_copy, columns=features_to_encode, dtype=int)

        # 3. Define and store the final feature set
        features = df_encoded.drop(columns=['log_id', 'timestamp', 'key_id', 'user_agent'])
        self.columns = features.columns.tolist()
        return self

    def transform(self, df, y=None):
        # 1. Engineer features on the new data
        df_copy = df.copy()
        df_copy['timestamp'] = pd.to_datetime(df_copy['timestamp'])
        df_copy['hour'] = df_copy['timestamp'].dt.hour
        df_copy['day_of_week'] = df_copy['timestamp'].dt.dayofweek
        
        features_to_encode = ['user_id', 'action', 'status', 'source_ip']
        df_encoded = pd.get_dummies(df_copy, columns=features_to_encode, dtype=int)
        
        # 2. Reindex to match the columns learned during 'fit'
        # This guarantees the structure is identical.
        final_df = df_encoded.reindex(columns=self.columns, fill_value=0)
        
        return final_df[self.columns]