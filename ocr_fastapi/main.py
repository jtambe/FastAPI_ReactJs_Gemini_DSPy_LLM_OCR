import base64

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import dspy
dspy.settings.debug = True
from ocr_dspy.extractor import InvoiceExtractorModule
import logging

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@postgres:5432/mydb")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

load_dotenv()  # Load environment variables from .env
api_key = os.getenv("API_KEY")


class OCRInvoice(Base):
    __tablename__ = "OCR_Invoices"
    id = Column(Integer, primary_key=True, index=True)
    total_net_worth = Column(Float)
    total_vat = Column(Float)
    gross_worth = Column(Float)
    file_name = Column(String)

class InvoiceData(BaseModel):
    total_net_worth: float
    total_vat: float
    gross_worth: float
    file_name: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Move these lines to the global scope, outside any function
# API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
logger.debug("Initializing dspy.LM...")
lm = dspy.LM(
    "gemini/gemini-2.0-flash",
    api_key=api_key,
    # temperature=0.0,
    # api_base=API_BASE_URL
)
dspy.configure(lm=lm)
logger.debug("dspy.LM initialized successfully")

# Similarly, initialize this once at startup
invoice_extractor_module = InvoiceExtractorModule()
logger.debug("Invoice extractor Module initialized successfully")

@app.post("/upload_invoice", response_model=InvoiceData)
def upload_invoice(file: UploadFile = File(...), db: Session = Depends(get_db)):

    try:
        # Ensure the directory exists
        upload_dir = "uploaded_invoices"
        os.makedirs(upload_dir, exist_ok=True)

        # Save the uploaded file in the directory
        file_location = os.path.join(upload_dir, file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        # print(f"api_key: {api_key}")

        # with open(file_location, "rb") as img_file:
        #     logger.debug(f"File {file_location} opened successfully")
        #     base64_data = base64.b64encode(img_file.read()).decode('utf-8')
        #     logger.debug(f"Base64 data length: {len(base64_data)}")
        # image_data_uri = f"data:image/jpg;base64,{base64_data}"


        extracted_data = invoice_extractor_module(file_location)

        logger.debug(f"extracted_data : {extracted_data}")

        invoice = OCRInvoice(
            total_net_worth=extracted_data['total_net_worth'],
            total_vat=extracted_data['total_vat'],
            gross_worth=extracted_data['gross_worth'],
            file_name=file.filename
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)

        # return sample data for testing without DB
        return InvoiceData(**extracted_data, file_name=file.filename)

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

# Create tables if not exist
Base.metadata.create_all(bind=engine)
