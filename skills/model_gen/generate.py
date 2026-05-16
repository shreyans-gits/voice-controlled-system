import argparse
import os
import uuid
import drive_client

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to send 3D generation requests from your laptop to Google Colab via Google Drive."
    )

    parser.add_argument(
        "prompt", 
        type=str, 
        help="The text prompt describing the 3D asset you want to generate."
    )

    parser.add_argument(
        "--format", 
        type=str, 
        default="obj", 
        choices=["obj", "glb"], 
        help="The output file format (default: obj)."
    )

    parser.add_argument(
        "--timeout", 
        type=int, 
        default=300, 
        help="How long to wait for the generation in seconds (default: 300)."
    )
    
    args = parser.parse_args()
    job_id = str(uuid.uuid4())[:8]
    
    output_dir = "outputs"
    output_filename = f"{job_id}.{args.format}"
    local_path = os.path.join(output_dir, output_filename)
    
    os.makedirs(output_dir, exist_ok=True)

    print(f"Initializing Job ID: {job_id}")
    print(f"Prompt: \"{args.prompt}\"")
    print("-" * 50)

    try:
        print("[Laptop] Authenticating with Google Drive...")
        service = drive_client.get_drive_service()        
        drive_client.upload_job(service, job_id, args.prompt, args.format)

        remote_file_metadata = drive_client.poll_for_result(
            service=service, 
            job_id=job_id, 
            timeout=args.timeout,
            format = args.format
        )
        
        drive_file_id = remote_file_metadata.get('id')        
        drive_client.download_file(service, drive_file_id, local_path)        
        drive_client.delete_file(service, drive_file_id)        
        print("-" * 50)
        print(f"✓ Done. File saved to: {local_path}")

    except TimeoutError as te:
        print(f"\n[Error] Generation timed out: {te}")
        print("-> Verification Step: Is the Colab notebook active, connected, and watching the drive?")
    except Exception as e:
        print(f"\n[Error] Unexpected error occurred: {e}")

if __name__ == "__main__":
    main()