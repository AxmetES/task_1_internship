import logging

from db.models import Product, Category
from db.engine import Session


def get_or_create_category(category: Category):
    try:
        with Session() as session:
            category_obj = session.query(Category).filter_by(catalog_name=category.catalog_name).first()
            if category_obj:
                return category_obj
            else:
                new_category = Category(
                    catalog_name=category.catalog_name,
                    catalog_rus=category.catalog_rus
                )
                session.add(new_category)
                session.commit()
                new_category = session.query(Category).filter_by(catalog_name=category.catalog_name).first()
                return new_category
    except Exception as e:
        logging.exception(e)


def bulk_insert_products(products_data: list):
    try:
        with Session() as session:
            products_instances = [Product(**data) for data in products_data]
            session.bulk_save_objects(products_instances)
            session.commit()
    except Exception as e:
        logging.exception(e)

