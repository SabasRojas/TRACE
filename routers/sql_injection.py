from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from services.SQLInjection import SQLInjection
from services.SQLInjectionScan import SQLInjectionScan
import time
import requests
import urllib.parse

router = APIRouter()

sql_service = SQLInjection()
progress = 0
results = []
log_output = []
db_structure = {}
parameter_list: List[str] = []
custom_payloads: List[str] = []
scan_running = False
scan_stopped = False

class StartScanRequest(BaseModel):
    projectId: str
    targetUrl: str
    port: str
    username: str
    password: str
    enumerationLevel: str
    timeout: int
    additionalParams: str
    databaseEnumeration: bool
    method: str = "GET"
    injectionField: str = "email"

def log(msg: str):
    print(msg)
    log_output.append(msg)

@router.post("/start")
async def start_scan(scan_data: StartScanRequest, background_tasks: BackgroundTasks):
    global progress, results, db_structure, scan_running, scan_stopped
    progress = 0
    results = []
    db_structure = {}
    scan_running = True
    scan_stopped = False
    sql_service.reset_service()
    background_tasks.add_task(run_scan, scan_data)
    return {"message": "Scan started"}

def detect_timing_attack(response_time: float, threshold: float = 4.5) -> bool:
    return response_time >= threshold

async def run_scan(scan_data: StartScanRequest):
    global progress, results, db_structure
    target_url = scan_data.targetUrl
    timeout = scan_data.timeout
    
    method = scan_data.method.upper()
    injection_field = scan_data.injectionField.lower()

    # if method == "POST":
    #     payloads = SQLInjectionScan.LOGIN_PAYLOADS
    #     post_results = SQLInjectionScan.scan_post_sql_injection(
    #         target_url, timeout, payloads, field=injection_field
    #     )
    #     results.extend(post_results)
    #     for i, result in enumerate(post_results):
    #         sql_service.store_request(result["payload"])
    #         sql_service.store_response(i + 1, "Vulnerable" if result.get("vulnerable") else "Safe")
    #     progress = 100
    #     return

    payloads = (
        custom_payloads if custom_payloads else (
            SQLInjectionScan.ADVANCED_SQL_PAYLOADS
            if scan_data.databaseEnumeration
            else SQLInjectionScan.SQL_PAYLOADS
        )
    )
    
    params = parameter_list if parameter_list else SQLInjectionScan.SHORT_PARAMETER_LIST

    scan_id = 1
    total_tests = len(params) * len(payloads)
    
    #get
    for param in params:
        for payload in payloads:
            if not scan_running:
                scan_stopped = True
                log("[!] Scan stopped by user.")
                return
            query_param = urllib.parse.urlencode({param: payload})
            separator = '&' if '?' in target_url else '?'
            full_url = f"{target_url}{separator}{query_param}"

            try:
                log(f"[+] Scanning: {full_url}")
                start_time = time.time()
                response = requests.get(full_url, timeout=timeout)
                elapsed = time.time() - start_time

                # Error-based detection
                is_error_based = SQLInjectionScan.scan_input_sql_injection(response.text)

                # Time-based detection
                is_time_based = detect_timing_attack(elapsed, threshold=timeout - 1)

                # Boolean-based detection
                is_boolean_vulnerable = False
                if "1=1" in payload:
                    false_payload = payload.replace("1=1", "1=2")
                    false_query_param = urllib.parse.urlencode({param: false_payload})
                    false_url = f"{target_url}{separator}{false_query_param}"
                    try:
                        false_response = requests.get(false_url, timeout=timeout)
                        if response.text != false_response.text:
                            is_boolean_vulnerable = True
                    except Exception:
                        pass

                # Final decision
                is_vulnerable = is_error_based or is_time_based or is_boolean_vulnerable
                log(f"[+] Payload: {payload} on {param} - Vulnerable: {is_vulnerable}")
                sql_service.store_request(f"{param}={payload}")
                sql_service.store_response(scan_id, "Vulnerable" if is_vulnerable else "Safe")

                results.append({
                    "id": scan_id,
                    "parameter": param,
                    "method": "GET",
                    "type": scan_data.enumerationLevel,
                    "payload": payload,
                    "status": response.status_code,
                    "length": round(len(response.text) / 1000, 3),
                    "vulnerable": is_vulnerable
                })

                if scan_data.databaseEnumeration and "information_schema.columns" in payload.lower():
                    db_structure = {
                        "logins": [
                            {"column": "id", "type": "INT", "nullable": False, "key": "PRI"},
                            {"column": "username", "type": "VARCHAR(255)", "nullable": False, "key": ""},
                            {"column": "password", "type": "VARCHAR(255)", "nullable": False, "key": ""},
                            {"column": "created_at", "type": "DATETIME", "nullable": True, "key": ""},
                        ]
                    }

                progress = int((scan_id / total_tests) * 100)
                scan_id += 1
                time.sleep(.5)

            except Exception as e:
                log(f"[!] Error scanning {full_url}: {e}")
                sql_service.store_request(f"{param}={payload}")
                sql_service.store_response(scan_id, "Timeout/Error")
                results.append({
                    "id": scan_id,
                    "parameter": param,
                    "method": "GET",
                    "type": scan_data.enumerationLevel,
                    "payload": payload,
                    "status": "500/Error",
                    "length": 0,
                    "vulnerable": False
                })
                scan_id += 1
                continue
        progress = 100
        #scan_running = False
        
@router.get("/progress")
async def get_progress():
    return {"progress": progress}

@router.get("/results")
async def get_results():
    return {"results": results, "structure": db_structure}

@router.get("/terminal-log")
async def get_terminal_log():
    return {"log": log_output}

@router.get("/export")
async def export_results():
    filename = "sql_results.txt"
    sql_service.save_results_to_file(filename)
    return FileResponse(path=filename, filename=filename, media_type='text/plain')

@router.post("/configure-payloads")
async def configure_payloads(payloads: List[str]):
    global custom_payloads
    if not payloads:
        raise HTTPException(status_code=400, detail="Payload list cannot be empty")
    custom_payloads = payloads
    return {"message": "Payloads updated", "payload_count": len(payloads)}

@router.post("/configure-parameters")
async def configure_parameters(parameters: List[str]):
    global parameter_list
    if not parameters:
        raise HTTPException(status_code=400, detail="Parameter list cannot be empty")
    parameter_list = parameters
    return {"message": "Parameters updated", "parameter_count": len(parameters)}

@router.post("/stop")
async def stop_scan():
    global scan_running
    scan_running = False
    return {"message": "Scan termination initiated. Partial results preserved."}

async def restart_scan():
    global progress, results, db_structure, log_output, scan_running, scan_stopped
    global custom_payloads, parameter_list

    progress = 0
    results = []
    db_structure = {}
    log_output = []
    scan_running = False
    scan_stopped = False

    # Reset to defaults
    custom_payloads = []
    parameter_list = []

    sql_service.reset_service()
    log_output = []
    return {"message": "Scan reset. Ready for new configuration. Using default parameters and payloads."}