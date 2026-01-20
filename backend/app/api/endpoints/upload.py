from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.api.deps import require_hospital_user
from app.models.user import User
from app.schemas.stock import StockUploadResponse
from app.services.csv_processor import CSVProcessor

router = APIRouter(prefix="/api/hospital", tags=["data upload"])


@router.post("/upload-stock", response_model=StockUploadResponse)
async def upload_stock(
    file: UploadFile = File(...),
    current_user: User = Depends(require_hospital_user),
    db: Session = Depends(get_db)
):
    """
    Upload current stock data via CSV file (Hospital users only).
    
    **Authentication:** Requires hospital_admin or hospital_staff role
    
    **CSV Format:**
    ```
    medicine_id,medicine_name,medicine_quantity,medicine_expiry
    MED001,Paracetamol 500mg,5000,2025-12-31
    ```
    
    **Returns:**
    - `message`: Success/error message
    - `records_processed`: Total rows processed
    - `records_inserted`: New records added
    - `records_updated`: Existing records updated
    - `errors`: List of errors (if any)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Derive hospital_id from organization_id (for hospital users)
    hospital_id = current_user.organization_id
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Process CSV
    result = CSVProcessor.process_stock_csv(
        file_content,
        hospital_id,
        db
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return StockUploadResponse(
        message=result["message"],
        records_processed=result["records_processed"],
        records_inserted=result["records_inserted"],
        records_updated=result["records_updated"],
        errors=result["errors"]
    )


@router.post("/upload-usage", response_model=StockUploadResponse)
async def upload_usage(
    file: UploadFile = File(...),
    current_user: User = Depends(require_hospital_user),
    db: Session = Depends(get_db)
):
    """
    Upload historical usage data via CSV file (Hospital users only).
    
    **Authentication:** Requires hospital_admin or hospital_staff role
    
    **CSV Format:**
    ```
    usage_date,medicine_id,medicine_name,quantity_consumed,department
    2024-01-15,MED001,Paracetamol 500mg,350,Outpatient
    ```
    
    **Returns:**
    - `message`: Success/error message
    - `records_processed`: Total rows processed
    - `records_inserted`: New records added
    - `date_range`: Start and end dates of data
    - `errors`: List of errors (if any)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Derive hospital_id from organization_id (for hospital users)
    hospital_id = current_user.organization_id
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Process CSV
    result = CSVProcessor.process_usage_csv(
        file_content,
        hospital_id,
        db
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return StockUploadResponse(
        message=result["message"],
        records_processed=result["records_processed"],
        records_inserted=result["records_inserted"],
        records_updated=0,
        errors=result["errors"]
    )
