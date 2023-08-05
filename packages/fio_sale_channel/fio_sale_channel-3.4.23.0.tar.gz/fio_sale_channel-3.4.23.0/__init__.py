# -*- coding: utf-8 -*-
"""
    __init__.py

"""
from trytond.pool import Pool
from channel import (
    SaleChannel, ReadUser, WriteUser, ChannelException, ChannelOrderState
)
from wizard import (
    ImportDataWizard, ImportDataWizardStart, ImportDataWizardSuccess,
    ExportDataWizard, ExportDataWizardStart, ExportDataWizardSuccess,
    ImportDataWizardProperties, ImportOrderStatesStart, ImportOrderStates,
    ExportPricesStatus, ExportPricesStart, ExportPrices
)
from product import (
    ProductSaleChannelListing, Product, AddProductListing,
    AddProductListingStart
)
from sale import Sale, SaleLine
from user import User
from stock import StockLocation


def register():
    Pool.register(
        SaleChannel,
        ReadUser,
        WriteUser,
        ChannelException,
        ChannelOrderState,
        User,
        Sale,
        SaleLine,
        ProductSaleChannelListing,
        Product,
        ImportDataWizardStart,
        ImportDataWizardSuccess,
        ImportDataWizardProperties,
        ExportDataWizardStart,
        ExportDataWizardSuccess,
        ImportOrderStatesStart,
        ExportPricesStatus,
        ExportPricesStart,
        AddProductListingStart,
        StockLocation,
        module='sale_channel', type_='model'
    )
    Pool.register(
        AddProductListing,
        ImportDataWizard,
        ExportDataWizard,
        ImportOrderStates,
        ExportPrices,
        module='sale_channel', type_='wizard'
    )
