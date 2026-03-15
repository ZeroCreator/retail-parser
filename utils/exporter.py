from loguru import logger
import pandas as pd
from pathlib import Path
from models.product import Product
from config import Config
from datetime import datetime


class DataExporter:
    """Экспорт данных в файлы"""
    
    def __init__(self):
        self.output_dir = Path(Config.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_products(self, products: list[Product], store_name: str):
        """Экспорт товаров в файл"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if Config.OUTPUT_FORMAT == 'excel':
            self._export_excel(products, store_name, timestamp)
        else:
            self._export_csv(products, store_name, timestamp)
        
        logger.info(f"Экспортировано {len(products)} товаров для {store_name}")
    
    def _export_csv(self, products: list[Product], store_name: str, timestamp: str):
        """Экспорт в CSV"""
        data = [p.to_dict() for p in products]
        df = pd.DataFrame(data)
        
        filename = self.output_dir / f"{store_name}_{timestamp}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    def _export_excel(self, products: list[Product], store_name: str, timestamp: str):
        """Экспорт в Excel"""
        data = [p.to_dict() for p in products]
        df = pd.DataFrame(data)
        
        filename = self.output_dir / f"{store_name}_{timestamp}.xlsx"
        df.to_excel(filename, index=False, engine='openpyxl')
    
    def export_all(self, all_products: dict[str, list[Product]]):
        """Экспорт всех товаров в один файл"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        all_data = []
        for store_name, products in all_products.items():
            for product in products:
                product.store = store_name
                all_data.append(product.to_dict())
        
        df = pd.DataFrame(all_data)
        
        if Config.OUTPUT_FORMAT == 'excel':
            filename = self.output_dir / f"all_stores_{timestamp}.xlsx"
            df.to_excel(filename, index=False, engine='openpyxl')
        else:
            filename = self.output_dir / f"all_stores_{timestamp}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        logger.info(f"Экспортировано {len(all_data)} товаров из {len(all_products)} магазинов")
