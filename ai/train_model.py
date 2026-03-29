"""
Обучение модели прогноза % снижения цены тендера.
LightGBM Regressor — быстрый, точный, не требует GPU.
"""

import os
import csv
import json
import pickle
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(DATA_DIR, 'training_data.csv')
MODEL_PATH = os.path.join(DATA_DIR, 'model.pkl')
META_PATH = os.path.join(DATA_DIR, 'model_meta.json')


def load_data():
    """Загрузить данные из CSV"""
    rows = []
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    logger.info(f"Загружено {len(rows)} записей")
    return rows


def prepare_features(rows):
    """Подготовка фичей для модели"""
    # Собираем уникальные категории и типы процедур
    categories = sorted(set(r['category'] for r in rows))
    proc_types = sorted(set(r['proc_type'] for r in rows))
    
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    proc_to_idx = {p: i for i, p in enumerate(proc_types)}
    
    X = []
    y = []
    
    for row in rows:
        initial_price = float(row['initial_price'])
        drop_pct = float(row['drop_pct'])
        
        features = [
            cat_to_idx[row['category']],          # категория (encoded)
            np.log1p(initial_price),                # лог цены (нормализация)
            initial_price,                          # цена как есть
            proc_to_idx[row['proc_type']],          # тип процедуры
            1 if initial_price > 10_000_000 else 0, # крупная закупка
            1 if initial_price < 100_000 else 0,    # мелкая закупка
        ]
        
        X.append(features)
        y.append(drop_pct)
    
    return np.array(X), np.array(y), {
        'categories': categories,
        'cat_to_idx': cat_to_idx,
        'proc_types': proc_types,
        'proc_to_idx': proc_to_idx,
        'feature_names': ['category_idx', 'log_price', 'price', 'proc_type_idx', 'is_large', 'is_small'],
    }


def train():
    """Обучение модели"""
    try:
        import lightgbm as lgb
        use_lgb = True
        logger.info("Используем LightGBM")
    except ImportError:
        from sklearn.ensemble import GradientBoostingRegressor
        use_lgb = False
        logger.info("LightGBM не установлен, используем sklearn GradientBoosting")
    
    rows = load_data()
    X, y, meta = prepare_features(rows)
    
    # Split
    n = len(X)
    idx = np.random.RandomState(42).permutation(n)
    split = int(n * 0.8)
    train_idx, test_idx = idx[:split], idx[split:]
    
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    if use_lgb:
        model = lgb.LGBMRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            num_leaves=31,
            random_state=42,
            verbose=-1,
        )
    else:
        model = GradientBoostingRegressor(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
        )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = np.mean(np.abs(y_test - y_pred))
    rmse = np.sqrt(np.mean((y_test - y_pred) ** 2))
    
    logger.info(f"MAE: {mae:.2f}%")
    logger.info(f"RMSE: {rmse:.2f}%")
    logger.info(f"Средний реальный drop: {np.mean(y_test):.2f}%")
    logger.info(f"Средний предсказанный: {np.mean(y_pred):.2f}%")
    
    # Средние по категориям для fallback
    category_means = {}
    for row in rows:
        cat = row['category']
        if cat not in category_means:
            category_means[cat] = []
        category_means[cat].append(float(row['drop_pct']))
    
    category_averages = {cat: round(np.mean(vals), 1) for cat, vals in category_means.items()}
    
    # Save
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Модель сохранена: {MODEL_PATH}")
    
    meta['mae'] = round(mae, 2)
    meta['rmse'] = round(rmse, 2)
    meta['n_train'] = len(X_train)
    meta['n_test'] = len(X_test)
    meta['category_averages'] = category_averages
    meta['trained_at'] = str(np.datetime64('now'))
    
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    logger.info(f"Метаданные сохранены: {META_PATH}")
    
    return model, meta


if __name__ == '__main__':
    train()
