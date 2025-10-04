import os
from collections import defaultdict
from pathlib import Path
import re
import shutil
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import glob

def normalize_filename(filename):
    """
    Normalize filename by removing common copy indicators.
    Examples: 'file (1).txt', 'file copy.txt', 'file - Copy.txt' -> 'file.txt'
    """
    name_without_ext = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    
    patterns = [
        r'\s*\(\d+\)$',
        r'\s*-?\s*copy\s*\d*$',
        r'\s*-?\s*Copy\s*\d*$',
        r'\s*_copy\s*\d*$',
    ]
    
    normalized = name_without_ext
    for pattern in patterns:
        normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
    
    return normalized.strip() + extension

def find_all_files(folder_path):
    """Find all files and categorize them as duplicates or unique."""
    file_groups = defaultdict(list)
    
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            try:
                file_size = os.path.getsize(filepath)
                normalized_name = normalize_filename(filename)
                key = (normalized_name.lower(), file_size)
                
                file_groups[key].append({
                    'path': filepath,
                    'original_name': filename,
                    'normalized_name': normalized_name,
                    'size': file_size,
                    'relative_path': os.path.relpath(filepath, folder_path)
                })
            except (OSError, FileNotFoundError) as e:
                print(f"Error accessing file {filepath}: {e}")
    
    all_files = []
    for key, files in file_groups.items():
        is_duplicate = len(files) > 1
        duplicate_count = len(files) if is_duplicate else 0
        
        for file_info in files:
            file_info['is_duplicate'] = is_duplicate
            file_info['duplicate_count'] = duplicate_count
            file_info['group_key'] = key
            all_files.append(file_info)
    
    return all_files, file_groups

def format_size(size_bytes):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def print_table_separator(widths):
    """Print a table separator line."""
    print("+" + "+".join("-" * (w + 2) for w in widths) + "+")

def print_table_row(columns, widths):
    """Print a table row with proper padding."""
    row = "|"
    for col, width in zip(columns, widths):
        row += f" {str(col)[:width].ljust(width)} |"
    print(row)

def display_results_table(all_files):
    """Display all files in a table format."""
    if not all_files:
        print("\n✓ No files found in the folder!")
        return
    
    all_files.sort(key=lambda x: (not x['is_duplicate'], x['normalized_name'].lower(), x['path']))
    
    col_widths = [50, 12, 15, 12]
    headers = ["File Path", "Size", "Status", "Duplicates"]
    
    print("\n" + "=" * 95)
    print("📋 FILE DUPLICATE ANALYSIS REPORT")
    print("=" * 95)
    
    print_table_separator(col_widths)
    print_table_row(headers, col_widths)
    print_table_separator(col_widths)
    
    for file_info in all_files:
        status = "🔴 DUPLICATE" if file_info['is_duplicate'] else "✅ UNIQUE"
        dup_info = str(file_info['duplicate_count']) if file_info['is_duplicate'] else "-"
        
        columns = [
            file_info['relative_path'],
            format_size(file_info['size']),
            status,
            dup_info
        ]
        
        print_table_row(columns, col_widths)
    
    print_table_separator(col_widths)

def display_summary(all_files, file_groups):
    """Display summary statistics."""
    try:
        duplicate_files = [f for f in all_files if f['is_duplicate']]
        unique_files = [f for f in all_files if not f['is_duplicate']]
        duplicate_groups = {k: v for k, v in file_groups.items() if len(v) > 1}
        
        total_wasted_space = 0
        duplicate_files_to_remove = 0
        for key, files in duplicate_groups.items():
            size = files[0]['size']
            total_wasted_space += size * (len(files) - 1)
            duplicate_files_to_remove += len(files) - 1
        
        print("\n" + "=" * 95)
        print("📊 SUMMARY STATISTICS")
        print("=" * 95)
        print(f"📄 Total files scanned:              {len(all_files)}")
        print(f"✅ Unique files:                     {len(unique_files)}")
        print(f"🔴 Duplicate files:                  {len(duplicate_files)}")
        print(f"📁 Duplicate groups:                 {len(duplicate_groups)}")
        print(f"🗑️  Files that can be removed:       {duplicate_files_to_remove}")
        print(f"💾 Current wasted space:             {format_size(total_wasted_space)}")
        print(f"💰 Space to be saved if cleaned:    {format_size(total_wasted_space)}")
        print("=" * 95)
        
        return total_wasted_space, duplicate_files_to_remove
    except Exception as e:
        print(f"\n⚠️  Error displaying summary: {e}")
        return 0, 0

def export_to_csv(all_files, folder_path):
    """Export results to CSV file."""
    output_file = "duplicate_files_report.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['File Path', 'File Name', 'Size (Bytes)', 'Size (Readable)', 'Status', 'Duplicate Count', 'Normalized Name'])
        
        for file_info in all_files:
            status = "DUPLICATE" if file_info['is_duplicate'] else "UNIQUE"
            dup_count = file_info['duplicate_count'] if file_info['is_duplicate'] else 0
            
            writer.writerow([
                file_info['relative_path'],
                file_info['original_name'],
                file_info['size'],
                format_size(file_info['size']),
                status,
                dup_count,
                file_info['normalized_name']
            ])
    
    print(f"\n✓ CSV report saved to: {output_file}")

