import os

def divide_file_into_chunks(filename, output_dir='chunks', chunk_size=32768):
    """
    Divide a file into chunks and save each chunk as a separate file.
    
    Args:
        filename (str): Path to the source file to be divided.
        output_dir (str): Directory where chunk files will be saved.
        chunk_size (int): Size of each chunk in bytes.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Counter for chunk filenames
    chunk_number = 0
    
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break  # End of file reached
            chunk_filename = os.path.join(output_dir, f'{os.path.basename(filename)}_chunk_{chunk_number}')
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_file.write(chunk)
            chunk_number += 1

    print(f'File divided into {chunk_number} chunks and saved in {output_dir}.')
    return chunk_number

# Example usage
PATH=os.getcwd()
print(PATH)

if __name__ == "__main__":
    # source_file = PATH + "\test1.txt"  # Replace with the path to the source file
    source_file = os.path.join(PATH, "test1.txt")
    chunks_output_dir = "chunks_to_send"  # The directory to save the chunks; adjust as needed
    divide_file_into_chunks(source_file, chunks_output_dir)