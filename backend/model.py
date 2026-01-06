from pydantic import BaseModel

class WorkerModel(BaseModel):
    name: str
    role: int  # 0: MANUFACTURER, 1: DISTRIBUTOR, 2: TRANSPORTER
    walletAddress: str  # New: Ethereum address of the worker

class ProductModel(BaseModel):
    name: str
    description: str
    minTemp: int
    maxTemp: int
    minHumidity: int
    maxHumidity: int
    quantity: int
    mfgDate: str

class StatusModel(BaseModel):
    productId: int
    location: str
    temperature: int
    humidity: int
    quantity: int