def process_single_file(file_info, backup_folder, folder_path):
    """Process a single duplicate file (move to backup or delete)."""
    result = {
        'success': False,
        'file_info': file_info,
        'error': None,
        'backup_info': None
    }
    
    try:
        if backup_folder:
            relative_path = file_info['relative_path']
            backup_file_path = os.path.join(backup_folder, relative_path)
            backup_file_dir = os.path.dirname(backup_file_path)
            
            os.makedirs(backup_file_dir, exist_ok=True)
            
            shutil.move(file_info['path'], backup_file_path)
            
            result['success'] = True
            result['action'] = 'moved'
            result['backup_info'] = {
                'original_path': file_info['path'],
                'backup_path': backup_file_path,
                'relative_path': relative_path,
                'filename': file_info['original_name'],
                'size': file_info['size'],
                'normalized_name': file_info['normalized_name']
            }
        else:
            os.remove(file_info['path'])
            result['success'] = True
            result['action'] = 'deleted'
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

def remove_duplicates(file_groups, folder_path):
    """Remove duplicate files, keeping only one copy of each."""
    duplicate_groups = {k: v for k, v in file_groups.items() if len(v) > 1}
    
    if not duplicate_groups:
        print("\n✓ No duplicate files to remove!")
        return
    
    print("\n" + "=" * 95)
    print("🗑️  DUPLICATE FILE REMOVAL")
    print("=" * 95)
    print("\n⚠️  WARNING: This will remove duplicate files!")
    print("The first file in each group will be kept, all others will be removed.\n")
    
    total_to_remove = sum(len(files) - 1 for files in duplicate_groups.values())
    total_space = sum(files[0]['size'] * (len(files) - 1) for files in duplicate_groups.values())
    
    print(f"📊 Files to be removed: {total_to_remove}")
    print(f"💾 Space to be freed: {format_size(total_space)}\n")
    
    print("Preview of files to be kept and removed:\n")
    
    for group_num, ((normalized_name, size), files) in enumerate(duplicate_groups.items(), 1):
        print(f"📁 Group {group_num}: {normalized_name} ({format_size(size)})")
        print(f"   ✅ KEEP:   {files[0]['relative_path']}")
        for file_info in files[1:]:
            print(f"   ❌ REMOVE: {file_info['relative_path']}")
        print()
    
    print("=" * 95)
    proceed = input("\n⚠️  Do you want to proceed with removing these files? (yes/no): ").strip().lower()
    
    if proceed not in ['yes', 'y']:
        print("\n❌ Operation cancelled. No files were removed.")
        return
    
    backup_choice = input("\n💾 Do you want to create a backup before removing? (yes/no): ").strip().lower()
    
    backup_folder = None
    if backup_choice in ['yes', 'y']:
        while True:
            backup_folder = input("\n📁 Enter the backup folder path: ").strip().strip('"').strip("'")
            
            if not os.path.exists(backup_folder):
                create_folder = input(f"\n⚠️  Folder '{backup_folder}' doesn't exist. Create it? (yes/no): ").strip().lower()
                if create_folder in ['yes', 'y']:
                    try:
                        os.makedirs(backup_folder, exist_ok=True)
                        print(f"✓ Created backup folder: {backup_folder}")
                        break
                    except Exception as e:
                        print(f"❌ Error creating folder: {e}")
                        continue
                else:
                    continue
            elif not os.path.isdir(backup_folder):
                print(f"❌ '{backup_folder}' is not a directory. Please enter a valid folder path.")
                continue
            else:
                break
    
    print("\n" + "=" * 95)
    if backup_folder:
        print(f"📦 Backup will be created at: {backup_folder}")
        print("🔄 Files will be MOVED to backup, then removed from original location")
    else:
        print("⚠️  No backup will be created - files will be PERMANENTLY DELETED")
    
    final_confirm = input("\n🚨 Type 'CONFIRM' to proceed with bulk operation: ").strip()
    
    if final_confirm != 'CONFIRM':
        print("\n❌ Operation cancelled. No files were removed.")
        return
    
    # Collect all files to be processed
    files_to_process = []
    for (normalized_name, size), files in duplicate_groups.items():
        for file_info in files[1:]:  # Skip first file (keep it)
            files_to_process.append(file_info)
    
    # Statistics tracking
    processed_count = 0
    moved_count = 0
    deleted_count = 0
    freed_space = 0
    errors = []
    backed_up_files = []
    
    # Thread-safe lock for printing and updating statistics
    print_lock = threading.Lock()
    
    print(f"\n🔄 Processing {len(files_to_process)} duplicate files using parallel threads...\n")
    
    # Use ThreadPoolExecutor for parallel processing
    max_workers = min(10, len(files_to_process))  # Use up to 10 threads
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all file processing tasks
        future_to_file = {
            executor.submit(process_single_file, file_info, backup_folder, folder_path): file_info 
            for file_info in files_to_process
        }
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_file):
            result = future.result()
            
            with print_lock:
                if result['success']:
                    processed_count += 1
                    freed_space += result['file_info']['size']
                    
                    if result['action'] == 'moved':
                        moved_count += 1
                        backed_up_files.append(result['backup_info'])
                        print(f"✓ [{processed_count}/{len(files_to_process)}] Moved to backup: {result['file_info']['relative_path']}")
                    else:
                        deleted_count += 1
                        print(f"✓ [{processed_count}/{len(files_to_process)}] Deleted: {result['file_info']['relative_path']}")
                else:
                    error_msg = f"Failed to process {result['file_info']['relative_path']}: {result['error']}"
                    errors.append(error_msg)
                    print(f"✗ {error_msg}")
    
    # Create backup CSV if backup was created
    if backup_folder and backed_up_files:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"backup_report_{timestamp}.csv"
            csv_path = os.path.join(backup_folder, csv_filename)
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Original Path', 'Backup Path', 'Relative Path', 'Filename', 'Size (Bytes)', 'Size (Readable)', 'Normalized Name', 'Backup Date'])
                
                backup_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for file_info in backed_up_files:
                    writer.writerow([
                        file_info['original_path'],
                        file_info['backup_path'],
                        file_info['relative_path'],
                        file_info['filename'],
                        file_info['size'],
                        format_size(file_info['size']),
                        file_info['normalized_name'],
                        backup_date
                    ])
            
            print(f"\n✓ Backup CSV report created: {csv_path}")
        except Exception as e:
            print(f"\n⚠️  Warning: Could not create backup CSV: {e}")
    
    # Display results
    print("\n" + "=" * 95)
    print("📊 OPERATION SUMMARY")
    print("=" * 95)
    print(f"✅ Files successfully processed:  {processed_count}")
    
    if backup_folder:
        print(f"📦 Files moved to backup:         {moved_count}")
        print(f"📁 Backup location:               {backup_folder}")
    else:
        print(f"🗑️  Files permanently deleted:     {deleted_count}")
    
    print(f"💾 Space freed from source:       {format_size(freed_space)}")
    
    if errors:
        print(f"❌ Errors encountered:            {len(errors)}")
        print("\nErrors:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("🎉 All duplicate files processed successfully!")
    
    print("=" * 95)

def main():
    """Main function to run the duplicate finder."""
    try:
        print("=" * 95)
        print("🔎 DUPLICATE FILE FINDER")
        print("=" * 95)
        
        folder_path = input("\nEnter the folder path to scan: ").strip()
        folder_path = folder_path.strip('"').strip("'")
        
        if not os.path.exists(folder_path):
            print(f"\n❌ Error: Folder '{folder_path}' does not exist!")
            input("\nPress Enter to exit...")
            return
        
        if not os.path.isdir(folder_path):
            print(f"\n❌ Error: '{folder_path}' is not a folder!")
            input("\nPress Enter to exit...")
            return
        
        print(f"\n🔍 Scanning folder: {folder_path}")
        print("⏳ Please wait...\n")
        
        all_files, file_groups = find_all_files(folder_path)
        
        if not all_files:
            print("\n⚠️  No files found in the specified folder!")
            input("\nPress Enter to exit...")
            return
        
        print(f"\n✓ Scan complete! Found {len(all_files)} files.")
        
        display_results_table(all_files)
        
        duplicate_groups = {k: v for k, v in file_groups.items() if len(v) > 1}
        
        print(f"\nGenerating summary...")
        space_to_save, files_to_remove = display_summary(all_files, file_groups)
        
        if duplicate_groups:
            print("\n" + "=" * 95)
            print("🔍 DUPLICATE GROUPS DETAIL")
            print("=" * 95)
            
            group_num = 1
            for (normalized_name, size), files in duplicate_groups.items():
                print(f"\n📁 Group {group_num}: {normalized_name}")
                print(f"   Size: {format_size(size)} | Count: {len(files)} files | Wasted: {format_size(size * (len(files) - 1))}")
                for file_info in files:
                    print(f"   • {file_info['relative_path']}")
                group_num += 1
        
        print("\n" + "=" * 95)
        export = input("\nWould you like to export results to CSV? (yes/no): ").strip().lower()
        if export in ['yes', 'y']:
            export_to_csv(all_files, folder_path)
        
        if duplicate_groups:
            print("\n" + "=" * 95)
            remove = input("\nWould you like to remove duplicate files? (yes/no): ").strip().lower()
            if remove in ['yes', 'y']:
                remove_duplicates(file_groups, folder_path)
            else:
                print("\n✓ No files were removed. Operation completed.")
        else:
            print("\n✓ No duplicate files found. Nothing to remove.")
        
        print("\n" + "=" * 95)
        print("🎉 Script completed successfully!")
        print("=" * 95)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
