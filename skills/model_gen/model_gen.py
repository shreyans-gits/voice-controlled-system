import os
import sys
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.append(CURRENT_DIR)

import drive_client

class ModelGenModule:
    def __init__(self):
        self.output_dir = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "data", "outputs"))
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate(self, prompt: str) -> str:
        sanitized_prompt = re.sub(r'[^a-z0-9_]', '', prompt.lower().replace(' ', '_'))
        if not sanitized_prompt:
            sanitized_prompt = "generated_asset"
            
        job_id = sanitized_prompt
        file_format = "obj"
        output_filename = f"{job_id}.{file_format}"
        local_path = os.path.join(self.output_dir, output_filename)
        
        print(f"\n[NOVA Brain] Directing 3D Pipeline for Job ID: {job_id}")
        
        try:
            oauth_config_path = os.path.join(CURRENT_DIR, "two.json")
            service = drive_client.get_drive_service(oauth_path=oauth_config_path)            
            drive_client.upload_job(service, job_id, prompt, file_format)
            
            remote_file_metadata = drive_client.poll_for_result(
                service=service,
                job_id=job_id,
                timeout=300,
                format=file_format
            )
            
            drive_file_id = remote_file_metadata.get('id')
            drive_client.download_file(service, drive_file_id, local_path)
            
            drive_client.delete_file(service, drive_file_id)
            
            return local_path
            
        except TimeoutError as te:
            print(f"[NOVA Brain Error] Shape-E Pipeline Timed out: {te}")
            raise TimeoutError("Model generation timed out. Please check your Google Colab workspace connection.")
        except Exception as e:
            print(f"[NOVA Brain Error] Failed to execute generation sequence: {e}")
            raise e